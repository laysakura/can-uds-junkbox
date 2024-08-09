import isotp
from can_uds.comm import create_socket
from can_uds.uds import SecurityAccess, reset_ecu, start_diag_session


def start_level3(sock: isotp.socket):
    start_diag_session(sock, 0x03)
    sec_access = SecurityAccess(sock, 0x03)
    seed = sec_access.request_seed()
    print(f"[level3] Seed: {seed.hex()}")


def start_level1(sock: isotp.socket):
    start_diag_session(sock, 0x02)
    sec_access = SecurityAccess(sock, 0x01)
    seed = sec_access.request_seed()
    print(f"[level1] Seed: {seed.hex()}")

if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)

    start_level3(sock)
    start_level1(sock)
