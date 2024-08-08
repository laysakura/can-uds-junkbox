import argparse
import can


def send_recv(bus, arbitration_id, data):
    """
    メッセージの送受信を行う関数
    Returns: CANフレームdataの配列
    """
    msg = can.Message(
        arbitration_id=arbitration_id,
        dlc=len(data),
        data=data,
        is_extended_id=False,
    )
    bus.send(msg)

    responses = []
    while True:
        resp = bus.recv(timeout=0.2)
        if resp is None:
            break
        responses.append(resp)

    if not responses:
        print(f"Error: No response received (data={data})")
        return None

    return responses


def dump_memory(bus, arbitration_id, start_addr, length, ignore_zero):
    """
    メモリダンプを行う関数
    """
    # 128バイトずつダンプする
    for addr in range(start_addr, start_addr + length, 0x80):
        # メモリダンプのためのメッセージを作成
        byte1 = (addr >> 24) & 0xFF
        byte2 = (addr >> 16) & 0xFF
        byte3 = (addr >> 8) & 0xFF
        byte4 = addr & 0xFF
        read_mem_data = [0x07, 0x23, 0x14, byte1, byte2, byte3, byte4, 0x80]

        # メッセージ送信 & レスポンス受信
        responses = send_recv(bus, arbitration_id, read_mem_data)
        if responses is None:
            print(f"Error: No response received for address 0x{start_addr:08X}")
            return

        # レスポンスを解析し、ダンプ
        for i_resp, resp in enumerate(responses):
            data = resp.data[1:]
            for i in range(0, len(data), 16):
                # ignore_zero が True の場合、0x00 だけの行を出力しない
                if ignore_zero and all(b == 0 for b in data[i : i + 16]):
                    continue

                addr_by_16 = addr + (i_resp * 0x80) + i
                hex_data = " ".join(f"{b:02X}" for b in data[i : i + 16])
                ascii_data = "".join(
                    chr(b) if 32 <= b <= 126 else "." for b in data[i : i + 16]
                )
                print(f"{addr_by_16:08X} {hex_data} {ascii_data}")


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
        action='store_true',
        required=False,
        help="0x00 だけの行を出力しない",
    )
    args = parser.parse_args()

    try:
        # CAN バスの設定
        bus = can.interface.Bus(channel=args.interface, bustype="socketcan")
        # プログラムセッションへ移行
        send_recv(
            bus, args.arbitration_id, [0x02, 0x10, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        # メモリダンプの実行
        dump_memory(bus, args.arbitration_id, args.start_address, args.length, args.ignore_zero)
    finally:
        bus.shutdown()
