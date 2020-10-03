This is a guide to using your Trezor with Bitcoin Core.  It may seem like more trouble than it's worth but many applications use Bitcoin Core as a wallet such as LND, EPS, and JoinMarket.  Learning how to integrate your Trezor into a Bitcoin Core install is rather useful in many unexpected ways.  I did this all through the QT interfaces, but it's simple to script.  There is a much simpler guide available from the [HWI github](https://github.com/bitcoin-core/HWI/blob/master/docs/bitcoin-core-usage.md), and the smallest [Linux TLDR is here](https://www.reddit.com/r/Bitcoin/comments/izmi2w/windows_linux_guide_to_using_trezor_with_bitcoin/g6jqgxq/)

Unfortunately, I don't have access to a Coldcard or Ledger.  I'm not sure how the `setpin` or `-stdinpass` parameters are handled on that HW.

## ( A ) Install TrezorCTL, HWI, and build GUI

You only need to set the wallet up once, but may repeat to upgrade

### ( A.I ) Download extract and install HWI

1. Download and isntall [Python](https://www.python.org/downloads/)
1. Download https://github.com/bitcoin-core/HWI/archive/1.1.2.zip
2. Extract it to a working folder (assumes `C:\User\Reddit\src\HWI`)
4. Change Directory (`cd`) to working folder `cd "C:\User\Reddit\src\HWI"`
4. Setup venv `python -m venv .venv`
5. Enter venv `.venv\Scripts\activate.bat` <sup>1</sup>
6. Install dependencies `python -m pip install -U setuptools pip wheel`
7. Install TrezorCTL `python -m pip install trezor[hidapi]`
8. Install HWI `python -m pip install hwi pyside2`
9. Download `github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.7z`
9. Extract `MS64\dll\libusb-1.0.dll` from the archive
9. Copy to pywin `copy libusb-1.0.dll .venv\Lib\site-packages\pywin32_system32\`

### ( A.II ) Build the QT UI files

1. Download and install [MSYS2](https://www.msys2.org/#installation)
2. Launch a `mingw64.exe` shell
4. CD to working folder `cd "C:\User\Reddit\src\HWI"`
5. Enter venv `source .venv/Scripts/activate` <sup>1</sup>
6. Run UI build `bash contrib/generate-ui.sh`

***

## ( B ) Create a Trezor wallet in Bitcoin Core (testnet)

You only need to set the wallet up once, no private key data is stored, only `xpub` data

### ( B.I ) Retrieve keypool from HWI-QT

1. Launch `hwi-qt.exe --testnet` (assuming testnet)
2. Click `Set passphrase` (if needed) to cache your passphrase then click `Refresh`
3. Select you trezor from the list then click `Set Pin` (if needed)
4. Ensure your Trezor in the dropdown has a fingerprint
5. Select `Change keypool options` and choose `P2WPKH`
6. Copy all the text from the `Keypool` textbox

### ( B.II ) Create the wallet in Bitcoin QT

1. Launch Bitcoin Core (testnet) (non-pruned) <sup>2</sup>
2. Select `Console` from the `Window` menu
3. Create a wallet `createwallet "hwi" true`
4. Ensure that `hwi` is selected in the console wallet dropdown
5. Verify `walletname` using the `getwalletinfo` command
6. Import keypool `importmulti '<keypool_text_from_B.I.6>'` (note `'` caging)
7. Rescan if TXNs are missing `rescanblockchain <starting_block_num>` <sup>3</sup>

***

## ( C.I ) Grab Tesnet coins

1. Select the `Receive` tab in Bitcoin Core (testnet)
2. Ensure that the `Wallet` dropdown has `hwi` selected
3. Select `Create new receiving address` and copy address
4. Google "bitcoin testnet faucet" and visit a few sites
5. Answer captcha and input your addressed copied from C.I.3

***

## ( D ) Spending funds with HWI

This is how you can spend funds in your Trezor using Bitcoin Core (testnet)

### ( D.I ) Create an unsigned PSBT

1. Select the `Send` tab in Bitcoin Core (testnet)
2. Ensure that the `Wallet` dropdown has `hwi` selected
3. Verify your balance in `Watch-only balance`
4. Rescan if balance is wrong (see B.II.7) <sup>3</sup>
5. Craft your TXN as usual, then click `Create Unsigned`
6. Copy the PSBT to your clipboard when prompted

### ( D.II ) Sign your PSBT

1. In HWI-QT click `Sign PSBT`
2. Paste what you copied in D.I.6 in `PSBT to Sign` field
3. Click `Sign PSBT`
4. Copy the text for `PSBT Result`

### ( D.III ) Broadcast your TXN

1. Select the `Console` window in Bitcoin Core (testnet)
2. Ensure that the `Wallet` dropdown has `hwi` selected
3. Finalize PSBT: `finalizepsbt <psbt_copied_from_D.II.4>`
4. Copy the signed TXN hex from the `hex` field returned
5. Broadcast TXN: `sendrawtransaction <txn_copied_from_D.III.4>`

***

## Final Thoughts

I did this all through the GUI interfaces for the benefit of the Windows users.  Windows console is fine, but the quote escaping in windows console is nightmarish.  Powershell would be good, but that throws this on a whole another level for most Windows folks.

There is also the need to use HWI-QT due to a bug in blank passphrases on the commandline.  You can work around it by toggling passphrase off or on, but again, it's more than I wanted to spell out.

***

<sup>Footnotes:</sup>

* <sup>1. - Later version of python put the activate script under 'bin' instead of 'Script'</sup>
* <sup>2. - You can run pruned, but you need to have a fresh wallet</sup>
* <sup>3. - Rescan is automatic on 'importmulti' but I was pruned so it was wierd</sup>
