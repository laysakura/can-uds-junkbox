from can_uds.comm import create_socket
from can_uds.uds import (
    read_memory_by_id,
    reset_ecu,
)


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)

    for id_ in range(0, 0xFFFF):
        resp = read_memory_by_id(sock, id_)
        if resp:
            print("Found data: ", resp)
            break
