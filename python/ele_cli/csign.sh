#!/bin/bash
# [rights]  Copyright 2020 brianddk at github https:# github.com/brianddk
# [license] Apache 2.0 License https:# www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/ele_cli/csign.sh
# [ref]     reddit.com/r/TREZOR/comments/j4lp9g/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

source <(gpg2 -dq environ.asc)
# source ... (python venv)
# wallet=... (path to wallet)
# electrum=... (path to electrum)
tnarg="--testnet"
wtarg="$tnarg --wallet $wallet"
jtxn="$(grep -v "^//" txn.json | tr -d '\n' | sed 's/ //g')"

psbt="$($electrum serialize $jtxn $tnarg)"
stxn="$($electrum signtransaction $psbt $wtarg)"
deactivate
echo "$stxn"