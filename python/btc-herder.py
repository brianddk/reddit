#!/usr/bin/env python3
# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/btc-herder.py
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  https://github.com/brianddk/reddit/blob/master/README.md
# [ref]     reddit.com/r/Bitcoin/submit?draft=tbd
# [req]     pip3 install dnspython
# [req]     https://bitcoincore.org/en/download/
# [req]     https://packages.msys2.org/base/openbsd-netcat
# [usage]   python btc-herder.py
# [note]    You must set the following enviroinment variables:
#
#   NC_CLI  - The full path to your 'nc' executable
#   BTC_CLI - The full path to the 'bitcoin-cli' executable
#
# This script will produce '<network>_<n>_nodes.json' files
# You will probably want to change some defines below the imports

from json import loads, load, dumps, dump
from subprocess import run, TimeoutExpired
from time import sleep, time
from random import random, randint, choice
from dns.resolver import query
from sys import exit
from copy import deepcopy
from os.path import isfile
from os import environ

# You will likely want to change some of these
CMD_TIMEOUT = 5
MIN_CONN    = 300 # 5 min
# TESTNET     = True
TESTNET     = False
ABORT_FILE  = "abort.lock"
CMD_RETRY   = 5

# From bitcoin source code and bitnodes.io
ipv4_seeds = dict(
    mainnet = [
        "seed.bitcoin.sipa.be",
        "dnsseed.bluematt.me",
        "dnsseed.bitcoin.dashjr.org",
        "seed.bitcoinstats.com",
        "seed.bitcoin.jonasschnelli.ch",
        "seed.btc.petertodd.org",
        "seed.bitcoin.sprovoost.nl",
        "dnsseed.emzy.de",
        "seed.bitcoin.wiz.biz",
        "seed.bitnodes.io"
    ],
    testnet = [
        "testnet-seed.bitcoin.jonasschnelli.ch",
        "seed.tbtc.petertodd.org",
        "seed.testnet.bitcoin.sprovoost.nl",
        "testnet-seed.bluematt.me"
    ])

# From bitnodes.io
onion_seeds = dict(
    mainnet = ["seed.bitnodes.io"],
    testnet = []
    )

# Bitnodes and some friends, feel free to remove
favorite_nodes = dict(
    mainnet = [
        "88.99.167.175:8333",
        "88.99.167.186:8333",
        "[2a01:4f8:10a:37ee::2]:8333",
        "6zynxbbupfmnvc3g.onion:8333",
        "217.104.4.71:8333"
    ],
    testnet = [
        "88.99.167.175:18333",
        "88.99.167.186:18333",
        "[2a01:4f8:10a:37ee::2]:18333",
        "6zynxbbupfmnvc3g.onion:18333",
        "217.104.4.71:18333"
    ]
    )

def run_cmd(cmd):
    for i in range(0, CMD_RETRY):
        try:
            cp = run(cmd, capture_output=True, text=True, timeout=CMD_TIMEOUT)
            break
        except TimeoutExpired:
            cp = False
    return cp

def testport(addr, port, tor=False):
    wo_proxy = nc_cli + " -v -n -z"
    w_proxy  = nc_cli + " -v -n -z -X 5 -x 127.0.0.1:9050"
    cmd = w_proxy if tor else wo_proxy
    try:
        cp = run(cmd.split(), capture_output=True, text=True, timeout=CMD_TIMEOUT)
        rtn = True
    except TimeoutExpired:
        rtn = False
    return rtn

def getpeerinfo(testnet=TESTNET):
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["getpeerinfo"]
    cp = run_cmd(exe + args + cmd)
    return loads(cp.stdout)

def clearbanned(testnet=TESTNET):
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["clearbanned"]
    cp = run_cmd(exe + args + cmd)

def getaddednodeinfo(testnet=TESTNET):
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["getaddednodeinfo"]
    cp = run_cmd(exe + args + cmd)
    return loads(cp.stdout)

def removeadded(node, testnet=TESTNET):
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["addnode", node, "remove"]
    cp = run_cmd(exe + args + cmd)

def bannode(node, testnet=TESTNET):
    removeadded(node)
    addr = node.split(':')[0]
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["setban", addr, "add"]
    cp = run_cmd(exe + args + cmd)

def addnode(node, testnet=TESTNET):
    exe  = [btc_cli]
    args = ["--testnet"] if testnet else []
    cmd  = ["addnode", node, "add"]
    cp = run_cmd(exe + args + cmd)

def read_json(testnet=TESTNET):
    net = "testnet_" if testnet else "mainnet_"
    with open(net + "nodes.json", 'r') as file:
        nodes = load(file)
    for addr,node in nodes.items():
        node['conntime'] = 0
        node['banned'] = False
        node['added'] = False
        node['tried'] = 0
        nodes[addr] = node
    return nodes

def write_json(nodes, testnet=TESTNET):
    net = "testnet_" if testnet else "mainnet_"
    cntr = glbl_d['cntr']
    cntr = (cntr + 1) % 2
    glbl_d['cntr'] = cntr
    net += str(cntr) + "_"
    with open(net + "nodes.json", 'w') as file:
        dump(nodes, file, indent=4)

def sorter(tup):
    addr, node = tup
    conntime = node.get('conntime', 0)
    if conntime == 0:
        conntime = 0 - random()

        added = node.get('added', False)
        if added:
            conntime -=10

        port = node.get('port', 0)
        if port == 0:
            conntime -= 20

        tried = node.get('tried', 0)
        conntime -= tried

    return conntime

def sortnodes(nodes):
    return {k:v for k,v in sorted(nodes.items(), key=sorter, reverse=True)}

def lognode(addr, entry, nodes):
    if addr in nodes.keys():
        entry['best'] = nodes[addr].get('best', 0)
    nodes[addr] = entry
    nodes=sortnodes(nodes)
    write_json(nodes)
    return nodes

def updategpi(nodes, testnet=TESTNET):
    gpi = getpeerinfo()
    for node in gpi:
        addr,port = node['addr'].split(':')
        if addr == '127.0.0.1':
            continue
        entry = {key: node[key] for key in {'minfeefilter', 'relaytxes', 'conntime', 'inbound'}}
        entry['synced_blocks'] = node.get('synced_blocks', -1)
        if not node['inbound']:
            entry['port'] = port
        nodes = lognode(addr, entry, nodes)
    return nodes

def ban_stale(nodes):
    for addr,node in nodes.items():
        if (
            node.get('port', 0) and
            not node.get('inbound', True) and         # inbound == False
            not node.get('banned', False) and         # banned == False
            MIN_CONN - time() + node['conntime'] < 0
        ):
            port = node['port']
            bannode(f"{addr}:{port}")
            # print("banned", f"{addr}:{port}") # debug
            node['conntime'] = 0
            node['banned'] = True
            nodes[addr] = node

    write_json(nodes)
    return nodes

def seed(nodes, tor=False, testnet=TESTNET):
    key   = 'testnet' if testnet else 'mainnet'
    port  = 18333 if testnet else 8333
    seeds = onion_seeds[key] if tor else ipv4_seeds[key]
    type  = 'TXT' if tor else 'A'
    if seeds:
        # index = randint(0, len(seeds) - 1)
        host = choice(seeds)
        for addr in query(host, type):
            addr = str(addr).replace('"','')
            if addr not in nodes.keys():
                if not testport(addr, port, tor):
                    port = 0
                    node['tried'] = node.get('tried', 0) + 1
                entry = dict(port = port)
                nodes[addr] = entry
                # print(dumps({addr: entry}, indent=4)) # debug

    write_json(nodes)
    return nodes

def seed_ipv4(nodes):
    return seed(nodes, testnet=TESTNET)

def seed_onion(nodes):
    return seed(nodes, True, testnet=TESTNET)

def addnodes(nodes):
    sorted = sortnodes(nodes)
    for addr,node in sorted.items():
        if (
            node.get('port', 0) and
            not node.get('minfeefilter', False) and
            not node.get('conntime', 0) and
            not node.get('added', False)
        ):
            port = node['port']
            addnode(f"{addr}:{port}")
            node['added'] = True
            # print("added", f"{addr}:{port}") # debug
            nodes[addr] = node

def dump_diff(prev, curr): # debug
    # print(len(prev), len(curr)) # debug
    if len(prev) > len(curr):
        for key in prev.keys():
            if key not in curr.keys():
                pass # print(dumps({key:prev[key]}, indent=4)) # debug

def chk_glbl(): # debug
    prev, curr = (glbl['prev']['reachable'], glbl['curr']['reachable'])
    dump_diff(prev, curr)

    prev, curr = (glbl['prev']['relaytxes'], glbl['curr']['relaytxes'])
    dump_diff(prev, curr)

    prev, curr = (glbl['prev']['lowfee'], glbl['curr']['lowfee'])
    dump_diff(prev, curr)

def progress(nodes):
    reachable = relaytxes = lowfee = 0
    glbl['prev'] = deepcopy(glbl['curr']) # debug
    glbl['curr'] = dict(reachable=dict(), relaytxes=dict(), lowfee=dict())
    for addr,node in nodes.items():
        node['best'] = node.get('best', 0)
        if addr in glbl_list:
            pass # print(dumps({addr:node}, indent=4)) # debug
        if node.get('port', 0):
            node['best'] = max(1, node.get('best',0))
            reachable += 1
            glbl['curr']['reachable'][addr] = node
            if (
                not node.get('inbound', True) and
                node.get('synced_blocks', 0) > 0 and
                node.get('relaytxes', False)
            ):
                node['best'] = max(2, node.get('best',0))
                relaytxes += 1
                glbl['curr']['relaytxes'][addr] = node
                if node.get('minfeefilter', 0.00001000) < 0.00001000:
                    # print(dumps({addr: node}, indent=4)) # debug
                    node['best'] = max(3, node.get('best',0))
                    lowfee += 1
                    glbl['curr']['lowfee'][addr] = node

    nodes[addr] = node
    chk_glbl() # debug
    return (len(nodes), reachable, relaytxes, lowfee)

def clearadded():
    added = getaddednodeinfo()
    for item in added:
        node = item['addednode']
        removeadded(node)

def reset_all():
    clearbanned()
    clearadded()
    return dict()

def probeport(nodes, count, testnet=TESTNET):
    port  = 18333 if testnet else 8333
    sorted = sortnodes(nodes)
    for addr,node in sorted.items():
        if (
                not node.get('port', 0) and
                not node.get('conntime', 0)
            ):
            tor = True if 'onion' in addr else False
            if testport(addr, port, tor):
                count -= 1
                node['port'] = port
                # print("retry success") # debug
                # print(dumps({addr:node}, indent=4)) # debug
                glbl_list.append(addr)
            else:
                node['tried'] = node.get('tried', 0) + 1
                # print("retry failure") # debug
            nodes[addr] = node

        if count == 0:
            break

def restore_favorites(testnet=TESTNET):
    key   = 'testnet' if testnet else 'mainnet'
    for node in favorite_nodes[key]:
        addnode(node)

def get_environ():
    if (
        'NC_CLI' in environ.keys() and
        'BTC_CLI' in environ.keys()
    ):
        nc_cli  = environ['NC_CLI']
        btc_cli = environ['BTC_CLI']
        return (nc_cli, btc_cli)
    else:
        print("Read the source Luke!  You must set BTC_CLI and NC_CLI enviroinment variables")
        exit(1)

nc_cli, btc_cli = get_environ()
glbl_d = dict(cntr = 0)
glbl_list = list()
glbl = dict(curr = dict(reachable=dict(), relaytxes=dict(), lowfee=dict()))
# nodes = read_json()
nodes = reset_all()
# exit()
start = time()
cur_prog = (0, 0, 0, 0)
noadd = 0
fnf = True
try:
    while fnf and noadd < 60:
        last_prog = cur_prog
        nodes = updategpi(nodes)
        nodes = ban_stale(nodes)
        count = len(nodes)
        nodes = seed_ipv4(nodes)
        delta = len(nodes) - count
        if delta > 0:
            addnodes(nodes)
        cur_prog = progress(nodes)
        if(cur_prog > last_prog):
            noadd = 0
        else:
            noadd += 1
        secs = round(time() - start)
        print(noadd, cur_prog, secs)
        if noadd > 0:
            probeport(nodes, noadd)
        if noadd > 3:
            nodes = seed_onion(nodes)
        sac = choice(list(nodes.keys()))
        write_json(nodes)
        fnf = not isfile(ABORT_FILE)
        sleep(noadd+1)

except Exception as e:
    print(e)
finally:
    write_json(nodes)
    reset_all()
    restore_favorites()
