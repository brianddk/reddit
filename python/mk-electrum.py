#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/mk-electrum.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/Electrum/comments/h8gajd/_/fur8451/
# [req]     pip3 install pycoin mnemonic

from mnemonic import Mnemonic as Bip39
from electrum.mnemonic import Mnemonic as Bip32
from pycoin.networks.bitcoinish import create_bitcoinish_network as btcnet
from json import dump
from sys import argv

ACCT84   = '84H/0H/0H'
pub, prv = ("04b24746", "04b2430c")
HW84     = dict(bip32_pub_prefix_hex=pub, bip32_prv_prefix_hex=prv)
# SLIP_14  = "all all all all all all all all all all all all"
# ELEC_TST = ("wild father tree among universe such " +
#             "mobile favorite target dynamic credit identify")

def mk_wallet(xprv, xpub, type="bip39", seed=None):
    keystore = dict(
        pw_hash_version = 1,
        type            = "bip32",
        xprv            = xprv,
        xpub            = xpub,
    )
    if seed:
        keystore.update(seed = seed)

    wallet = dict(
                keystore            = keystore,
                seed_type           = type,
                seed_version        = 18,
                use_encryption      = False,
                wallet_type         = "standard"
    )
    
    return wallet

def mk_electrum(file, mnemo, isBip39=False):
    if isBip39:
        bip39 = Bip39("english")
        seed  = bip39.to_seed(mnemo)
        path  = ACCT84
        type  = "bip39"
        mnemo = None
    else:
        seed  = Bip32.mnemonic_to_seed(mnemo, None)
        type  = "segwit"
        path  = "0H"
    
    net   = btcnet("", "", "", **HW84)
    key   = net.keys.bip32_seed(seed)
    xprv  = key.subkey_for_path(path).hwif(as_private=True)
    xpub  = key.subkey_for_path(path).hwif(as_private=False)

    wallet = mk_wallet(xprv, xpub, type=type, seed=mnemo)
    with open(file, "w+") as w:
        dump(wallet, w, indent=4)

if __name__ == "__main__":
    if len(argv) < 5:
        print(f"Usage:\t{argv[0]}",
              "<file> <bip39 Y|N> <passphrase> <mnemonic>")
        print('\tHint: Use "" as your passphrase if you have none')
    else:
        file       = argv[1]
        isBip39    = ('y' in argv[2].lower())
        passphrase = argv[3]
        mnemo      = " ".join(argv[4:]).strip()
        mk_electrum(file, mnemo, isBip39)
