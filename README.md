# can-uds-junkbox

CANやらUDSやらOBD-IIやら使って諸々するライブラリ ( `can_uds` ) とツール群。

`examples/` 以下はCTFとかの解答。

## ライブラリインストール

```bash
python3 -m venv ~/venv
. ~/venv/bin/activate
pip install -e .
```

## ツール群

### read-mem-by-addr.py

UDSの Read Memory By Address (0x23) サービスを使って、指定したアドレスから指定した長さのデータを読み出すツール。

```bash
# 例: vcan0 に対し 7E0 のソースCAN IDを使って RMBA 命令。
#     0xC3F85300 から 0x200 バイト読み出す。
#     0x00 しかない行は出力対象外にする。
python read-mem-by-addr.py vcan0 -a 7E0 -s 0xC3F85300 -l 0x200 -z
```

成功出力例:

```text
C3F85300 81 63 00 00 00 00 00 .c.....
C3F85380 81 63 00 00 00 00 00 .c.....
C3F85D80 10 .
C3F85400 81 63 00 66 6C 61 67 .c.flag
C3F85500 7B 6D 65 6D 2B 72 33 {mem+r3
C3F85580 34 64 7D 00 00 00 00 4d}....
C3F85480 81 63 00 00 00 00 00 .c.....
```

拒否を示す 7F から始まるレスポンスは自動的に検知するので、指定した領域のメモリが全く読めなければ何もダンプされない時がある（正常動作）。
