import argparse

from can_uds.comm import create_socket
from can_uds.uds import read_memory


def _dump_data(data: bytes, addr: int, ignore_zero: bool):
    """
    データを16バイトずつダンプする関数
    """
    step = 16

    for i in range(0, len(data), step):
        data_ = data[i : i + step]

        # ignore_zero が True の場合、0x00 だけの行を出力しない
        if ignore_zero and all(b == 0 for b in data_):
            continue

        hex_data = " ".join(f"{b:02X}" for b in data_)
        ascii_data = "".join(chr(b) if 32 <= b <= 126 else "." for b in data_)
        print(f"{addr + i:08X}  {hex_data}  {ascii_data}")


def dump_memory(sock, start_addr: int, length: int, ignore_zero: bool):
    """
    Read Memory By Address (0x23) によりメモリダンプを行う関数
    """
    ret = read_memory(sock, start_addr, length)
    for addr, data in ret:
        _dump_data(data, addr, ignore_zero)


if __name__ == "__main__":
    # コマンドラインパラメータの解析
    parser = argparse.ArgumentParser(description="メモリダンプツール")
    parser.add_argument("interface", help="CAN バスインターフェース名")
    parser.add_argument(
        "-a",
        "--arbitration-id",
        type=lambda x: int(x, 16),
        required=True,
        help="ソースCAN ID (e.g. 7DF / 7E0)",
    )
    parser.add_argument(
        "-s",
        "--start-address",
        type=lambda x: int(x, 16),
        required=True,
        help="開始アドレス (16進数) (e.g. 0xC3F80000)",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=lambda x: int(x, 16),
        required=True,
        help="ダンプ長 (16進数) (e.g. 0xFF)",
    )
    parser.add_argument(
        "-z",
        "--ignore-zero",
        action="store_true",
        required=False,
        help="0x00 だけの行を出力しない",
    )
    args = parser.parse_args()

    sock = create_socket(args.interface, args.arbitration_id, args.arbitration_id + 8)
    dump_memory(sock, args.start_address, args.length, args.ignore_zero)
