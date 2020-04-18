With the rollout of the new 0.12.0 API, I thought it might be time to update some of my old `offline_txn` scripts.  The following is about 80 lines of python that will craft and sign a ***VERY*** simple transaction on Testnet.

The new rollout also comes with some new tools.  The [build_tx.py](https://github.com/trezor/trezor-firmware/blob/master/python/tools/build_tx.py) that is useful in conjunction with the `trezorctl` `sign_tx` command.

Both of the methods below will produce a signed TXN that can then be imported into Electrum using the "Tools -> Load transaction -> From text" command.

Note: u/Crypto-Guide has a [good walkthrough](https://youtu.be/-DBf8aoVemw) for installing `trezorlib` in Windows if you haven't already done that.

## Example of using `trezorctl btc sign-tx`

This example uses the `build_tx.py` script to build JSON to feed to the `sign-tx` command.  You will need to download the [build_tx.py](https://github.com/trezor/trezor-firmware/blob/master/python/tools/build_tx.py) file from github.  It is not automatically installed with the `trezor` package.  The JSON format (if your interested) is described in [transaction-format.md](https://github.com/trezor/trezor-firmware/blob/master/python/docs/transaction-format.md) which is also on the github repo.

```
# python build_tx.py | trezorctl btc sign-tx -
Coin name [Bitcoin]: Testnet
Blockbook server [btc1.trezor.io]: tbtc1.trezor.io

Previous output to spend (txid:vout) []: e294c4c172c3d87991...060fad1ed31d12ff00:0
BIP-32 path to derive the key: m/84'/1'/0'/0/0
Input amount: 129999866
Sequence Number to use (RBF opt-in enabled by default) [4294967293]:
Input type (address, segwit, p2shsegwit) [segwit]:

Previous output to spend (txid:vout) []:

Output address (for non-change output) []: 2MsiAgG5LVDmnmJUPnYaCeQnARWGbGSVnr3
Amount to spend (satoshis): 129999706

Output address (for non-change output) []:
BIP-32 path (for change output) []:
Transaction version [2]:
Transaction locktime [0]:
Please confirm action on your Trezor device.

Signed Transaction:
0200000000010100ff121dd31ead0f06...f279b642d85c48798685f86200000000
```

## Example of using crafting a TXN using `trezorlib` directly

If your good with python, or want to see how everything works under the hood, here's 80 lines of python to generate a similar signed transaction.

```python
#!/usr/bin/env python3
# [repo]    https://github.com/brianddk/reddit ... python/offline_txn.py
# [req]     pip3 install trezor

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
#     e294c4c172c3d87991b0369e45d6af8584be92914d01e3060fad1ed31d12ff00
in1_prev_txn_s = '{"txid":' \
    '"e294c4c172c3d87991b0369e45d6af8584be92914d01e3060fad1ed31d12ff00"}'

in1_prev_index = 0
in1_addr_path  = "m/84'/1'/0'/0/0" # allallall seed
in1_amount     = 129999867
out1_address   = "2MsiAgG5LVDmnmJUPnYaCeQnARWGbGSVnr3"
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
    script_type=proto.InputScriptType.SPENDWITNESS,
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
```

From here, you simple take the resultant TXN hex and import it into Electrum using the "Tools -> Load transaction -> From text" clickpath