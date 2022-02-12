[#]:_[strip]___If_the_formatting_is_broken,_please_let_me_know_what_app_you_used

[#]:_[strip]___-----BEGIN_PGP_SIGNED_MESSAGE-----
[#]:_[strip]___Hash:_SHA256

[#]:_[begin]___Document_Hash_Starts_at_the_beginning_of_this_line_{_EOL=`\n`_}
[#]:_[rights]__Copyright_2022_brianddk_at_github_https://github.com/brianddk
[#]:_[license]_Apache_2.0_License_https://www.apache.org/licenses/LICENSE-2.0
[#]:_[repo]____github.com/brianddk/reddit/blob/master/markdown/brute-force.md
[#]:_[btc]_____BTC-b32:_bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
[#]:_[tipjar]__github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
[#]:_[ref]_____github.com/brianddk/reddit/blob/master/python/signed-md.py
[#]:_[version]_1.0
[#]:_[title]___Brute_Force_Math_for_Trezor_and_BIP39
[#]:_[usageA]__<msg.md_pgm.py_stripGpg_|_pgm.py_stripUnderscore
[#]:_[usageB]__<msg.md_pgm.py_stripGpg_|_pgm.py_setHash_|_gpg2_--clear-sign_\
[#]:_[usageB.]____|_pgm.py_fixupGpg_|_pgm.py_prepGpg_|_gpg2_--verify
[#]:_[verify]__re1='s@(^\[#\]:\x5f\[strip\]\x5f+)'_re2='([^\x5f]*)\x5f?'_\
[#]:_[verify.]____re3='@\2\x20\3\x20\4\x20@g'_sh_-c_\
[#]:_[verify.]____'sed_-E_"$re1$re2$re2$re2$re3"_msg.md'_|_gpg2_--verify

I saw a few posts asking about seed mnemonic, passphrase and PIN brute-force workloads.  Here's my attempt to explain it.  To start with, lets try to simplify some of these numbers and refer to them all in log_base_2.  This is sometimes called "bits of entropy".  But call them what you like.

### Cracking hashrate

When looking at how many guesses can be done per second, lets try to look at some benchmarks.  As we'll see below, the vast majority of the work here are SHA512 hashes.  Looking at a [recent SHA512 benchmark](https://openbenchmarking.org/test/pts/hashcat&eval=306f31f896ee6afac758df6db7589b6a2a232723#metrics) shows an RTX3080 capable of 7 billion hashes / second (7 GH/s).  To simplify the math, lets just assume an attacker is capable of 100 GH/s.  This is huge overshoot since with most of this stuff, there are bottlenecks in parallelization.  So having 10 GPUs won't give you a 10x increase, due to bottlenecks.

Also, it is common to imagine that bitcoin (SHA256) miners could be tasked with cracking.  This is also untrue since SHA256 and SHA512 are different.  There are also required memory reads that will break much of the run speed that a theoretical miner would be able to achieve.  [Here's a detailed writeup](https://rya.nc/asic-cracking.html) in case you are not convinced.

Lets use one year of cracking as a single unit.  Using 100 GH/s for a year gives us (using log_2) 61.45.

### Passphrase cracking given Mnemonic

First lets try to quantify what types of operations are required to do stuff here.  To do something like a passphrase brute-force, assuming you know the seed-mnemonic, here are the basic steps:

1. Perform a checksum verification on the mnemonic (SHA256)
2. Perform a HMAC SHA512 operation on the (mnemonic + passphrase) string
3. Redo \#2 on the result iterating a total of 2048 times
4. Take the resulting BIP32 `xprv` then determine your derivation
5. For each node in your derivation, perform one HMAC SAH512 operation
6. Repeat \#5 for each of the three major bitcoin script types

So for each passphrase guess, steps 2-3 will require 2048 HMAC SHA512 operations.  Each standard derivation will require 5 HMAC SHA512 operations, and for each guess you need to perform 3 unique derivations (Legacy, P2SH-Segwit, Segwit) to check for Bitcoin.  So a total of (2048 + 3 * 5) or 2063 attempts per passphrase (given a seed).  Or in log_2, 11.01.

Given our hashrate above, and our hashes per guess above, we now know our passphrase needs 50.44 bits of entropy (61.45 - 11.01) to defeat a one-year crack.  So if your passwords use the base58 character set you would need a 9 character passphrase, or if you use the BIP39 wordlist you would need a 5 word passphrase.

### Mnemonic cracking

For the mnemonic, the count is exactly like the passphrase cracking, but we have to do a checksum verification (step \#1) on each and every guess.  But we get to discard some work since if the checksum fails, we can skip steps 2-6.  So the number of checksum pass -vs- checksum fail depends on the number of words in the mnemonic.  For 12 words, you get a `pass:fail` ration of `1:16`  or `1:(2**12/3)`.  The latter formula holds for all numbers of words (12, 15, 18, 21, 24).

So our number of hashes for a mnemonic guess works out to one SHA256 to test the checksum, then the rest is as before.  We can divide out the number of failed checksums so the number of guesses per POSSIBLE mnemonic combo comes to:

    let w = number_of_words
    hash_per_mnemo = (2063 + 2**(w/3)) / 2**(w/3)

Sticking to log_2, `log_2(hash_per_mnemo(w))` for `w:{12, 15, 18, 21, 24}` comes to `{7.02, 6.03, 5.05, 4.10, 3.18}` respectively.  And, of course, the number of memo guesses comes to:

    let w = number_of_words
    num_guesses = 2048**w
    
Putting it all together (reminder logs sum), the number of hashes required to cover the entire key space for `w:{12, 15, 18, 21, 24}` comes to `{139, 171, 203, 235, 267}` respectively.  So obviously, these numbers are way out of reach for any cracking.  It would require 2^77 years (139 - 61.45) to crack a 12 word seed.  Or 2.21 trillion billion years.  Long past the heat death of the universe.

### Pin cracking

Unlike mnemonic and passphrase, PINs use ChaCha20 not SHA, and it  uses it as full data decryption algorithm.  So to perform a PIN brute force, assuming you captured the device memory the steps are as follows

1. Perform a HMAC SHA256 hash on the stringified PIN
2. Redo \#1 on the result iterating a total of 10,000 times
3. Use the result of \#2 to decrypt the captured memory
4. Scan the decrypted memory for magic bytes to confirm decryption

So there are 10,000 SHA256 hashes, a full data ChaCha20 decryption, followed by a few memory reads to check for success.  But since I don't have any good benchmarks of this operation, the only one I have to use would be from Kraken's post.  The Kraken team cracked a 4 digit pin (keyspace of 10000) in less than 120 seconds.  That comes to 83 attempts per second, or in log_2 31.29 bits of entropy per year.  So a 9 digit pin would require months to crack, a 10 digit pin would require years, and an 11 digit pin would require decades.

### Conclusion

The seed mnemonic is beyond any brute force possibilities by a fairly large margin.  But if you're concerned about a Joe Grand or Kraken type disassembly attack, you can protect against it using `sd-protect`, large pin or large passphrase.  Any one of those choices is fine, you don't need all three.  The largeness of the PIN would be 10 or 11 digits.  The largeness of the passphrase would be 9 random base58 characters or 5 random bip39 words.  Like the seed-mnemonic, `sd-protect` is well beyond any brute-force attempts.

 
[#]:_[end]_____Document_Hash_ENDS_at_the_end_of_this_line_{_EOL=`\n`_}
[#]:_[hash]____7a74dd38b9e131dc7c4b1a9e8b8671bb9e168548f7e7f1de90a3c7425882dc9b
^&copy; ^hash: ^[7a74dd38b9e131dc7](https://web.archive.org/web/20220212015757/https://www.blockchain.com/btc-testnet/tx/580a0e263189784395fbc88bbb5e928effaaf5b622888b3d17f3262e4123625a)

[#]:_[strip]___-----BEGIN_PGP_SIGNATURE-----

[#]:_[strip]___iQFEBAEBCAAuFiEEYoX6CPtntyvk2kGEg18EM6bVGGAFAmIHFQsQHGJyaWFuZGRr
[#]:_[strip]___QHJlZGRpdAAKCRCDXwQzptUYYLRQB/9350NYnD14eB+3yG/PCwjlJ+2XgdDP7A3S
[#]:_[strip]___gW0VFmP5mKJEsD2fu39D8TOyZww8ikUxk+06k8TzQ3rdIQTTZBkXGTH1r19ngKbr
[#]:_[strip]___HrzQRC6oThzv2+NWWuyenX75Z1nrcj04rAYmqy9hORtera64z/tmjRqitTdd7YbE
[#]:_[strip]___hteaF9Zl3p1t6VddaRK6cbbIFsH9/Kq4VjI/cvQdhQXpi0D4EbYwh5ioLK+4Tcog
[#]:_[strip]___F7lTd27vSiyCnI0ElIXnQ2hC+/YLR0RkxdeRIIGl18IlOfWcSDJcItvqA6RtlFdT
[#]:_[strip]___RCTyUJOxATl3RUEPGKHenbbvGuQ/eMXSaOC+3TbS4x8WOUW1FQ1P
[#]:_[strip]___=qMuS
[#]:_[strip]___-----END_PGP_SIGNATURE-----
