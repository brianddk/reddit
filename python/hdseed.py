#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/sqldump.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     python -m pip install electrum
# [note]    To run in electrum console, correct file path and run:
#    with open(r"C:\Windows\Temp\hdseed.py") as f: exec(f.read())

from mnemonic import Mnemonic as BIP39
from electrum.bitcoin import serialize_privkey as to_wif
from electrum.bip32 import BIP32Node
from electrum import constants

try:
    # If defined, we are in electrum console
    wallet 
except NameError:
    # Not in electrum console, free to toggle network
    constants.set_testnet()
if(constants.net.TESTNET):
    bip39  = BIP39("English")
    mnemo  = bip39.generate()
    seed   = bip39.to_seed(mnemo)
    bip32  = BIP32Node.from_rootseed(seed, xtype='standard')
    bip44k = bip32.subkey_at_private_derivation("m/44'/1'/0'/0/0").eckey
    bip49k = bip32.subkey_at_private_derivation("m/49'/1'/0'/0/0").eckey
    bip84k = bip32.subkey_at_private_derivation("m/84'/1'/0'/0/0").eckey
    bip44w = to_wif(bip44k.get_secret_bytes(),True,'p2pkh').split(':')[-1]
    bip49w = to_wif(bip49k.get_secret_bytes(),True,'p2wpkh-p2sh').split(':')[-1]
    bip84w = to_wif(bip84k.get_secret_bytes(),True,'p2wpk').split(':')[-1]
    print(f'Your BIP39 Mnemonic:     "{mnemo}"')
    print(f'Your BIP32 Root Key:     "{bip32.to_xprv()}"')
    print(f'Your legacy hdseed:      "{bip44w}"')
    print(f'Your p2sh-segwit hdseed: "{bip49w}"')
    print(f'Your bech32 hdseed:      "{bip84w}"')
else:
    print("You are not on Testnet, Exiting for safety")
