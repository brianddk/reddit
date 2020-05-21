#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/bad_address.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     pip3 pycoin mnemonic

from mnemonic import Mnemonic
from pycoin.symbols.btc import network as btc

code = ("abandon abandon abandon abandon abandon abandon" + 
        " abandon abandon abandon abandon abandon about")
path = '44H/0H/0H/0/0'
mnemo = Mnemonic("english")

one_privkey = btc.parse.secret_exponent(1).address()
zero_hash   = btc.address.for_p2pkh(bytes([0]*20))
one_bip39   = btc.keys.bip32_seed(mnemo.to_seed(code)
                ).subkey_for_path(path).address()

print(one_privkey, one_bip39, zero_hash)
    