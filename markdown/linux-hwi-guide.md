Linux / TLDR;

Install HWI

1. `sudo apt install libusb-1.0-0-dev libudev-dev python3-dev`
1. extract `github.com/bitcoin-core/HWI/archive/1.1.2.zip[*]` to `hwi`
2. `cd hwi; python -m venv .venv; source .venv\bin\activate`
3. `python -m pip install -U setuptools pip wheel`
4. `python -m pip install trezor[hidapi] hwi`

Create Wallet

1. `hwi enumerate`
7. `hwi -d <path_from_enum> -t trezor promptpin`
8. `hwi -d <path_from_enum> -t trezor sendpin <pin_from_numpad>`
9. `hwi --stdinpass -d <path_from_enum> enumerate`
10. `hwi --testnet --stdinpass -f <fpr_from_enum> getkeypool --wpkh 0 1000`
11. `bitcoin-cli -testnet createwallet hwi true`
12. `bitcoin-cli -testnet -rpcwallet=hwi importmulti <json_from_gkp>`
13. `bitcoin-cli -testnet -rpcwallet=hwi rescanblockchain`

Spend from Wallet

1. `bitcoin-cli -testnet -rpcwallet=hwi walletcreatefundedpsbt ...`
1. `hwi --testnet --stdinpass -f <fpr_from_enum> signtx <PSBT_from_prev>`
2. `bitcoin-cli -testnet -rpcwallet=hwi finalizepsbt <PBST_from_prev>`
3. `bitcoin-cli -testnet sendrawtransaction  <TXN_from_prev>`
