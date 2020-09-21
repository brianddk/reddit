Feel free to stop at ***Level 0*** or ***Level 1***, which is fine.  More advanced configs are offered to those with more tech savvy.  BTW, the "For Dummies" is a callback to a set of "tech" books in the 90's intended to be as easy as possible.  It is in jest and not intended to insult the reader.  Finally, if you dislike the formatting, a well formatted copy can be [found here](https://github.com/brianddk/reddit/blob/master/markdown/fullnode_for_dummies.md)

***

There is a fairly small subset of r/Bitcoin users that run a full node.  I think the idea of running a full node has gotten a bad rap over the years since there is so much talk about running on a Raspberry Pi, or getting zippy SSDs.  Although all of this can be fun, it is often not really required at all.  Here are some ways to run a full node starting with the very simple.  I'll get into more complex configs, but these are all optional.

### Tech Skill Level: 0 (the basics)

1. [Download Bitcoin Core](https://bitcoincore.org/en/download/)
2. Launch the downloaded installer and install the app
9. Launch the installed "Bitcoin Core" app and let it run overnight

In many cases, thats it.  If your running a new machine with a fairly good internet connection, 8 or 9 hours will be enough to complete the "Initial Block Download" (IBD).  This may fill up your drive a bit, but again, on most new machines, 300 GB of space isn't that hard to come by.

### Tech Skill Level: 1 (encrypted wallet)

One thing we left out in the level-0 exercise is encrypting your wallet.  It's easy enough to do well, but a bit more difficult to do right.  The main challenge is that humans generate really poor passwords.  If you want a good password, the best way is to use something called "diceware".  Basically, you just grab 4 or 5 dice and each throw of the dice represents a certain word on a special list.  The throw `{1,4,5,3,1}` for example would be the word `camping` on the [EFF-diceware-wordlist](https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt).  So you repeat this a few times until you have a list of 8 or so words which becomes the passphrase you use to encrypt your wallet.  ***Write it down***, it is always hard to remember at first.  So at level-1 your list becomes:

1. [Download Bitcoin Core](https://bitcoincore.org/en/download/)
2. Launch the downloaded installer and install the app
9. Launch the installed "Bitcoin Core" app and let it run overnight
4. Choose `Encrypt Wallet` from the `Settings Menu`
5. Enter your 8 word (or so) passphrase generated using the Diceware method

![Wallet Encryption Dialog](/assets/encrypt.png)

### Tech Skill Level: 2 (enable pruning if needed)

Though I said "300 GB of space isn't hard to come by", some times it actually is.  If space is an issue, a simple way to fix it is to tell bitcoin to simple take less space.  This is called "pruning" and can take that number from 300 GB down to below 5 GB.  If you can't find 5 GB, then you'll have to read ahead to level-4 to add USB storage.  But the good news is, enabling pruning is pretty easy, we just add another step to our working list:

1. [Download Bitcoin Core](https://bitcoincore.org/en/download/)
2. Launch the downloaded installer and install the app
9. Launch the installed "Bitcoin Core" app and let it run overnight
4. Do the wallet encryption steps here if you wish
5. Choose `Options` from the `Settings Menu`
6. Choose `Prune block storage to:` and select the max size for the blocks to use
7. Exit and restart the bitcoin application for the changes to take effect

![Pruning Dialog](/assets/prune.png)

Note, even setting this to 1 GB will still leave you with about a 4.5 GB install.  The blocks take up a lot of space, but the `chainstate` and other folders eat up at least 3.5 GB and they can't be pruned.  Also, be aware, to disable pruning requires you to perform the entire IBD again.  While pruned some other functions my be disabled as well, so just know that pruning does limit some functionality.

### Tech Skill Level: 3 (verify the installer)

Although this is arguably something that should be done at level-0, some find the intricacies of comparing hash (thumbprint) values to be tedious and beyond the scope of a beginner.  You will find these types of hash compares suggested quite often as a way to prevent running tainted programs.  Programs are often tainted by bad disk or network performance, but most often, taint is malicious code inserted by viruses or malware.  This is a way to guard yourself against those types of attacks.

What I cover here is a very basic comparison on the certificate, but a [more thorough verification](https://bitcoincore.org/en/download/#verify-your-download) advised by mosts uses a program called [Gpg4Win](https://www.gpg4win.org/), and is beyond the scope of this beginners guide.  But regardless, most users should strive to do this minimum level of validation.

1. [Download Bitcoin Core](https://bitcoincore.org/en/download/)
2. Launch the downloaded installer
3. When prompted "Do you want to allow..." click `Show more details`
4. In the details section select `Show information about the publisher's certificate`
5. In the certificate window select the `Details` tab
6. In the `Details` tab `Subject` should start with "CN = Bitcoin Core Code Signing Association"
7. Also ensure `Thumbprint` reads `ea27d3cefb3eb715ed214176a5d027e01ba1ee86`
8. If the checks pass, click `OK` to exit the certificate window and `Yes` to allow the installer to run.
9. Launch the installed "Bitcoin Core" app and let it run overnight
10. Do the wallet encryption steps here if you wish
11. Do the optional pruning steps here if you wish

![Certification Validation Windows](/assets/uac.png)

Note: The certificate used to sign the current Bitcoin installer is only valid from March 2020 to March 2021.  After that point the thumbprint on the certificate will change.  This is by design and intentional.  If your reading this post after March 2021, then it is understood that the thumbprint has changed.

### Tech Skill Level: 4 (use secondary storage)

We glossed over the "new machine with fairly good internet" part.  Truth be known many people do not have fairly new machines, and find the IBD to take longer than the "over night" best wishes.  For most people the slowdown is the disk access when calculating what is called `chainstate`.  This requires fast random reads and writes to the disk.  If you have an SSD disk, this will be no problem, but if you have a non-SSD "spinning" disk, random writes are always slow.  Though an SSD will speed things up, they are pricey, so a nice middle ground may be a simple high-end USB key drive.  You can get some with 10 to 15 MB/s random writes which is usually a order of magnitude faster than a "spinning" disk.  And with pruning (see level-2), a small USB drive should be fine.

Once you decide on a drive, the tricky part will be to enable external storage.  It requires editing a configuration file and adding a few lines.  The configuration file needs to be in both the default directory, and USB key drive, but before we do that, we want to create a directory on the key drive.  You will need to determine the drive letter of your USB key drive.  For the sake of this example, we will assume it is `D:`, but you ***must determine this yourself and correct the example***.  Once you know the drive letter, create a blank folder on the drive called `Bitcoin`.  So for this example, creating `Bitcoin` on drive `D:` will create the path `D:\Bitcoin`.  Once done, assuming that `D:` is your drive, here are the steps to edit the two configuration files:

1. [Download Bitcoin Core](https://bitcoincore.org/en/download/)
2. Launch the installer, verify it, then run it
3. Launch the installed "Bitcoin Core" app and let it run overnight
4. Do the wallet encryption steps here if you wish
5. Do the optional pruning steps here if you wish
6. Launch "Notepad" by typing "Notepad.exe" in the windows search bar then click `Open`
7. Type the line `datadir=D:\Bitcoin` (depending on your drive letter) in the blank file
8. Choose `Save` from the `File` menu in notepad
9. Type `%APPDATA%\Bitcoin\bitcoin.conf` (note the percent signs) in the `File name` box
10. Select `All Files` from the `Save as type` dropdown
11. Click the `Save` button and overwrite the file if prompted
12. Exit and restart the bitcoin application for the changes to take effect

![Save As Dialog](/assets/usb.png)

Now that you've reached this level of technical expertise, there are many new configuration options that you can begin to modify if you wish.  Most configuration data is contained in the `bitcoin.conf` file and learning how to maintain it is a key step for a node operator.

### Tech Skill Level: 5 (all other customizations)

Here's a short list of various things you can ***ADD*** to your `bitcoin.conf` file.  You generally just add a new line for each configuration settings.

* `addresstype=bech32`
* `changetype=bech32`

The `addresstype` / `changetype` allows your wallet to use the native-segwit (bech32) format.  This is the most efficient and inexpensive way to spend bitcoin, and is a recommended configuration.  The default uses something called `p2sh-segwit` which is more compatible with older wallets, but more expensive to spend.

* `minrelaytxfee=0.00000011`

Changing the `minrelaytxfee` setting allows you to help propagate lower fee transactions.  It will require more memory but TXN memory is capped at 300 MB by default anyways, so if you have enough memory, it is a good setting to choose.

* `dbcache=2048`

The `dbcache` setting controls how many MB of memory the program will use for the chainstate database.  Since this is a key bottleneck in the IBD, setting this value high (2048 MB) will greatly speed up the IBD, assuming you have the memory to spare

* `blocksdir=C:\Bitcoin`
* `datadir=D:\Bitcoin`

In level-4 we discussed moving the `datadir` to a fast external storage, but the majority of the space used for bitcoin is the blocks directory (`blocksdir`).  Although you should always use for fastest storage for `datadir`, you are free to use slow storage for `blocksdir`.  So if you only want to consume a small amount of your SSD (assumed `D:`) then you can keep your blocks on your slow "spinning" drive.

* `upnp=1`

One of the harder challenges you may face running a node, is to get incoming connections.  If you are lucky, you may find that your firewall and network HW support the uPnP protocol.  If they do, this setting will allow bitcoin to configure uPnP to allow incoming connections to your node.
