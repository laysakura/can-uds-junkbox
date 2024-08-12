from typing import Optional
import isotp

from can_uds.comm import is_positive_resp, send_recv
from can_uds.util import p16, p32, p8


def start_diag_session(sock: isotp.socket, sub_func: int):
    """
    0x10 Diagnostic Session Control

    sub_func:
        0x01: Default Session
        0x02: Programming Session
        0x03: Extended Session
        0x04: Safety System Diagnostic Session
    """
    resp = send_recv(sock, bytes([0x10, sub_func]))
    assert is_positive_resp(resp, 0x10), "Start Diagnostic Session failed"


def reset_ecu(sock: isotp.socket, sub_func: int = 0x01):
    """
    0x11 ECU Reset

    sub_func:
        0x01: Hard Reset
        0x02: Key Off On Reset
        0x03: Soft Reset
    """
    resp = send_recv(sock, bytes([0x11, sub_func]))
    assert is_positive_resp(resp, 0x11), "Reset failed"


def read_memory_by_id(sock: isotp.socket, id_: int) -> Optional[bytes]:
    """
    0x22 Read Data By Identifier

    Returns:
        データが取得できる場合、そのデータ。
        データが取得できない場合、None。
    """
    resp = send_recv(sock, bytes([0x22]) + p16(id_))
    if is_positive_resp(resp, 0x22):
        return resp[3:]
    else:
        return None


def read_memory_by_addr(
    sock: isotp.socket, start_addr: int, length: int
) -> list[tuple[int, bytes]]:
    """
    0x23 Read Memory By Address

    Returns: [(addr, data), ...]
        addr: 開始アドレス
        data: 開始アドレスから読み取ったデータチャンク
    指定されたアドレス範囲からの読み取りが全て拒否された場合、返り値は [] となる。
    """
    addr, len_, step = start_addr, length, min(length, 0x800)
    ret = []
    # step バイトずつ読む。
    while step > 0:
        resp = send_recv(sock, bytes([0x23, 0x24]) + p32(addr) + p16(step))
        if is_positive_resp(resp, 0x23):
            ret.append((addr, resp[1:]))
            addr += step
            len_ -= step
            step = min(step, len_)
        else:
            # step が大きいと拒否されることがあるので、半分ずつ小さくする。
            step //= 2

    return ret


class SecurityAccess:
    """
    0x27 Security Access
    """

    def __init__(self, sock: isotp.socket, level: int):
        """
        level:
            0x01: Seed Request (Level1)
            0x03: Seed Request (Level3)
            0x05: Seed Request (Level5)
        """
        assert level in (0x01, 0x03, 0x05), "Invalid Security Access Level"
        self.sock = sock
        self.level = level

    def request_seed(self) -> bytes:
        resp = send_recv(self.sock, bytes([0x27, self.level]))
        assert is_positive_resp(resp, 0x27), "Request Seed failed"
        return resp[2:]

    def send_key(self, key: bytes) -> bool:
        resp = send_recv(self.sock, bytes([0x27, self.level + 1]) + key)
        return is_positive_resp(resp, 0x27)


class RoutineControl:
    """
    0x31 Routine Control
    """

    def __init__(self, sock: isotp.socket, routine_id: int):
        assert 0 <= routine_id <= 0xFFFF, "Invalid Routine ID"
        self.sock = sock
        self.routine_id = routine_id

    def call_routine(self, explicit_stop: bool = False) -> Optional[bytes]:
        """
        Returns: Routine results if the routine is called successfully.
        """
        if self._start_routine():
            res = self._request_routine_results()
            if explicit_stop:
                assert self._stop_routine(), "Stop Routine failed"
            return res
        else:
            return None

    def _start_routine(self) -> bool:
        """
        Returns: True if the routine is started successfully.
        """
        resp = send_recv(self.sock, bytes([0x31, 0x01]) + p16(self.routine_id))
        return is_positive_resp(resp, 0x31)

    def _stop_routine(self) -> bool:
        """
        Returns: True if the routine is stopped successfully.
        """
        resp = send_recv(self.sock, bytes([0x31, 0x02]) + p16(self.routine_id))
        return is_positive_resp(resp, 0x31)

    def _request_routine_results(self) -> Optional[bytes]:
        resp = send_recv(self.sock, bytes([0x31, 0x03]) + p16(self.routine_id))
        if is_positive_resp(resp, 0x31):
            return resp[4:]
        else:
            return None


def request_download(sock: isotp.socket, addr: int, length: int) -> int:
    """
    0x34 Request Download

    Returns: maxNumberOfBlockLength
      (TransferData で1回に送信できる最大データ長)
    """
    data_format = 0x00  # no copmression, no encryption
    addr_length_format = 0x44  # 32-bit address and length
    resp = send_recv(
        sock, bytes([0x34, data_format, addr_length_format]) + p32(addr) + p32(length)
    )
    assert is_positive_resp(resp, 0x34)

    max_number_of_block_length = resp[2:]
    assert len(max_number_of_block_length) <= 4
    return int.from_bytes(max_number_of_block_length, "big")


def transfer_data(sock: isotp.socket, data: bytes, block_len: int):
    """
    0x36 Transfer Data
    """
    for seq, i in enumerate(range(0, len(data), block_len), 1):
        sequence_num = seq & 0xFF
        resp = send_recv(
            sock, bytes([0x36]) + p8(sequence_num) + data[i : i + block_len]
        )
        assert is_positive_resp(resp, 0x36)


def request_transfer_exit(sock: isotp.socket):
    """
    0x37 Request Transfer Exit
    """
    resp = send_recv(sock, bytes([0x37]))
    assert is_positive_resp(resp, 0x37)


class UploaderToEcu:
    """
    Combination of Request Download, Transfer Data, and Request Transfer Exit.
    """

    def __init__(self, sock: isotp.socket, addr: int, length: int, explicit_exit: bool = True):
        self.sock = sock
        self.addr = addr
        self.length = length
        self.block_len = request_download(sock, addr, length)
        self.explicit_exit = explicit_exit

    def upload(self, data: bytes):
        transfer_data(self.sock, data, self.block_len)
        if self.explicit_exit:
            request_transfer_exit(self.sock)
