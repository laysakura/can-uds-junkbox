import argparse
import isotp
from can_uds.comm import create_socket, send_recv
from can_uds.util import p16, p32


def _weird_read_memory_by_addr(
    sock: isotp.socket, start_addr: int, length: int
) -> list[tuple[int, bytes]]:
    addr, len_, step = start_addr, length, min(length, 0x800)
    ret = []
    # step バイトずつ読む。
    while step > 0:
        resp = send_recv(sock, bytes([0x23, 0x24]) + p32(addr) + p16(step))
        # ポジティブレスポンスかネガティブレスポンスか知る術がないので、1バイト目からメモリの中身を返してきていると仮定する。
        ret.append((addr, resp[:]))
        addr += step
        len_ -= step
        step = min(step, len_)

    return ret


def dump_firmware(sock: isotp.socket, filename: str, length: int):
    # このECU、ReadMemoryByAddressに対するレスポンスが、ポジティブレスポンスとしてもネガティブレスポンスとしてもおかしい。
    # 1バイト目からメモリの中身を返してきている。
    #
    # （ポジティブレスポンスなら1バイト目は SID + 0x40 になるべき）
    # （ネガティブレスポンスなら1バイト目は 0x7F になるべきで、ELFのマジックコード的にたまたまそうなっている。
    # ただしネガティブレスポンスなら2バイト目は SID になるべきところ、マジックコードの2バイト目になっている。）
    #
    # なので、 read_memory_by_addr の再実装のようなことをする必要があった。

    resp = _weird_read_memory_by_addr(sock, 0x00400000, length)

    with open(filename, "wb") as f:
        for _addr, data in resp:
            f.write(data)


if __name__ == "__main__":
    # コマンドラインパラメータの解析
    parser = argparse.ArgumentParser(description="特定メモリ領域のファームをダンプ")
    parser.add_argument(
        "-l",
        "--length",
        type=lambda x: int(x, 16),
        required=True,
        help="ダンプ長 (16進数) (e.g. 0xFF)",
    )
    args = parser.parse_args()

    print("You have to be in Security Access Level1 to read memory.")

    sock = create_socket("vcan0", 0x7E0, 0x7E8)
    dump_firmware(sock, "firmware.bin", args.length)
