There is a fairly small subset of r/Bitcoin users that run a full node.  I think the idea of running a full node has gotten a bad rap over the years since there is so much talk about running on a Raspberry Pi, or getting zippy SSDs.  Although all of this can be fun, it is often not really required at all.  Here are some ways to run a full node starting with the very simple.  I'll get into more complex configs, but these are all optional.

### Tech Skill Level: 0 (the basics)

1. Download Bitcoin Core
2. Install it
3. Let it run overnight

In many cases, thats it.  If your running a new machine with a fairily good internet connection, 8 or 9 hours will be enough to complete the "Initial Block Download" (IBD).  This may fill up your drive a bit, but again, on most new machines, 300 GB of space isn't that hard to come by.

### Tech Skill Level: 1 (encrypted wallet)

One thing we left out in the level-0 excercise is encrypting your wallet.  It's easy enough to do well, but a bit more difficult to do right.  The main challenge is that humans generate really poor passwords.  If you want a good password, the best way is to use something called "diceware".  Basically, you just grab 4 or 5 dice and each throw of the dice represents a certain word on a special list.  The throw `{1,4,5,3,1}` for example would be the word `camping` on the [EFF-diceware-wordlist](https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt).  So you repeat this a few times until you have a list of 8 or so words which becomes the passphrase you use to encrypt your wallet.  ***Write it down***, it is always hard to remember at first.  So at level-1 your list becomes:

1. Download Bitcoin Core
2. Install it
3. Let it run overnight
4. Choose `Encrypt Wallet` from the `Settings Menu`
5. Enter your 8 word (or so) passphrase generated using the Diceware method

### Tech Skill Level: 2 (enable pruning if needed)

Though I said "300 GB of space isn't hard to come by", some times it actually is.  If space is an issue, a simple way to fix it is to tell bitcoin to simple take less space.  This is called "pruning" and can take that number from 300 GB down to below 5 GB.  If you can't find 5 GB, then you'll have to read ahead to level-3 to add USB storage.  But the good news is, enabling pruning is pretty easy, we just add another step to our working list:

1. Download Bitcoin Core
2. Install it
3. Let it run overnight
4. Choose `Encrypt Wallet` from the `Settings Menu`
5. Enter your 8 word (or so) passphrase generated using the Diceware method
6. Choose `Options` from the `Settings Menu`
7. Choose `Prune block storage to:` and select the max size for the blocks to use

Note, even setting this to 1 GB will still leave you with about a 4.5 GB install.  The blocks take up a lot of space, but the `chainstate` and other folders eat up at least 3.5 GB and they can't be pruned.  Also, be aware, to disable pruning requires you to perform the entire IBD again.  While pruned some other functions my be disabled as well, so just know that pruning does limit some functionaility.

### Tech Skill Level: 3 (use secondary storage)

We glossed over the "new machine with fairly good internet" part.  Truth me known many pepole do not have fairly new machines, and find the IBD to take longer than the "over night" best wishes.  For most people the slowdown is the disk access when calculating what is called `chainstate`.  This requires fast random reads and writes to the disk.  If you have an SSD disk, this will be no problem, but if you have a non-SSD "spinning" disk, random writes are always slow.  Though an SSD will speed things up, they are pricey, so a nice middle ground may be a simple high-end USB key drive.  You can get some with 10 to 15 MB/s random writes which is usually a order of magnatude faster than a "spinning" disk.  And with pruning (see level-2), a small USB drive should be fine.

Once you decide on a drive, the tricky part will be to enable external storage.  It requires editing a configuration file and adding a few lines.  The bitcoin program will let you edit your configuration files, but requires something called a "file association".  Many copies of Windows don't have this association, so don't be alarmed.  An error here is actually expected.  Here are the steps if you don't get the error, then we will go over what to do if you do get the error.

1. Download Bitcoin Core
2. Install it
3. Let it run overnight
4. Choose `Encrypt Wallet` from the `Settings Menu`
5. Enter your 8 word (or so) passphrase generated using the Diceware method
6. Add the pruning steps here, if that is your desire
7. Choose `Options` from the `Settings Menu`
8. Choose `Open Configuration File`, and anwer 'OK' after reading the warning
9. If the file opens, add the lines below, if it doesn't read about how to fix it below

Through the windows file browser, you will need to determine the drive letter of your USB key drive.  For the sake of this example, we will assume it is `D:`, but you ***must determine this yourself and correct the example***.  Once you know the drive letter, create a blank folder on the drive called `Bitcoin`.  So for this example, creating `Bitcoin` on drive `D:` will create the path `D:\Bitcoin`.  Once done, assuming that `D:` is your drive, here is what we add to the configuration file:

```
datadir=D:\Bitcoin
```
