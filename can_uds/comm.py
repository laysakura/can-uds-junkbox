import isotp


def create_socket(interface: str, txid: int, rxid: int, timeout: float = 1.0) -> isotp.socket:
    s = isotp.socket(timeout=timeout)
    s.bind(interface, isotp.Address(txid=txid, rxid=rxid))
    return s


def send_recv(sock: isotp.socket, req: bytes) -> bytes:
    sock.send(req)
    return sock.recv()


def is_positive_resp(resp: bytes) -> bool:
    return len(resp) > 0 and resp[0] != 0x7F
