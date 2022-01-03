#!/bin/bash
# [rights]  Copyright 2022 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    github.com/brianddk/reddit/blob/master/shell/trezor-suite.sh
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
# [ref]     https://www.reddit.com/r/TREZOR/comments/ruqzjd/

export http_proxy="socks5://127.0.0.1:9050"
export https_proxy="socks5://127.0.0.1:9050"
export no_proxy="localhost,127.0.0.1"
file="Trezor-Suite-21.12.2-linux-x86_64.AppImage"

function ip_tables()
{
  iptables -I OUTPUT -p tcp --dport 21325 -j ACCEPT -s localhost -d localhost
  iptables -I INPUT -p tcp --dport 21325 -j ACCEPT -s localhost -d localhost
}

function get_files()
{
  file="$1"
  wget "https://suite.trezor.io/web/static/desktop/${file}.asc"
  wget "https://trezor.io/security/satoshilabs-2021-signing-key.asc"
  gpg --import satoshilabs-2021-signing-key.asc
  printf "trust\n5\ny\nquit\n" | gpg --command-fd 0 --edit-key "0xeb483b26b078a4aa1b6f425ee21b6950a2ecb65c"
  wget "https://suite.trezor.io/web/static/desktop/${file}"
  chmod +x "${file}"
}

if [[ ! -f "$file" ]]; then
  sudo -u amnesia bash -c "$(declare -f get_files); get_files $file" || exit 1
fi
sudo -u amnesia gpg --verify "${file}.asc" "${file}" || exit 2
if ! curl -f http://127.0.0.1:21325/ 1> /dev/null 2>&1; then
  sudo bash -c "$(declare -f ip_tables); ip_tables" || exit 3
fi
sudo -u amnesia "${PWD}/${file}"
