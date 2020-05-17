#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/mining.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

spot = 8939.90
hashrate = 110 * 10**12
difficulty = float("16,104,807,485,529".replace(',','_'))
reward = 12.5
usd_per_day = (spot * hashrate * reward * 60 * 60 * 24) / (difficulty * 2**32)
print(usd_per_day)
