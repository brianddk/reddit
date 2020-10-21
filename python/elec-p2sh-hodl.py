#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/elec-p2sh-hodl.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [txid]    a8110bbdd40d65351f615897d98c33cbe33e4ebedb4ba2fc9e8c644423dadc93
# [ref]     https://live.blockcypher.com/btc-testnet/tx/{txid}/
# [req]     python -m pip install electrum
# [note]    with open(r"..\reddit\python\hodl.py", 'r') as s: exec(s.read())

from electrum.transaction import TxOutpoint, PartialTxInput, PartialTxOutput, PartialTransaction
from electrum.bitcoin import deserialize_privkey, opcodes, push_script
from electrum.crypto import hash_160, sha256d
from electrum.constants import set_testnet
from electrum.ecc import ECPrivkey

# The basic bitcoinlib utility  scripts
x    = lambda h: bytes.fromhex(h)
lx   = lambda h: bytes.fromhex(h)[::-1]
b2x  = lambda b: (b.hex() if 'hex' in dir(b) else hex(b)).replace('0x','')
b2lx = lambda b: b[::-1].hex().replace('0x','')

# Very simple bitcoin script comiler
compile = lambda s: "".join([
    opcodes[i].hex() if i in dir(opcodes) else push_script(i) for i in s])

# Electrum assumes P2SH is multisig, this subclass corrects that
class P2SHPartialTransaction(PartialTransaction):

    def __init__(self):
        PartialTransaction.__init__(self)
    
    @classmethod
    def get_preimage_script(cls, txin: 'PartialTxInput') -> str:
        return b2x(txin.redeem_script)

# Set testnet
set_testnet()

# I removed the R-value grinding to use "legacy" sig processing
# This is the original TXID we are trying to hit
otxid = 'a8110bbdd40d65351f615897d98c33cbe33e4ebedb4ba2fc9e8c644423dadc93'

# Basic constants to build the TXNIN
wif = 'cQNjiPwYKMBr2oB3bWzf3rgBsu198xb8Nxxe51k6D3zVTA98L25N'
txid = x('6d500966f9e494b38a04545f0cea35fc7b3944e341a64b804fed71cdee11d434')
vout = 1
sats = 9999
script_type = 'p2sh'
binzero  = 2**32
sequence = binzero - 3
address = 'tb1qv9hg20f0g08d460l67ph6p4ukwt7m0ttqzj7mk'
sats_less_fees = sats - 200
locktime = 1602565200

# Build the Transaction Input
_, privkey, compressed = deserialize_privkey(wif)
pubkey = ECPrivkey(privkey).get_public_key_hex(compressed=compressed)
prevout = TxOutpoint(txid=txid, out_idx=vout)
txin = PartialTxInput(prevout=prevout)
txin.nsequence = sequence
txin.script_type = script_type
expiry = b2x(lx(b2x(locktime)))
redeem_script = compile([
    expiry, 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', pubkey, 'OP_CHECKSIG'])
txin.redeem_script = x(redeem_script)

# Build the Transaction Output
txout = PartialTxOutput.from_address_and_value(address, sats_less_fees)

# Build and sign the transaction
tx = P2SHPartialTransaction.from_io([txin], [txout], locktime=locktime)
tx.version = 1
sig = tx.sign_txin(0, privkey)
txin.script_sig = x(compile([sig , redeem_script]))

# Get the serialized txn and compute txid
txn = tx.serialize()
txid = b2lx(sha256d(x(txn)))

# Ensure we arrived at where we intended
if txid != otxid:
    print("Did not achive target TXID hash")
    print("Perhaps R-value hashing needs to be reverted")
    Print("See: https://redd.it/jf97pc")

# Display results
print("pubk:", pubkey)
print("priv:", b2x(privkey))
print("txid:", txid)
print("txn:", txn)
