import hashlib
import isotp
from can_uds.comm import create_socket
from can_uds.uds import RoutineControl, UploaderToEcu, reset_ecu
import os


def mydir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def read_firmware(path) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] Firmware not found: {path}")
        raise


def flash_firmware(sock: isotp.socket, firmware: bytes):
    addr = 0x00  # カスタムファームウェアを書くアドレス。今回はこのアドレスは無視して `/tmp/firmware` に書かれるので何でも良い。

    # チェックサムが必要なので計算して末尾に付け加える
    md5_checksum = hashlib.md5(firmware).digest()
    firmware_with_checksum = firmware + md5_checksum
    print(f"Checksum: {md5_checksum.hex()}")

    uploader = UploaderToEcu(
        sock,
        addr,
        firmware_with_checksum,
        # 今回のシミュレーターでは RequestTransferExit がサポートされていない
        explicit_exit=False,
    )
    uploader.upload()


def exec_firmware(sock: isotp.socket):
    ctrl = RoutineControl(
        sock, 0xA5A5
    )  # ファームウェアを実際に `/tmp/firmware` に書いて実行してもらうためのルーチンID
    resp = ctrl.call_routine()
    assert resp, "Failed to call a5a5 routine"


if __name__ == "__main__":
    print("[NOTE] You need to be in Security Access Level 5.")

    firm_path = os.path.join(mydir(), "firmware.bin")
    print(f"[NOTE] You need to place a firmware to flash in: {firm_path}.")
    firmware = read_firmware(firm_path)

    sock = create_socket("vcan0", 0x7E0, 0x7E8, timeout=30.0)

    print("Flashing firmware...")
    flash_firmware(sock, firmware)
    print("Firmware flashed.")

    exec_firmware(sock)
    print("Firmware executed.")
