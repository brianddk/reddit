#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/elec-get-addr.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/Electrum/comments/jn2m0q/-/gaz1dbm/
# [req]     python -m pip install electrum
# [note]    with open(r"..\reddit\python\script.py", 'r') as s: exec(s.read())

from electrum.constants import set_testnet
from electrum.bip32 import BIP32Node
from electrum.bitcoin import pubkey_to_address

# Set testnet
set_testnet()

# You get this from Wallet info dialog
xpub = 'vpub5SLqN2bLY4WeYkHyoQNaC4JuFVxDVWtx7YUjuxRwWTkLocCBy3ejp3X3Uxmefk1ae4ZCpTVYkJPUG2pAgv8K9mdxfgcGDwWRzq7YTWCCmAq'
path = 'm/0/0'
xpub = BIP32Node.from_xkey(xpub)

for i in range(0, 20):
    path = f"{path[:3]}/{i}"
    node = xpub.subkey_at_public_derivation(path)
    pubk = node.eckey.get_public_key_bytes()
    addr = pubkey_to_address('p2wpkh', pubk.hex())
    print(f"Address at path [{path}]: {addr}")
