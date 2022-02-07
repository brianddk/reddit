[#]:_[strip]___If_the_formatting_is_broken,_please_let_me_know_what_app_you_used

[#]:_[strip]___-----BEGIN_PGP_SIGNED_MESSAGE-----
[#]:_[strip]___Hash:_SHA256

[#]:_[begin]___Document_Hash_Starts_at_the_beginning_of_this_line_{_EOL=`\n`_}
[#]:_[rights]__Copyright_2022_brianddk_at_github_https://github.com/brianddk
[#]:_[license]_Apache_2.0_License_https://www.apache.org/licenses/LICENSE-2.0
[#]:_[repo]____github.com/brianddk/reddit/blob/master/markdown/trusting-trust.md
[#]:_[btc]_____BTC-b32:_bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
[#]:_[tipjar]__github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
[#]:_[ref]_____github.com/brianddk/reddit/blob/master/python/signed-md.py
[#]:_[version]_1.0
[#]:_[usageA]__<msg.md_pgm.py_stripGpg_|_pgm.py_stripUnderscore
[#]:_[usageB]__<msg.md_pgm.py_stripGpg_|_pgm.py_setHash_|_gpg2_--clear-sign_\
[#]:_[usageB.]____|_pgm.py_fixupGpg_|_pgm.py_prepGpg_|_gpg2_--verify
[#]:_[verify]__re1='s@(^\[#\]:\x5f\[strip\]\x5f+)'_re2='([^\x5f]*)\x5f?'_\
[#]:_[verify.]____re3='@\2\x20\3\x20\4\x20@g'_sh_-c_\
[#]:_[verify.]____'sed_-E_"$re1$re2$re2$re2$re3"_msg.md'_|_gpg2_--verify

TLDR; Bitcoin v22.0 moves to Guix so that we can "trust the compiler" even less

`<tinfoil_hat_fud>`

With any software that handles finance or private keys, the question of trust is important.  Most have a general concept of this stuff, and that is usually fine for most anyone's needs.  But there is always the rare case where trust policies are too laxed and users get burned, like the [Electrum v3.3.3 phishing attack](https://github.com/spesmilo/electrum/issues/4968).  Here I'll try to go through the minimal level of trust all the way down to the theoretical limit of what can be done.  At the heart of the matter is the concept of extended trust.  In most trust-tests, we start with something that has more trust and see if we can connect it to something with less trust.  I'll walk through a few examples from the top down.  In general we will go through the following levels:

1. Trust the site
2. Trust the builders
3. Trust the compiler
4. Trust the kernel
5. Trust the hardware

### Trusting the site

When downloading software such as bitcoin-core, at a minimum it is important to ensure you download from `bitcoin.org` and not some site like `download.com`.  If you grab software from a sketchy site, it may come packaged with code to steal your keys (See "Electrum phishing" above).

In the realm of "trusting the site" there are those who trust the browser to get you to `bitcoin.org` and others who are more paranoid and will ensure that SSL is enforced.  Unfortunately, unless the site uses something like DNSSEC, DANE, or other cryptographic domain verification, you can just never be sure.  Attacks like bitsquatting and dns-poisoning can get past even the best intentions of DNS security.  So... sites can't be trusted.

### Trusting the builders

In most cases, trusting the builders is the what most recommend.  This process completely ignores WHERE the binaries were taken from (even `download.com`) and instead rely on a builder's cryptographic signature delivered with, or embedded in, the file.  These are usually either GPG signatures or CodeSigning certificates like Authenticode.  Main issues here is that many user's don't know WHO the builders are.  In many cases, most simply assume that a trusted product, must have a trusted package owner / builder.  A recent example of where this went horribly wrong was when ownership of a popular JavaScript library was left to a randome contributor.  The new owner went about [crafting back-doors to steal bitcoin](https://www.theregister.com/2018/11/26/npm_repo_bitcoin_stealer/).  Since JavaScript is interpretive, it was quickly spotted, but it shows the danger of entrusting new package builders or maintainers.  Clever projects (like bitcoin) get around this problem by having reproducible builds.

Reproducible builds are a way to design software so that many community developers can each build the software and ensure that the final installer built is identical to what other developers produce.  With a very public, reproducible project like bitcoin, no single developer needs to be completely trusted.  Many developers can all perform the build and attest that they produced the same file as the one the original builder digitally signed.

In most situations, those who are not developers are fine to stop here.  Just insist that the software you use is open-source, well audited, reproducible, with multiple maintainers who all attest to the same verified compiled binaries.  Bitcoin meets this test on all counts

### Trusting the compiler

For those who may fear an evil cabal of developers, or feel their project is not audited enough, the next level down is to trust nothing but the compiler.  These users will build the project from source code removing the need to trust the project builders.  Many may imagine that this is the furthest down the "rabbit hole" this topic can go, but in actuality it isn't.  In a 1984 award speech, the recipient, Ken Thompson, posited the question "Should you trust your compiler?".  He goes on to outline a method called the "[Trusting Trust Attack](https://dl.acm.org/doi/pdf/10.1145/358198.358210)".  Since even the most paranoid users usually trust the compiler, Ken suggested the compiler is the perfect place to put your Trojan.

The basics of this attack are due to the fact that to make a new compiler binary, you generally use the last compiler binary.  But what if compiler binary had malicious code to infect new binaries.  This is particularly problematic since compilers building compliers goes back pretty far.  Android was made with Linux that was made from Minix.  Apple was made with BSD and BSD was made from Unix.  These build genealogies go back decades.  So what if the original Unix back in the 60's had a trojan in the compiler that has been carried forward for the last 60 years?

As involved as this sounds, there have been many proof of concepts done to prove the attack's viability.  And with distrust of state security agencies getting worse year after year, it's not hard to imagine that some agency would want to pull off such attack.  The main attack "surface" here are what builders call the "seed binaries".  These are the previous versions of compiler and tools needed to build the next compiler.  If you can "seed" your build with a smaller set of binaries then, in theory, you may get the set so small that examination, byte for byte, could look for "bad code".

In version 22.0, bitcoin moved to the [Guix build system](https://github.com/bitcoin/bitcoin/blob/v22.0/contrib/guix/README.md) for their official builds.  This reduced the "weight" of those seed binaries [from 550 MB down to 120 MB](https://guix.gnu.org/blog/2019/guix-reduces-bootstrap-seed-by-50/).  The Guix team is prototyping a new compiler build with a reduced seed weight of [357 bytes](https://www.joyofsource.com/we-did-it.html).  That's a reduction of 99.999935% from the binary seed weight of Bitcoin v0.21.2

This claim is a bit hyperbolic, but less than you might think.  The complier build requires a proto-complier (mes) and a shell (guile).  This reduction is only for `mes` not `guile`.  Though there is work to do the same reduction on `guile` that was done on `mes`, but that may still be a few years out.

### Trusting the Kernel

Implicit in the trust of the compiler is the trust of the kernel and OS that the compiler is running on.  So if a trusting-trust trojan decided to propagate and infect in both a compiler and kernel, then reducing your binary seed may not be enough.  This is a harder attack to pull off since a 357 byte seed build will likely be hand audited for the first few iterations.  The trojan would need to know to infect the process far enough along to where it wasn't visible any more.

The solution to this is to bootstrap your compiler build, without a kernel.  This can be done up until a point.  The hex assembler and macro assembler can be loaded directly out of a legacy bootloader (think 0x7C00) and work is ongoing in in the `stage0` project that helped in the `mes` bootstrap.  But realistically, I'm not sure how far they can take this.

### Trusting the Hardware

Imagining if you could bootstrap without the kernel, there is still the trust of the hardware.  A builder is trusting that the processor and instruction pipeline is not doing something malicious if it detects a compiler bootstrap is in place.  Although this is pretty deep paranoia, people are still thinking about this stuff.  The reduced `mes` bootstrap is working to have a `x86` and `arm` bootstrap independent of each other.  Although one can be cross-compiled on the other, it was thought to be better if `arm` software didn't have to trust `x86` hardware for a bootstrap, and vice-versa.

`</tinfoil_hat_fud>`

### References

* [Youtube: ELI5 Bootstrapping](https://www.youtube.com/watch?v=nslY1s0U9_c)
* [Youtube: Reducing Bitcoin Bootstrapping](https://www.youtube.com/watch?v=I2iShmUTEl8)
* [Youtube: Mes Bootstrapping Reduction](https://www.youtube.com/watch?v=XvVW80dDF8I)
* [Youtube: Mes Reduced Binary Seed Bootstrap](https://www.youtube.com/watch?v=mhopx8J2Z8s)
* [Ken Thompson: Trusting Trust Attack](https://dl.acm.org/doi/pdf/10.1145/358198.358210)
* [MIT: How to perform Trusting Trust Attack](https://web.mit.edu/6.033/2014/wwwdocs/assignments/quizzes/trust_stack_slides.pdf)
* [First Reduction of Mes bootstrap to 120 MB](https://guix.gnu.org/blog/2019/guix-reduces-bootstrap-seed-by-50/)
* [Future Reduction of Mes bootstrap to 357 B](https://www.joyofsource.com/we-did-it.html)
* [Bitcoin Bootstrapping](https://github.com/bitcoin/bitcoin/blob/v22.0/contrib/guix/README.md)
* [Stage0 Project](https://github.com/oriansj/stage0)
* [Mes Project](https://www.gnu.org/software/mes/)
* [Guix Project](https://guix.gnu.org/)
 
[#]:_[end]_____Document_Hash_ENDS_at_the_end_of_this_line_{_EOL=`\n`_}
[#]:_[hash]____68a4dd4bc6d2c0cc90e4c2a7ff9acd4c36ea1c849ab0a23321d88091bd4f95f3
^&copy; ^hash: ^[68a4dd4bc6d2c0cc9](https://web.archive.org/web/20220207055821/https://www.blockchain.com/btc-testnet/tx/dd5f36239ae74a0c380c1bb74feedbea507bb81f5ff97a02f62b57e869ca09c2)

[#]:_[strip]___-----BEGIN_PGP_SIGNATURE-----

[#]:_[strip]___iQFEBAEBCAAuFiEEYoX6CPtntyvk2kGEg18EM6bVGGAFAmIAtiEQHGJyaWFuZGRr
[#]:_[strip]___QHJlZGRpdAAKCRCDXwQzptUYYEp6CAC4PyY5+ch4SuT3HZy2il5nfq2KrkRd9oRr
[#]:_[strip]___Sezl4DCboEbgvpez2jqB6177tjnC13h8c+rXVBQTcrmKucL0dnlG2V1hHQtFDJPv
[#]:_[strip]___meEHTaxa/b2o6aIzO7fLeoS5uMSaj+BP2dyC6ph6pXb/wgU2ARtdhIcU6XiP7kMw
[#]:_[strip]___XGkszoMOim48prFHwk8/WGFZfbf3Mlu6LHflkn9aM1PjO5nCQ66ua4Ng0H0LthZH
[#]:_[strip]___WpiSTWk93luu7HNiq25b00SzNWofc54QRLk9qZnf8uC6ztoZzwRyum8iJkgKzZIs
[#]:_[strip]___3XaDTQKvlCzFSNBbM8JvVv48m4AZ3qPsVBy/7CEcy4pcevhDnZxj
[#]:_[strip]___=EtN3
[#]:_[strip]___-----END_PGP_SIGNATURE-----
