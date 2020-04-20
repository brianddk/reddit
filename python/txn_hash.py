#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/txn_hash.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/g4hvyf

from hashlib import sha256
from sys import exit

def isvi(vint):
    if (vint >= int('fd'):
        print("ERROR: varint detected")
        exit(1)

def slice_int(b,s,w=1, test=True):
    s = int(b[s:s+w].hex(),16)
    if test: isvi(s)
    return s

def txid(tx):
    v  = 4
    f  = 2
    ic = 1    
    bin  = bytes.fromhex(tx)
    p = v; 
    flags = slice_int(bin, p, f, False)
    if flags == 1:
        p+=f
        inc = slice_int(bin, p)
        p+=1
        for i in range(0, inc):
            p+=36
            s = slice_int(bin,p)
            p+=1
            p += s + 4
        ouc = slice_int(bin, p)
        p+=1
        for o in range(0, ouc):
            p+=8
            s = slice_int(bin,p)
            p+=1
            p += s
        bin = bin[:4] + bin[6:p] + bin[-4:]
    txid = sha256(sha256(bin).digest()).digest()[::-1].hex()
    return txid

#Raw Legacy
t0 = ('0200000001cd3b93f5b24ae190ce5141235091cd93fbb2908e24e5b9ff6776ae'
      'c11b0e04e5000000006b4830450221009f156db3585c19fe8e294578edbf5b5e'
      '4159a7afc3a7a00ebaab080dc25ecb9702202581f8ae41d7ade2f06c9bb9869e'
      '42e9091bafe39290820438b97931dab61e140121030e669acac1f280d1ddf441'
      'cd2ba5e97417bf2689e4bbec86df4f831bf9f7ffd0fdffffff010005d9010000'
      '00001976a91485eb47fe98f349065d6f044e27a4ac541af79ee288ac00000000')

#Raw Segwit
t1 = ('0200000000010100ff121dd31ead0f06e3014d9192be8485afd6459e36b09179'
      'd8c372c1c494e20000000000fdffffff013ba3bf070000000017a914051877a0'
      'cc43165e48975c1e62bdef3b6c942a38870247304402205644234fa352d1ddbe'
      'c754c863638d2c26abb9381966358ace8ad7c52dda4250022074d8501460f4e4'
      'f5ca9788e60afafa1e1bcbf93e51529defa48317ad83e069dd012103adc58245'
      'cf28406af0ef5cc24b8afba7f1be6c72f279b642d85c48798685f86200000000')

# **UPDATE** Raw Segwit with flags and tx_witnesses stripped      
t2 = ('02000000'  '0100ff121dd31ead0f06e3014d9192be8485afd6459e36b09179'
      'd8c372c1c494e20000000000fdffffff013ba3bf070000000017a914051877a0'
      'cc43165e48975c1e62bdef3b6c942a3887'                    '00000000')

print(f"t0: {txid(t0)}\nt1: {txid(t1)}\nt2: {txid(t2)}")

# TXN_IDs from the above python
# t0: cb33472bcaed59c66fae30d7802b6ea2ca97dc33c6aad76ce2e553b1b4a4e017
# t1: b11fdde7e3e635c7f15863a9399cca42d46b5a42d87f4e779dfd4806af2401ce
# t2: d360581ee248be29da9636b3d2e9470d8852de1afcf3c3644770c1005d415b30

# TXN_IDs from Electrum
# Correct
# t0: cb33472bcaed59c66fae30d7802b6ea2ca97dc33c6aad76ce2e553b1b4a4e017
# t1: d360581ee248be29da9636b3d2e9470d8852de1afcf3c3644770c1005d415b30

