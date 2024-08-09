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
