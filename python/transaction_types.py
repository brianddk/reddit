#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/transaction_types.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [txid]    e9c05a5f454d6bd10803eb20a8ba529bcf8d85f441b35ca7c8a4a67e26bdfa1a
# [ref]     https://www.reddit.com/r/Bitcoin/comments/jmiko9/
# [req]     python -m pip install bitcoinlib
# [note]    This requires bitcoind running with -testnet -txindex=1
#
import sys
from os import environ
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

from hashlib import sha256
from enum import Enum
from bitcoin import SelectParams
from bitcoin.core import b2x, b2lx, x, Hash160, Hash
from bitcoin.core.script import CScript, OP_HASH160, OP_EQUAL, OP_CHECKSIG, OP_EQUALVERIFY, OP_DUP, OP_0
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.rpc import Proxy

SelectParams('testnet')
proxy = Proxy()
# Not recognized when datadir conf param is present

Sha256  = lambda x: sha256(x).digest()
Hash256 = lambda x: Hash(x)

def patch(asm):
    full = asm
    asm = ''
    for i in full:
        if i == "" or i == "0": i = '0P_0'
        if i == 'OP_NOP1': i = 'OP_DESERIALIZE'
        asm += i + ' '
    return asm.strip()

def pp(asm):
    pp = ""
    rtn = '\n'
    indent = ''
    for i in asm:
        if i == '<': indent = '    '
        if i == '>': indent = ''
        i += ' '
        prev = pp
        pp += i
        if len(pp) > 150 or i == '< ' or i == '> ':
            rtn += prev + '\n' + indent
            pp = i
    rtn = (rtn + pp).strip()
    rtn = rtn.replace('    <', '<')
    rtn = rtn.replace('\n> ', '>\n')
    return rtn

def deserialize(asm, indexes):
    i = 0
    rtn = []
    for j in indexes:
        a = '< ' + proxy._call('decodescript', asm[j])['asm'] + ' >'
        a = patch(a.split())
        rtn += asm[i:j] + a.split()
        i = j + 1
    rtn += asm[i:]
    return rtn

def make_addresses():
    # Or just hardcode it ; hwi ; m/10141'/0' ; m/84'/1'/0'/0/0
    seckey = CBitcoinSecret('cTqr6cjXsev49PWpHXctTbutZQg5kpTWoGZy8z3yZ7jYgmgKYVFo')

    witver=0
    print("wif", seckey)
    print("pubk", b2x(seckey.pub))
    print("")

    # https://en.bitcoin.it/wiki/IP_transaction
    # https://en.bitcoin.it/wiki/Script#Obsolete_pay-to-pubkey_transaction
    script = CScript([seckey.pub, OP_CHECKSIG])
    # p2pk = CBitcoinAddress.from_scriptPubKey(script) # not recognized Issue a PR

    # https://en.bitcoin.it/wiki/Transaction#Pay-to-PubkeyHash
    script = CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG])
    p2pk = p2pkh = CBitcoinAddress.from_scriptPubKey(script)

    print("p2pk", p2pk)
    print("p2pkh", p2pkh)

    # https://github.com/bitcoin/bips/blob/master/bip-0016.mediawiki#specification
    redeemScript = CScript([seckey.pub, OP_CHECKSIG])
    script = CScript([OP_HASH160, Hash160(redeemScript), OP_EQUAL])
    print("p2sh", CBitcoinAddress.from_scriptPubKey(script))
    p2sh_redeemScript = " ".join(deserialize([b2x(redeemScript)],[0]))

    # https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh
    script = CScript([OP_0, Hash160(seckey.pub)])
    print("p2wpkh", CBitcoinAddress.from_scriptPubKey(script))

    # https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wsh
    witnessScript = CScript([seckey.pub, OP_CHECKSIG])
    script = CScript([OP_0, Sha256(witnessScript)])
    print("p2wsh", CBitcoinAddress.from_scriptPubKey(script))
    p2wsh_witnessScript = " ".join(deserialize([b2x(witnessScript)],[0]))

    # https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh-nested-in-bip16-p2sh
    redeemScript = CScript([OP_0, Hash160(seckey.pub)])
    script = CScript([OP_HASH160, Hash160(redeemScript), OP_EQUAL])
    print("p2sh-p2wpkh", CBitcoinAddress.from_scriptPubKey(script))
    p2sh_p2wpkh_redeemScript = " ".join(deserialize([b2x(redeemScript)],[0]))

    # https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wsh-nested-in-bip16-p2sh
    witnessScript = CScript([seckey.pub, OP_CHECKSIG])
    redeemScript = CScript([OP_0, Sha256(witnessScript)])
    script = CScript([OP_HASH160, Hash160(redeemScript), OP_EQUAL])
    print("p2sh-p2wsh", CBitcoinAddress.from_scriptPubKey(script))

    print("",)
    print("p2sh_redeemScript",p2sh_redeemScript)
    print("p2wsh_witnessScript",p2wsh_witnessScript)
    print("p2sh_p2wpkh_redeemScript",p2sh_p2wpkh_redeemScript)

    print("p2sh_p2wsh_witnessScript", " ".join(deserialize([b2x(witnessScript)],[0])))
    print("p2sh_p2wsh_redeemScript", " ".join(deserialize([b2x(redeemScript)],[0])))

class TxType(Enum):
    unknown     =  0
    p2sh_p2wpkh =  1
    p2sh_p2wsh  =  2
    p2wpkh      =  4
    p2wsh       =  8
    p2sh        = 16
    p2pkh       = 32
    p2pk        = 64
    op_return   =128

class Transaction():

    def __init__(self):
        self.found = 0
        self.printed = 0
        self.unknowns = []

    def process(self, g1, g2, g3, k):
        ss  = b2x(self.ss)
        spk = b2x(self.spk)
        assembled = g1 +ss+ g2 +spk+ g3
        asm = proxy._call('decodescript', assembled)['asm']
        asm = patch(self.wp + asm.split())
        asm = asm.split()
        print(f"\n=== {self.type} === Level 1 === {self.txid}:{k} ===\n" + pp(asm))
        w = len(self.wp) - 1
        s = w + 3
        idxs = []
        if self.type == TxType.p2sh_p2wpkh: idxs = [s]
        if self.type == TxType.p2sh_p2wsh:  idxs = [w,s]
        if self.type == TxType.p2wsh:       idxs = [w]
        if self.type == TxType.p2sh:        idxs = [len(proxy._call('decodescript', ss)['asm'].split()) - 1]
        if idxs:
            asm = deserialize(asm, idxs)
            print(f"\n=== {self.type} === Level 2 === {self.txid}:{k} ===\n" + pp(asm))
        self.printed |= self.type.value

    def get_script(self, inout):
        is_in  = inout.get('scriptSig', False)
        is_out = inout.get('scriptPubKey', False)
        if inout.get('coinbase', False):
            return False
        elif is_out:
           self.spk = x(is_out.get('hex', ''))
        else:
            self.ss = x(is_in.get('hex', ''))
            self.wp = inout.get('txinwitness', [])
            po = inout.get('txid', False)
            pn = inout.get('vout', False)
            if po:
                pt = proxy._call('getrawtransaction', po, True)
                t = pt['vout'][pn]
                self.spk = x(t['scriptPubKey']['hex'])
        return True

    def gettxn(self, txid):
        wp, ss, spk = [[], b'', b'']
        self.wp  = wp
        self.ss  = ss
        self.spk = spk
        self.type = TxType.unknown
        self.txid = txid
        txn = proxy._call('getrawtransaction', txid, True, bhash)
        k = -1
        for vout in txn['vout']:
            k += 1
            if self.found == 255: break
            if self.get_script(vout):
                pass
            else:
                continue
            if (self.spk[0:1]).hex() == '6a' or (self.spk[-1:]).hex() == '6a':         # op_return
                self.type,g1,g2,g3=[TxType.op_return, '', '', '']
                self.found |= self.type.value
                if self.printed & self.type.value:
                    pass
                else:
                    self.process(g1, g2, g3, k)

        k = -1
        for vin in txn['vin']:
            k += 1
            if self.found == 255: break
            if self.get_script(vin):
                pass
            else:
                continue
            type = TxType.unknown
            ss = self.ss
            spk = self.spk
            if   len(ss)  == 23 and (ss[0:3]).hex() == '160014': type,g1,g2,g3=[TxType.p2sh_p2wpkh, '76a9', '76', '69b07c7588ac'] # p2sh-p2wpkh
            elif len(ss)  == 35 and (ss[0:3]).hex() == '220020': type,g1,g2,g3=[TxType.p2sh_p2wsh,  '76a8', '76', '69b07c7588b0'] # p2sh-p2wsh
            elif len(spk) == 22 and (spk[0:2]).hex() == '0014':  type,g1,g2,g3=[TxType.p2wpkh,      '76a9', ''  , '7c7588ac']     # p2wpkh
            elif len(spk) == 34 and (spk[0:2]).hex() == '0020':  type,g1,g2,g3=[TxType.p2wsh,       '76a8', ''  , '7c7588b0']     # p2wsh
            elif len(spk) == 23 and (spk[0:2] + spk[22:23]).hex() == 'a91487': type,g1,g2,g3=[TxType.p2sh,      '', '76', '69b0'] # p2sh
            elif len(spk) == 25 and (spk[0:3] + spk[23:25]).hex() == '76a91488ac': type,g1,g2,g3=[TxType.p2pkh, '', '',   '']     # p2pkh
            elif len(spk) == 35 and (spk[0:1] + spk[34:35]).hex() == '21ac':       type,g1,g2,g3=[TxType.p2pk,  '', '',   '']     # p2pk
            # else:
                # # print("unknown")
                # self.unknowns.append([txid, b2x(spk)])
            self.type = type
            self.found |= self.type.value
            if self.printed & self.type.value:
                pass
            elif self.type.value:
                self.process(g1, g2, g3, k)
            else:                               #unknown type
                self.process('', '', '', k)

if __name__ == "__main__":
    make_addresses()
    latest = proxy.getblockcount()
    i = -1
    txn = Transaction()
    while True:
        i += 1
        j = -1
        if txn.found == 255: break
        bhash  = proxy.getblockhash(latest - i)
        block  = proxy.getblock(bhash)
        bhash = b2lx(bhash)
        for tx in block.vtx:
            j += 1
            if txn.found == 255: break
            txid = b2lx(tx.GetTxid())
            txn.gettxn(txid)
