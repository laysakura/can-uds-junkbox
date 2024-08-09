# can-uds-junkbox

CANやらUDSやらOBD-IIやら使って諸々するツール群

## インストール

```bash
python3 -m venv ~/venv
. ~/venv/bin/activate
pip install -r requirements.txt
```

## read-mem-by-addr.py

UDSの Read Memory By Address (0x23) サービスを使って、指定したアドレスから指定した長さのデータを読み出すツール。

```bash
# 例: vcan0 に対し 7E0 のソースCAN IDを使って RMBA 命令。
#     0xC3F85300 から 0x200 バイト読み出す。
#     0x00 しかない行は出力対象外にする。
python ./can_uds/read-mem-by-addr.py vcan0 -a 7E0 -s 0xC3F85300 -l 0x200 -z
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

失敗出力例 (拒否を示す 7F から始まるレスポンス):

```text
88024f057ae3:~$ python read-mem-by-addr.py vcan0 -a 7E0 -s 0xD3F85300 -l 0x200 -z
D3F85300 7F 23 31 00 00 00 00 .#1....
D3F85380 7F 23 31 00 00 00 00 .#1....
D3F85400 7F 23 31 00 00 00 00 .#1....
D3F85480 7F 23 31 00 00 00 00 .#1....
D3F85500 10 .
```
