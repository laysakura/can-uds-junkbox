# You need to:
#   pip install randcrack

import time
import isotp
from randcrack import RandCrack
from can_uds.comm import create_socket
from can_uds.uds import (
    SecurityAccess,
    reset_ecu,
)


def solve_level5(sock: isotp.socket):
    """
    メルセンヌ・ツイスタをcrackする。
    624個の乱数列から、次の乱数が予想できる。
    """
    rc = RandCrack()
    sec_access = SecurityAccess(sock, 0x05)

    for i in range(624):
        seed = sec_access.request_seed()
        print(f"[level5] seed{i}: {seed.hex()}")
        rc.submit(int.from_bytes(seed, "big"))

    key_ = rc.predict_getrandbits(32)
    key = key_.to_bytes(4, "big")
    print(f"[level5] predicted key: {key.hex()}")

    if sec_access.send_key(key):
        print("[level5] Security Access Level5 succeeded")
    else:
        print("[level5] Security Access Level5 failed")


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)
    time.sleep(3.0)

    solve_level5(sock)
