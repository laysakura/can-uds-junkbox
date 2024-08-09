import isotp


def create_socket(
    interface: str, txid: int, rxid: int, timeout: float = 1.0
) -> isotp.socket:
    s = isotp.socket(timeout=timeout)
    s.bind(interface, isotp.Address(txid=txid, rxid=rxid))
    return s


def send_recv(sock: isotp.socket, req: bytes) -> bytes:
    sock.send(req)
    return sock.recv()


def is_positive_resp(resp: bytes, req_sid: int) -> bool:
    """
    Positive response has at least 1 byte. This function checks it.

    - SID (request SID + 0x40)
    """
    if len(resp) == 0:
        return False

    return resp[0] == req_sid + 0x40


def is_negative_resp(resp: bytes, req_sid: int) -> bool:
    """
    Negative response has at least 3 bytes. This function checks them.

    - SID (0x7F)
    - SIDRQ (same as the request SID)
    - NRC
    """
    if len(resp) < 3:
        return False

    if resp[0] != 0x7F:
        return False

    return resp[1] == req_sid
