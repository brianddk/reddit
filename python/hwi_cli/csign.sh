#!/bin/bash
# [rights]  Copyright 2020 brianddk at github https:# github.com/brianddk
# [license] Apache 2.0 License https:# www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/python/hwi_cli/csign.sh
# [ref]     reddit.com/r/TREZOR/comments/j4lp9g/
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt

source <(gpg2 -dq environ.asc)
# source ... (python venv)
# btc_cli=... (path to bitcoin-cli)
# cfarg=... (bitcoin-cli conf file arg)
# wtarg=... (wallet file arg)
# fpr=... (keypool fingerprint

ins="$(grep -v "^//" inputs.json | tr -d '\n' | sed 's/ //g')"
outs="$(grep -v "^//" outputs.json | tr -d '\n' | sed 's/ //g')"
# pool="$(cat pool.json | tr -d '\n' | sed 's/ //g')"

# createpsbt
psbt="$("$btc_cli" "$cfarg" "createpsbt" "$ins" "$outs")"

# walletprocesspsbt
psbt="$("$btc_cli" $wtarg "walletprocesspsbt" "$psbt")"
psbt="$(<<< "$psbt" grep 'psbt' | sed 's/"psbt"://;s/[", ]//g')"

# sign psbt
psbt="$(hwi --testnet -f "$fpr" signtx "$psbt")"
psbt="$(<<< "$psbt" sed 's/"psbt"://;s/[",{} ]//g')"

# finalize psbt
stxn="$("$btc_cli" $wtarg "finalizepsbt" "$psbt")"
stxn="$(<<< "$stxn" grep 'hex' | sed 's/"hex"://;s/[", ]//g')"

deactivate

echo "$stxn"
