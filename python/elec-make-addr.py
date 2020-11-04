#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/elec-make-addr.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/Bitcoin/comments/jnrzcc/-/gb3hjqv/
# [req]     python -m pip install electrum
# [note]    with open(r"..\reddit\python\script.py", 'r') as s: exec(s.read())

from electrum.constants import set_testnet, set_mainnet
from electrum.ecc import ECPrivkey
from electrum.bitcoin import pubkey_to_address, serialize_privkey
from random import randint

# Set testnet
set_testnet()

# Set mainnet
# set_mainnet()

# Number of addresses to generate:
n = 20

# Type of address
type = 'p2wpkh'
# type = 'p2wpkh-p2sh'
# type = 'p2pkh'

# https://www.secg.org/sec2-v2.pdf section 2.4.1
def get_priv():
    n = 'FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141'
    n = int(n.replace(' ',''), 16)
    priv = randint(1, n-1)
    return bytes.fromhex(f"{priv:064x}")
    
# You get this from Wallet info dialog
for i in range(0, n):
    priv = get_priv()
    wif  = serialize_privkey(priv, True, '').replace(':', '')
    pubk = ECPrivkey(priv).get_public_key_bytes()
    addr = pubkey_to_address('p2wpkh', pubk.hex())
    print(f"WIF: {wif} Address: {addr}")
