#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/elec-p2sh-hodl.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [txid]    3a461e6de82cb2365e9105b127e7e2976da998aeaf7284333304bd3ff78de2b6
# [ref]     https://live.blockcypher.com/btc-testnet/tx/{txid}/
# [req]     python -m pip install electrum
# [note]    with open(r"..\reddit\python\hodl.py", 'r') as s: exec(s.read())

from electrum.transaction import TxOutpoint, PartialTxInput, PartialTxOutput, PartialTransaction
from electrum.bitcoin import deserialize_privkey, opcodes, push_script
from electrum.crypto import hash_160, sha256, sha256d
from electrum.ecc import ECPrivkey
from electrum.segwit_addr import encode
from electrum import constants

# The basic bitcoinlib utility  scripts
x    = lambda h: bytes.fromhex(h)
lx   = lambda h: bytes.fromhex(h)[::-1]
b2x  = lambda b: (b.hex() if 'hex' in dir(b) else hex(b)).replace('0x','')
b2lx = lambda b: b[::-1].hex().replace('0x','')

# Very simple bitcoin script comiler
compile = lambda s: "".join([
    opcodes[i].hex() if i in dir(opcodes) else push_script(i) for i in s])

bech32_encode = lambda w: encode(constants.net.SEGWIT_HRP, 0, x(w))

# Set testnet
constants.set_testnet()

# Basic constants to build the TXNIN
wif = 'cNyQjVGD6ojbLFu1UCapLCM836kCrgMiC4qpVTV9CUx8kVc5kVGQ'
txid = x('ef3fad03b7fd4fe42956e41fccb10ef1a95d98083d3b9246b6c17a88e51c8def')
vout = 1
sats = 10_000
sequence = 0 # in retrospect "-3" in two's complement may be better
address = 'tb1q5rn69avl3ganw3cmhz5ldcxpash2kusq7sncfl'
sats_less_fees = sats - 500
locktime = 1602572140

# Build the Transaction Input
_, privkey, compressed = deserialize_privkey(wif)
pubkey = ECPrivkey(privkey).get_public_key_hex(compressed=compressed)
expiry = b2x(lx(b2x(locktime)))
witness_script = compile([
    expiry, 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', pubkey, 'OP_CHECKSIG'])
script_hash = b2x(sha256(x(witness_script)))
hodl_address = bech32_encode(script_hash)
prevout = TxOutpoint(txid=txid, out_idx=vout)
txin = PartialTxInput(prevout=prevout)
txin._trusted_value_sats = sats
txin.nsequence = sequence
txin.script_sig = x(compile([])) # empty script (important!)
txin.witness_script = x(witness_script)

# Build the Transaction Output
txout = PartialTxOutput.from_address_and_value(address, sats_less_fees)

# Build and sign the transaction
tx = PartialTransaction.from_io([txin], [txout], locktime=locktime)
tx.version = 1
txin_index = 0
sig = tx.sign_txin(txin_index, privkey)

# Prepend number of elements in script per the spec.
script = [sig, witness_script]
size = bytes([len(script)])
txin.witness = size + x(compile(script))

# Get the serialized txn and compute txid
txn = tx.serialize()

# Display results
print("PayTo:", hodl_address)
print("wif:", wif)
print("pubk:", pubkey)
print("txid:", tx.txid())
print("txn:", txn)
