import isotp

from can_uds.comm import is_positive_resp, send_recv


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
