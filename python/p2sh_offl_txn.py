#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/p2sh_offl_txn.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip3 install trezor

from trezorlib import btc, messages as proto, tools, ui
from trezorlib import MINIMUM_FIRMWARE_VERSION as min_version
from trezorlib import __version__ as lib_version
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.btc import from_json
from sys import version_info as py_ver, exit
from decimal import Decimal
from json import loads

# Tested with SLIP-0014 allallall seed (slip-0014.md)
# User Provided Fields; These are pulled from test scripts
# CHANGE THESE!!!
coin           = "Testnet"

# Get legacy UTXO prev_txn hex from blockbook server.  For example:
# https://tbtc1.trezor.io/api/tx-specific/ \
#     65b811d3eca0fe6915d9f2d77c86c5a7f19bf66b1b1253c2c51cb4ae5f0c017b
in1_prev_txn_s = '{"txid":' \
    '"65b811d3eca0fe6915d9f2d77c86c5a7f19bf66b1b1253c2c51cb4ae5f0c017b"}'

in1_prev_index = 0
in1_addr_path  = "m/49'/1'/0'/0/0" # allallall seed
in1_amount     = 5000000
out1_address   = "2Mt7P2BAfE922zmfXrdcYTLyR7GUvbwSEns"
out1_amount    = in1_amount - 192

# Defaults
tx_version     = 2
tx_locktime    = 0
sequence       = 4294967293

# Code
in1_prev_txn_j  = loads(in1_prev_txn_s, parse_float=Decimal)
in1_prev_hash   = in1_prev_txn_j['txid']
in1_prev_hash_b = bytes.fromhex(in1_prev_hash)
device = get_transport()
client = TrezorClient(transport=device, ui=ui.ClickUI())

fw = client.features
fw_min = min_version[fw.model]
py_min = (3,6,0)
tl_min = [0,12,0]
if (fw_min > (fw.major_version, fw.minor_version,fw.patch_version) or 
    tl_min > [int(i) for i in lib_version.split('.')] or py_min > py_ver):
    m = "Requires at least Python rev {}, trezorlib rev {}, and FW rev {}"
    print(m.format(py_min, tl_min, fw_min))
    exit(1)
    
signtx = proto.SignTx(
    version = tx_version,
    lock_time = tx_locktime
)

ins = [proto.TxInputType(
    address_n=tools.parse_path(in1_addr_path),
    prev_hash=in1_prev_hash_b,
    prev_index=in1_prev_index,
    amount=in1_amount,
    script_type=proto.InputScriptType.SPENDP2SHWITNESS,
    sequence=sequence
)]
outs = [proto.TxOutputType(
    address=out1_address,
    amount=out1_amount,
    script_type=proto.OutputScriptType.PAYTOADDRESS
)]

txes = None
for i in ins:
    if i.script_type == proto.InputScriptType.SPENDADDRESS:
        tx = from_json(in1_prev_txn_j)
        txes = {in1_prev_hash_b: tx}
        break

_, serialized_tx = btc.sign_tx(client, coin, ins, outs, 
                               details=signtx, prev_txes=txes)
client.close()
print(f'{{"hex": "{serialized_tx.hex()}"}}')
