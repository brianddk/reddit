#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/mk-electrum.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/Electrum/comments/h8gajd/_/fur8451/
# [req]     pip3 install pycoin mnemonic

from mnemonic import Mnemonic
from pycoin.networks.bitcoinish import create_bitcoinish_network as btcnet
from json import dump, dumps

ACCT84   = '84H/0H/0H'
pub, prv = ("04b24746", "04b2430c")
HW84     = dict(bip32_pub_prefix_hex=pub, bip32_prv_prefix_hex=prv)
SLIP_14  = "all all all all all all all all all all all all"

mnemo = Mnemonic("english")
seed  = mnemo.to_seed(SLIP_14)
net   = btcnet("", "", "", **HW84)
key   = net.keys.bip32_seed(seed)
xprv  = key.subkey_for_path(ACCT84).hwif(as_private=True)
xpub  = key.subkey_for_path(ACCT84).hwif(as_private=False)

wallet = dict(
            keystore = dict(
                pw_hash_version = 1,
                type            = "bip32",
                xprv            = xprv,
                xpub            = xpub,
            ),
            seed_type           = "bip39",
            seed_version        = 18,
            use_encryption      = False,
            wallet_type         = "standard"
)

with open("scripted_wallet", "w+") as w:
    dump(wallet, w, indent=4)
