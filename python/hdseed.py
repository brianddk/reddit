#!/usr/bin/env python3
# [rights]  Copyright 2021 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/hdseed.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [req]     python -m pip install electrum
# [note]    To run in electrum console, correct file path and run:
#    with open(r"C:\Windows\Temp\hdseed.py") as f: exec(f.read())

# ignore BIP45 and BIP48 MS-wallets

from mnemonic import Mnemonic as BIP39
from electrum.bitcoin import serialize_privkey as to_wif
from electrum.bitcoin import deserialize_privkey as from_wif
from electrum.bip32 import BIP32Node
from electrum import constants
from json import dumps
from sys import argv
hexdigits = '0123456789abcdefABCDEF'

def main():

    seed = globals().get('seed', None)
    if 'wallet' not in globals():
        # Not in electrum console, free to toggle network
        constants.set_testnet()
        if len(argv) > 1:
            seed = argv[1]

    if(constants.net.TESTNET):
            
        bip = {}
        (mnemo, tprv, gwif) = [None] * 3

        if seed:
            (tmp, seed) = (seed, None)
            if '0x' == tmp[:2].lower(): 
                tmp = tmp[2:]
            if set(tmp).issubset(hexdigits) and 64 == len(tmp):
                seed = bytes.fromhex(tmp)
                gwif = to_wif(seed,True,'p2pkh').split(':')[-1] # to_wif(seed,True,'').split(':')[-1]
            elif 'tprv' == tmp[:4]:
                tprv = tmp
            elif 12 == len(tmp.split()):
                mnemo = tmp
            else:
                gwif = tmp
                _, seed, _ = from_wif(tmp)
                
        bip39  = BIP39("English")
        if not (seed or mnemo or gwif or tprv):
            mnemo  = bip39.generate()
        if mnemo:
            seed = bip39.to_seed(mnemo)
        if tprv:
            bip32  = BIP32Node.from_xkey(tprv)
        if seed:
            bip32  = BIP32Node.from_rootseed(seed, xtype='standard')
            tprv   = bip32.to_xprv()
                        
        desc = {'44':['pkh'],'49':['wpkh','sh'],'84':['wpkh'],'86':['tr']}
        conf = {'44':'legacy','49':'p2sh-segwit','84':'bech32','86':'bech32m'}
        for k in desc.keys():
            imp  = {'timestamp':'now','range':[0,1000],'next_index':1}
            imp  = [dict(imp), dict(imp)]
            acct = f"{k}'/1'/0'"
            if gwif:
                key = seed
                wif = gwif
            else:
                key  = bip32.subkey_at_private_derivation(f"m/{acct}/0/0").eckey.get_secret_bytes()
                wif  = to_wif(key,True,'p2pkh').split(':')[-1]
            bip[k] = {}
            bip[k]['key'] = key.hex()
            bip[k]['wif'] = wif
            change = 0
            for j in ['addr', 'change']:
                path      = f"{acct}/{change}"
                desc_str  = f"{tprv}/{path}/*"
                for i in desc[k]:
                    desc_str = f"{i}({desc_str})"
                desc_str  = descsum_create(desc_str)     
                imp[change]['desc'] = desc_str
                imp[change]['internal'] = bool(change)
                imp[change]['active'] = not bool(change)                
                bip[k][j] = {}
                bip[k][j]['derivation'] = path
                bip[k][j]['desc'] = desc_str
                bip[k][j]['import'] = 'importdescriptors ' + dumps(imp[change]).replace('"', r'\"')
                change += 1
            imp_txt = dumps(imp).replace('"', r'\"')
            if '86' == k:
                cmd = ''
            else:
                cmd =  f'createwallet "bip{k}-berkley" false true\n'
                cmd += f'sethdseed true "{wif}"\n'            
            cmd += f'createwallet "bip{k}-sqlite"  false true "" false true\n'
            cmd += f'importdescriptors "{imp_txt}"'            
            bip[k]['import'] = imp_txt
            bip[k]['commands'] = cmd
                    
        print(f'\n# Your BIP39 Mnemonic:    "{mnemo}"')
        print(  f'# Your BIP32 Root Key:    "{tprv}"')
        print(f'\n# Your legacy hdseed      wif:"{bip["44"]["wif"]}", priv:"{bip["44"]["key"]}"')
        print(  f'# Your p2sh-segwit hdseed wif:"{bip["49"]["wif"]}", priv:"{bip["49"]["key"]}"')
        print(  f'# Your bech32 hdseed      wif:"{bip["84"]["wif"]}", priv:"{bip["84"]["key"]}"\n')
        
        for k in desc.keys():
            print(f'##################################################')
            print(f'# Your BIP{k} config is:\ntest.addresstype={conf[k]}\ntest.changetype={conf[k]}\n')
            print(f'# Your BIP{k} commands are:\n{bip[k]["commands"]}\n')
        
    else:
        print("You are not on Testnet, Exiting for safety")

        
INPUT_CHARSET = "0123456789()[],'/*abcdefgh@:$%{}IJKLMNOPQRSTUVWXYZ&+-.;<=>?!^_|~ijklmnopqrstuvwxyzABCDEFGH`#\"\\ "
CHECKSUM_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
GENERATOR = [0xf5dee51989, 0xa9fdca3312, 0x1bab10e32d, 0x3706b1677a, 0x644d626ffd]

def descsum_polymod(symbols):
    """Internal function that computes the descriptor checksum."""
    chk = 1
    for value in symbols:
        top = chk >> 35
        chk = (chk & 0x7ffffffff) << 5 ^ value
        for i in range(5):
            chk ^= GENERATOR[i] if ((top >> i) & 1) else 0
    return chk

def descsum_expand(s):
    """Internal function that does the character to symbol expansion"""
    groups = []
    symbols = []
    for c in s:
        if not c in INPUT_CHARSET:
            return None
        v = INPUT_CHARSET.find(c)
        symbols.append(v & 31)
        groups.append(v >> 5)
        if len(groups) == 3:
            symbols.append(groups[0] * 9 + groups[1] * 3 + groups[2])
            groups = []
    if len(groups) == 1:
        symbols.append(groups[0])
    elif len(groups) == 2:
        symbols.append(groups[0] * 3 + groups[1])
    return symbols

def descsum_create(s):
    """Add a checksum to a descriptor without"""
    symbols = descsum_expand(s) + [0, 0, 0, 0, 0, 0, 0, 0]
    checksum = descsum_polymod(symbols) ^ 1
    return s + '#' + ''.join(CHECKSUM_CHARSET[(checksum >> (5 * (7 - i))) & 31] for i in range(8))

main()
