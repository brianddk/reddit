#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/dump-blkdat.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [txid]    e9c05a5f454d6bd10803eb20a8ba529bcf8d85f441b35ca7c8a4a67e26bdfa1a
# [ref]     https://www.reddit.com/r/Bitcoin/comments/jmiko9/

from struct import unpack
from hashlib import sha256
from time import strftime, gmtime
from sys import argv, exit
from os.path import isfile
b2x = lambda x: x.hex()
b2lx = lambda x: x[::-1].hex()
Hash256 = lambda x: sha256(sha256(x).digest()).digest()

def header(first):
    hdr = "==========================================================================================================================="
    msg = "   SIZE nVersion BlockHash                                                        TimeStamp      Bits     Nonce        TXNs"
    if first: print(msg + '\n' + hdr)
    else:     print(hdr + '\n' + msg)

class Block():

    def __init__(s, data):
        s.magic, s.size, s.version, s.hash, s.prevhash, s.merk, s.epoch, s.bits, s.nonce, s.count = [None] * 10
        if type(data) is bytes:
            s.magic, s.size, blockheader, s.count = unpack('<4sI80s9s', data)
            s.version, s.prevhash, s.merk, s.epoch, s.bits, s.nonce = unpack('<4s32s32sI4sI', blockheader)
            s.hash = Hash256(blockheader)
            s._isvalid()

    def __str__(s):
        time = strftime("%b%d %H:%M:%S", gmtime(s.epoch))
        rtn = [f"{s.size:7d}", b2lx(s.version), b2lx(s.hash), time, b2lx(s.bits), f"{s.nonce:10d}", f"{s._varint(s.count):6d}"]
        return " ".join([str(i) for i in rtn])

    def _varint(s, data):
        x = data[0]
        if   x < 0xfd: return x
        elif x < 0xfe: return int(b2lx(data[1:3]),16)
        elif x < 0xff: return int(b2lx(data[1:5]),16)
        else         : return int(b2lx(data[1:9]),16)

    def _isvalid(s):
        assert b2x(s.magic) == 'f9beb4d9' or b2x(s.magic) == '0b110907' or b2x(s.magic) == 'fabfb5da'

if __name__ == "__main__":
    if len(argv) > 1 and isfile(argv[1]):
        blockfile = argv[1]
    else:
        print("Usage:", argv[0], "[blk?????.dat]")
        exit(1)
    buffer = True
    with open(blockfile, 'rb') as f:
        header(True)
        while buffer:
            buffer = f.read(4*6 + 32*2 + 9)
            if buffer:
                block = Block(buffer)
                print(block)
                f.read(block.size-(4*6 + 32*2 + 9)+8)
        header(False)
