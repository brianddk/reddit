#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/bip39-diceware.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/liwe2f

from random import randint, choice
from mnemonic import Mnemonic

nemo = Mnemonic('english')
wordlist = nemo.wordlist
# i = 0
# for R in range(1,7):
    # for G in range(1,7):
        # for B in range(1,7):
            # for W in range(1,7):
                # for C in ['H', 'T']:
                    # if i>=2048: break
                    # print(R, G, B, W, C, ' ', wordlist[i], sep='')
                    # i+=1

L = []
for i in range(100000):
    R, G, B, W, C = (randint(0,5), randint(0,5), randint(0,5), randint(0,5), randint(1,2))
    n = C * (R*(6**3) + G*(6**2) + B*(6**1) + W)
    if n < 2048: L += [n]
    
W = [wordlist[i] for i in L]

p,f = [0,0]
for i in range(len(W)):
    if i < 12: continue
    x = i - 12
    seed = " ".join(W[x:i])
    if nemo.check(seed):
        p +=1
    else:
        f +=1
    # print(test, seed)
    
print(f/p)