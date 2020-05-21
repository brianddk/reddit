#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/keys_lol.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     reddit.com/r/Bitcoin/comments/gnogna/_/frbbwbr/
# [req]     pip3 pycoin

from pycoin.symbols.btc import network as btc

BIT_WIDTH=256

for exp in range(1, 2**BIT_WIDTH):
    print(btc.parse.secret_exponent(exp).address())
