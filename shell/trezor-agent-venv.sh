#!/bin/bash
# [rights]  Copyright 2022 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/shell/trezor-agent-venv.sh
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/r/TREZOR/comments/rqxuh0/-/hr629qp/

venv="trezor-agent.venv"
pkgs="python3-venv python3-dev python3-tk libusb-1.0-0-dev libudev-dev"

export http_proxy="socks5://127.0.0.1:9050"
export https_proxy="socks5://127.0.0.1:9050"
export no_proxy="localhost,127.0.0.1"

function sudo_apt()
{
  apt-get update
  apt-get install $*
}

for i in $pkgs
do
  if ! dpkg -S $i 1>/dev/null 2>&1
  then
    sudo bash -c "$(declare -f sudo_apt); sudo_apt $pkgs" || exit 1
    break
  fi
done

python3 -m venv $venv
pushd ./$venv/lib/python3*/site-packages/
cp -a /usr/lib/python3/dist-packages/* .
popd
source ./$venv/bin/activate
python3 -m pip --proxy socks5:127.0.0.1:9050 install --upgrade pip setuptools wheel
python3 -m pip --proxy socks5:127.0.0.1:9050 install Cython hidapi
python3 -m pip --proxy socks5:127.0.0.1:9050 install --upgrade trezor[hidapi]==0.12.2 trezor_agent==0.11.0
