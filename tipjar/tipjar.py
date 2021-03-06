#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/tipjar/tipjar.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

from requests import Request, Session
from re import findall
from time import sleep
from json import dumps
from os import isatty
from sys import stdin

session = Session()
cache = {}
def get_bal(coin, showdust = False):
    uri = coin['uri'].format(**coin)
    coin['_addr'] = coin['addr'].lower()
    key = coin['key'].format(**coin)
    if uri not in cache.keys():
        # sleep(1/7)
        prep = Request('GET', uri).prepare()
        prep.headers.clear() # etherscan hates headers
        r = session.send(prep)
        if not r.ok:
            return r
        cache[uri] = r.json()
    j = cache[uri]
    for node in key.split('.'):
        if '*' in node:
            _, key, test = node.split(':')
            for node in j:
                if node[key] == test:
                    j = node
                    break
        elif '#' in node:
            _, i = node.split('#')
            j = j[int(i)]
        else:
            j = j[node]
    coin['dust'] = 0 if showdust else coin['dust']
    return float(j) / coin['div'] - coin['dust']

tipjar = dict(
    btc = dict(
        addr = "bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj,3AAzK4Xbu8PTM8AD3fDnmjdNkXkmu6PS7R,18MDTTiqPM8ZEo29Cig1wfGdkLNtvyorW5",
        uri  = "https://api.blockchair.com/bitcoin/dashboards/addresses/{addr}",
        key  = "data.set.balance",
        dust = 0,
        div  = 10**8
    ),
    tbtc_44 = dict(
        addr = "mpaMBuoJ7ZiiJhmRZVvDT3JPncZV7XTeyy",
        uri  = "https://tbtc2.trezor.io/api/address/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    ftc = dict(
        addr = "6mx5WVXsTEdsh9UCainpdAHDrDwH4mZQTD",
        uri  = "https://explorer.feathercoin.com/api/addr/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    tltc_44 = dict(
        addr = "mpaMBuoJ7ZiiJhmRZVvDT3JPncZV7XTeyy",
        uri  = "https://testnet.litecore.io/api/addr/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    bch = dict(
        addr = "qqz77k4rqar3uppj8k28de06narwkqaamcf624p8zl",
        uri  = "https://api.blockchair.com/bitcoin-cash/dashboards/addresses/{addr}",
        key  = "data.set.balance",
        dust = 0,
        div  = 10**8
    ),
    tbtc_49 = dict(
        addr = "2N1bhQ2Cp8QKt88ds9udWE1TGX89cebNMRW",
        uri  = "https://tbtc1.trezor.io/api/address/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    xrp = dict(
        addr = "rEXJQNj9frFgG3Wk3smqGFVdMUX53c7Fw4",
        uri  = "https://api.xrpscan.com/api/v1/account/{addr}",
        key  = "xrpBalance",
        dust = 40.0,
        div  = 1
    ),
    # xrp = dict(
        # addr = "rEXJQNj9frFgG3Wk3smqGFVdMUX53c7Fw4",
        # uri  = "https://api.blockchair.com/ripple/raw/account/{addr}",
        # key  = "data.{addr}.account.account_data.Balance",
        # dust = 0,
        # div  = 10**6
    # ),
    tbch = dict(
        addr = "bchtest:qp346ld04gnll2n3u2zr2uvy8slrpkagvvy7rdrmev",
        conv = "mpaMBuoJ7ZiiJhmRZVvDT3JPncZV7XTeyy",
        uri  = "https://explorer.bitcoin.com/api/tbch/addr/{conv}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    ltc = dict(
        addr = "ltc1q5uucgx9f8n70nq7jmjy03rpg84cm4tm70z5rz6,MKcAge42cX6WZnnPfFGJAxReUYZUbsi6t3,LQjSwZLigtgqHA3rE14yeRNbNNY2r3tXcA",
        uri  = "https://api.blockchair.com/litecoin/dashboards/addresses/{addr}",
        key  = "data.set.balance",
        dust = 0,
        div  = 10**8
    ),
    tltc_49 = dict(
        addr = "QUxTX3549WNyGKPun1fXJhthfWbSSKWxaL",
        uri  = "https://testnet.litecore.io/api/addr/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    eth = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b",
        uri   = "https://api.blockchair.com/ethereum/dashboards/address/{addr}?erc_20=true",
        key   = "data.{_addr}.address.balance",
        dust  = 0.00947497,
        div   = 10**18
    ),
    tbtc_84 = dict(
        addr = "tb1qr3lzhp555lzxecjrae2vsl7mtnherxnau5tfe5",
        uri  = "https://tbtc2.trezor.io/api/address/{addr}",
        key  = "balance",
        dust = 0,
        div  = 1
    ),
    amb = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b",
        uri   = "https://api.blockchair.com/ethereum/dashboards/address/{addr}?erc_20=true",
        key   = "data.{_addr}.layer_2.erc_20.*:token_symbol:AMB.balance_approximate",
        dust  = 0.1,
        div   = 1
    ),
    dai = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b",
        uri   = "https://api.blockchair.com/ethereum/dashboards/address/{addr}?erc_20=true",
        key   = "data.{_addr}.layer_2.erc_20.*:token_symbol:DAI.balance_approximate",
        dust  = 0,
        div   = 1
    ),
    bat = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b",
        uri   = "https://api.blockchair.com/ethereum/dashboards/address/{addr}?erc_20=true",
        key   = "data.{_addr}.layer_2.erc_20.*:token_symbol:BAT.balance_approximate",
        dust  = 0,
        div   = 1
    ),
    rob_60_0 = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b,0xF7A1009746850D1581AB8b4A87bf5810775925fe",
        uri   = "https://api-ropsten.etherscan.io/api?module=account&action=balancemulti&address={addr}&tag=latest&apikey={apikey}",
        key   = "result.#0.balance",
        dust  = 1,
        div   = 10**18
    ),
    rob_60_1 = dict(
        addr  = "0xBc72A79357Ff7A59265725ECB1A9bFa59330DB4b,0xF7A1009746850D1581AB8b4A87bf5810775925fe",
        uri   = "https://api-ropsten.etherscan.io/api?module=account&action=balancemulti&address={addr}&tag=latest&apikey={apikey}",
        key   = "result.#1.balance",
        dust  = 0,
        div   = 10**18
    ),
    xlm = dict(
        addr = "GDXJRFK4IO3EMOITZSHE7B2HHLR3RSDRBYF2P2PDQ6AKGZNFVALC2PEO",
        uri  = "https://horizon.stellar.org/accounts/{addr}",
        key  = "balances.*:asset_type:native.balance",
        dust = 3.00096,
        div  = 1
    ),
)

if isatty(stdin.fileno()):
    apikey = False
else:
    apikey = stdin.read().strip()

# DEBUG = True
DEBUG = False

for coin in tipjar.keys():
    if 'apikey' in tipjar[coin]['uri']:
        if apikey:
            tipjar[coin].update(apikey = apikey)
        else:
            continue
    bal  = get_bal(tipjar[coin], showdust = DEBUG)
    addr = tipjar[coin]['addr']
    lbl  = coin.split('_')[0]
    if bal or DEBUG: print(f"{lbl:8}: {bal:,.8f} {addr}")

"""
-----BEGIN PGP MESSAGE-----
Version: GnuPG v2
Comment: gpg2 --decrypt < tipjar.py 2>NUL | tipjar.py

hQEMAxknaFN8ZgFHAQf/cUh/rEF1LgmJO8nS0wQtca1SU0LLElbkd2saxSw8nFaZ
FqKeQMgCdZO65wSpSJp+LrzZaOOAFeHEgJoFlhU042Q/Im2bSWcYRW3dGOJn1GET
Y1VS0plr8D3Fe4mA0PCrPRd5qN7POi9YEbWU6bFUtcLXN2/Ynk8sa/fn8kLEFDkx
XXaK+hSghUuCcjrjBo+gV37iibtCO6PAIAA6Ay7HqGduln1IkiJ+0LQ2RC1sE6SI
V1FPl6LommliCyuksygwCfFkG7P6RtWLrvPcC/13UYBFJSE77XR7ainqeekwW8m6
8VRcoFQYVOibXJo77Mk5KI/lrL6fch3PuMgIfOlFFdJfAZUCH4TQx72rGBt5d0g3
ra+DxLAlQRadY1Gy8QiC87Ek5ehcANw1CNSRDHsuZjn6fSueRZH8NX0ZKiVh270I
8woKA3QC4lqRW8seymWDpaa30ASgtYBjv9t6kmvamSA=
=D6nY
-----END PGP MESSAGE-----
"""
