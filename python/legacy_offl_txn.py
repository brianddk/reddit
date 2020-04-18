#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    https://github.com/brianddk/reddit/python/legacy_offl_txn.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  https://github.com/brianddk/reddit/tipjar.txt

from trezorlib import btc, messages as proto, tools, ui
from trezorlib import MINIMUM_FIRMWARE_VERSION as min_version
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.btc import from_json
from json import loads
from decimal import Decimal
from sys import exit

# Tested with SLIP-0014 allallall seed (slip-0014.md)
# User Provided Fields; These are pulled from test scripts
# CHANGE THESE!!!
coin           = "Testnet"

# Get legacy UTXO prev_txn hex from blockbook server.  For example:
# https://tbtc1.trezor.io/api/tx-specific/ \
#     e5040e1bc1ae7667ffb9e5248e90b2fb93cd9150234151ce90e14ab2f5933bcd
in1_prev_txn_s = '{"txid":"e5040e1bc1ae7667ffb9e5248e90b2fb93cd9150234151ce90e14ab2f5933bcd","hash":"e5040e1bc1ae7667ffb9e5248e90b2fb93cd9150234151ce90e14ab2f5933bcd","version":1,"size":226,"vsize":226,"weight":904,"locktime":0,"vin":[{"txid":"bb0bc570bbde0a0c06f33fa0bd2516149c35c566bf70e8e08861ad9f07400021","vout":0,"scriptSig":{"asm":"3045022100a484e6399d1c0e50b5a26716a0f9c51a2d9d7c0cd6dc41f25f56375e5d0c0b4d02200360655bf46a65688744c411783ed6f048efa238a591af716878af279bfbf66e[ALL] 02dcd8d570036b1575605734359eff834e362bf2ac6463b27bd877b9cb4c6162d1","hex":"483045022100a484e6399d1c0e50b5a26716a0f9c51a2d9d7c0cd6dc41f25f56375e5d0c0b4d02200360655bf46a65688744c411783ed6f048efa238a591af716878af279bfbf66e012102dcd8d570036b1575605734359eff834e362bf2ac6463b27bd877b9cb4c6162d1"},"sequence":4294967295}],"vout":[{"value":0.31000000,"n":0,"scriptPubKey":{"asm":"OP_DUP OP_HASH160 a579388225827d9f2fe9014add644487808c695d OP_EQUALVERIFY OP_CHECKSIG","hex":"76a914a579388225827d9f2fe9014add644487808c695d88ac","reqSigs":1,"type":"pubkeyhash","addresses":["mvbu1Gdy8SUjTenqerxUaZyYjmveZvt33q"]}},{"value":1.42920000,"n":1,"scriptPubKey":{"asm":"OP_DUP OP_HASH160 dd597a4de23945b20a56446ce3a1b6e39cbf351c OP_EQUALVERIFY OP_CHECKSIG","hex":"76a914dd597a4de23945b20a56446ce3a1b6e39cbf351c88ac","reqSigs":1,"type":"pubkeyhash","addresses":["n1hLpUJwuAqRvhYDE3LH6VUEFJAMtTHp8e"]}}],"hex":"0100000001210040079fad6188e0e870bf66c5359c141625bda03ff3060c0adebb70c50bbb000000006b483045022100a484e6399d1c0e50b5a26716a0f9c51a2d9d7c0cd6dc41f25f56375e5d0c0b4d02200360655bf46a65688744c411783ed6f048efa238a591af716878af279bfbf66e012102dcd8d570036b1575605734359eff834e362bf2ac6463b27bd877b9cb4c6162d1ffffffff02c005d901000000001976a914a579388225827d9f2fe9014add644487808c695d88ac40c98408000000001976a914dd597a4de23945b20a56446ce3a1b6e39cbf351c88ac00000000","blockhash":"00000000204a06722dd65156b2c941ca4991246ad177f588c48999e50a2b0506","confirmations":1396431,"time":1424379055,"blocktime":1424379055}'

in1_prev_index = 0
in1_addr_path  = "m/44'/1'/0'/0/0" # allallall seed
in1_amount     = 31000000
out1_address   = "msj42CCGruhRsFrGATiUuh25dtxYtnpbTx"
out1_amount    = in1_amount - 192

# Defaults
tx_version     = 1
tx_locktime    = 0
sequence       = 4294967293

# Code
in1_prev_txn_j  = loads(in1_prev_txn_s, parse_float=Decimal)
in1_prev_hash   = in1_prev_txn_j['txid']
in1_prev_hash_b = bytes.fromhex(in1_prev_hash)
device = get_transport()
client = TrezorClient(transport=device, ui=ui.ClickUI())

fw_version = (client.features.major_version, 
           client.features.minor_version, client.features.patch_version)
if fw_version < min_version[client.features.model]:
    print("Please flash to the latest FW")
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
    script_type=proto.InputScriptType.SPENDADDRESS,
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
