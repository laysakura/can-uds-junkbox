import isotp


def p16(x: int) -> bytes:
    return x.to_bytes(2, "big")


def p32(x: int) -> bytes:
    return x.to_bytes(4, "big")


def p64(x: int) -> bytes:
    return x.to_bytes(8, "big")


def create_socket(interface: str, txid: int, rxid: int) -> isotp.socket:
    s = isotp.socket(0.2)
    s.bind(interface, isotp.Address(txid=txid, rxid=rxid))
    return s


def send_recv(sock, req: bytes) -> isotp.Message:
    sock.send(req)
    return sock.recv()


def is_positive_resp(resp: isotp.Message) -> bool:
    return resp and resp.data[0] != 0x7F
