import time
import isotp
from can_uds.comm import create_socket
from can_uds.uds import (
    SecurityAccess,
    read_memory_by_addr,
    reset_ecu,
    start_diag_session,
)


def start_level1(sock: isotp.socket):
    start_diag_session(sock, 0x02)
    sec_access = SecurityAccess(sock, 0x01)
    seed = sec_access.request_seed()
    assert len(seed) == 4
    print(f"[level1] Seed: {seed.hex()}")

    # アドレス 0x1ac08 にキーが書かれている。
    key = b""
    for _addr, data in read_memory_by_addr(sock, 0x1AC08, 4):
        key += data
    assert len(key) == 4
    print(f"[level1] Key: {key.hex()}")

    ret = sec_access.send_key(key)
    assert ret, "Security Access Level1 failed"


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)
    time.sleep(3.0)

    start_level1(sock)
