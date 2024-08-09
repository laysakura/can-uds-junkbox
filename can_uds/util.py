def p16(x: int) -> bytes:
    return x.to_bytes(2, "big")


def p32(x: int) -> bytes:
    return x.to_bytes(4, "big")


def p64(x: int) -> bytes:
    return x.to_bytes(8, "big")
