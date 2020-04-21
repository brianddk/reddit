#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/eth_hash.py
# [eth]     eth/erc20: 0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/r/ethereum/comments/g565bv
# [req]     pip3 install pysha3

from sha3 import keccak_256 as sha3

txn_hex = ('f8aa0b85012a05f20083030d4094a74476443119a942de49859'
           '0fe1f2454d7d4ac0d80b844a9059cbb00000000000000000000'
           '0000a6abb480640d6d27d2fb314196d94463cedcb31e0000000'
           '000000000000000000000000000000000000000000011c37937'
           'e0800026a047ef1bb1625e4152b0febf6ddc1a57bfcea643813'
           '2928dda4c9c092b34f38a78a03f70084c300235d588b7010398'
           '8dd6f367e0f67bf38e2759a4c77aa461b220e2')
txn = bytes.fromhex(txn_hex)
txn_id = sha3(txn).digest().hex()
print(txn_id)