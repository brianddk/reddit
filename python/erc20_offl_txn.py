#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/erc20_offl_txn.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip3 install trezor

from trezorlib import tools, ui, ethereum
from trezorlib import MINIMUM_FIRMWARE_VERSION as min_version
from trezorlib import __version__ as lib_version
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from sys import version_info as py_ver, exit
from rlp import encode as rlp_encode
from web3 import Web3
from hashlib import sha256

# Tested with SLIP-0014 allallall seed (slip-0014.md)
# User Provided Fields; These are pulled from test scripts
# CHANGE THESE!!!
address         = "m/44'/60'/0'/0/0"
token_address   = "0xa74476443119A942dE498590Fe1f2454d7D4aC0d" #EIP-55
to_address      = "0xA6ABB480640d6D27D2FB314196D94463ceDcB31e" #EIP-55
nonce           = 11
gas_price       = 5000000000
gas_limit       = 200000
amount          = 5000000000000000
chain_id        = 1                                            #EIP-155

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

w3 = Web3()
address_n = tools.parse_path(address)
from_address = ethereum.get_address(client, address_n)

min_abi = [
    {
        "name": "transfer",
        "type": "function",
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    }
]
contract = w3.eth.contract(address=token_address, abi=min_abi)
data = contract.encodeABI("transfer", [to_address, amount])
data = bytes.fromhex(data[2:])

sig = ethereum.sign_tx(
    client,
    n=address_n,
    nonce=nonce,
    gas_price=gas_price,
    gas_limit=gas_limit,
    to=token_address,
    value=0,
    data=data,
    chain_id=chain_id,
)

to = bytes.fromhex(to_address[2:])
transaction = rlp_encode((nonce, gas_price, gas_limit, to, amount, data) + sig)
print(f'{{"hex": "0x{transaction.hex()}"}}')
print(sha256(sha256(transaction).digest()).hexdigest())