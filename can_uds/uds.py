import isotp

from can_uds.comm import is_positive_resp, send_recv
from can_uds.util import p16, p32


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
    assert is_positive_resp(resp), "Start Diagnostic Session failed"


def reset_ecu(sock: isotp.socket):
    """
    0x11 ECU Reset
    """
    resp = send_recv(sock, bytes([0x11, 0x02]))
    assert is_positive_resp(resp), "Reset failed"


def read_memory(
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
        if is_positive_resp(resp):
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
        assert is_positive_resp(resp), "Request Seed failed"
        return resp[2:]

    def send_key(self, key: bytes) -> bool:
        resp = send_recv(self.sock, bytes([0x27, self.level + 1]) + key)
        return is_positive_resp(resp)
