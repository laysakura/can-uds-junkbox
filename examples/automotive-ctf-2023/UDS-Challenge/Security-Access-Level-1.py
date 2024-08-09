from can_uds.comm import create_socket
from can_uds.uds import SecurityAccess, reset_ecu, start_diag_session


if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    reset_ecu(sock)

    start_diag_session(sock, 0x02)

    sec_access = SecurityAccess(sock, 0x01)
    seed = sec_access.request_seed()
    print(f"Seed: {seed.hex()}")
