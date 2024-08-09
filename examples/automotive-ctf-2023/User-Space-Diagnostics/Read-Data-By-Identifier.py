from can_uds.comm import create_socket
from can_uds.uds import (
    read_memory_by_id,
    reset_ecu,
)
import time

if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8, timeout=2.0)
    reset_ecu(sock)
    time.sleep(5.0)

    for id_ in range(0, 0xFFFF):
        resp = read_memory_by_id(sock, id_)
        if resp:
            print("Found data: ", resp)
            break
