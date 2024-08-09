from can_uds.comm import create_socket
from can_uds.uds import (
    RoutineControl,
    reset_ecu,
)
import time

if __name__ == "__main__":
    sock = create_socket("vcan0", 0x7E0, 0x7E8, timeout=2.0)
    reset_ecu(sock)
    time.sleep(5.0)

    for routine_id in range(0, 0xFFFF):
        ctrl = RoutineControl(sock, routine_id)
        resp = ctrl.call_routine()
        if resp:
            print(f"Found data @ routine id = {routine_id}: ", resp)
