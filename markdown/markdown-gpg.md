[#]:_[strip]___If_the_formatting_is_broken,_please_let_me_know_what_app_you_used

[#]:_[strip]___-----BEGIN_PGP_SIGNED_MESSAGE-----
[#]:_[strip]___Hash:_SHA256

[#]:_[begin]___Document_Hash_Starts_at_the_beginning_of_this_line_{_EOL=`\n`_}
[#]:_[rights]__Copyright_2022_brianddk_at_github_https://github.com/brianddk
[#]:_[license]_Apache_2.0_License_https://www.apache.org/licenses/LICENSE-2.0
[#]:_[repo]____github.com/brianddk/reddit/blob/master/markdown/markdown-gpg.md
[#]:_[btc]_____BTC-b32:_bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
[#]:_[tipjar]__github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
[#]:_[ref]_____github.com/brianddk/reddit/blob/master/python/signed-md.py
[#]:_[version]_0.1
[#]:_[title]___Fun_experiment_in_"GPG_Signed_Reddit_Posts"
[#]:_[usageA]__<msg.md_pgm.py_stripGpg_|_pgm.py_stripUnderscore
[#]:_[usageB]__<msg.md_pgm.py_stripGpg_|_pgm.py_setHash_|_gpg2_--clear-sign_\
[#]:_[usageB.]____|_pgm.py_fixupGpg_|_pgm.py_prepGpg_|_gpg2_--verify
[#]:_[verify]__re1='s@(^\[#\]:\x5f\[strip\]\x5f+)'_re2='([^\x5f]*)\x5f?'_\
[#]:_[verify.]____re3='@\2\x20\3\x20\4\x20@g'_sh_-c_\
[#]:_[verify.]____'sed_-E_"$re1$re2$re2$re2$re3"_msg.md'_|_gpg2_--verify

TLDR; I decided to make a crazy complicated way to GPG-sign reddit posts.  Feel free to ignore.

Out of curiosity, I decided to set about performing GPG `clear-sign` operation on reddit posts.  The idea is similar to how GPG clear-sign is used in email or general text declarations today.  I've also done this in the past on web-page postings embedding the clear-sign meta-data in comment tags.  This is effectively how I decided to do it on reddit.  Although I could leave the meta-data visible inline using `<pre>` tags, I didn't want to pollute the post with all that data, so hidden comments was the path I choose.
 
Since reddit flavored markdown doesn't support multi-line comments (`<!-- -->`) I had to accept a bit (or a lot) of pre/post processing to make this work.  Not completely happy with the results, but since I was planning on scripting all of this stuff heavily, pre/post processing became less of an issue.

So the basic form of "comments" in reddit-markdown is really just a mal-formed link descriptor.  Specifically `[]:CommentsHere`.  The content inside the `[]` is supposed to be a link reference number and the data after the `:` is supposed to be the URL.  But if you never reference the link data, its ignored.  You also can't have spaces after the `:` so I have to convert spaces to `_` and back again in my pre/post processing.  This form of mal-formed link comments works in reddit-flavored-markdown, github-flavored-markdown, and stackexchange-flavored-markdown.  So my clear-text signature meta-data looks like this once encoded in "comments"

    [#]:-----BEGIN_PGP_SIGNED_MESSAGE-----
    
Since I'm committed to pre/post processing, I put more tags in the comments to make parsing easier, but that is the general idea.  So now the comments are invisible to the user, but I still need a way to verify it externally.  So luckily the reddit API provides such a way.  Simply append `/.json` to the end of the URI and you will get the raw JSON.  Of course you get more data than just the markdown, so those familiar with JSON or javascript will need to know that the markdown is located at `[0].data.children[0].data.selftext` in the JSON object.

Since the comment stripping is rather kludgy I also provide a straight SHA256 checksum as well.  I do require the checksum be clipped so that only the body of the message is used.  For this I tag a `[begin]` and `[end]` comment for the hasher to know when to start and end.  I only include the first 17 hex chars of the checksum since that is enough to ensure no one can realistically perform hash grinding.  I mean... I suppose they COULD, but I just can't imagine anyone would put that much hashing power to the task.

And finally, since there is no time oracle in GPG (that I know of), I choose to use a blockchain public ledger as a time oracle.  It's not exact, but it can get you down to the general hour of publication, which in most cases is fine.  I link to the blockchain proof-of-time transaction in the hash footer.  Just search the page for the hash in the footer to find the full SHA256 hash encoded in the transaction.

To see a full working example, look at a recent post I made to prototype it.  Here's the [formatted post](https://www.reddit.com/r/Bitcoin/comments/smj1ep/) and here's the signed [post JSON](https://www.reddit.com/r/Bitcoin/comments/smj1ep/.json)

So with all this pieced together I get to assert the following:

1. That I indeed published the text enclosed
2. That I indeed published it within the hour claimed
3. No alterations were made to the text since publication

***

Now, there are many infinitely easier ways to do this, but this was just my method.  Below I will outline the 120 lines of python code to glue it all together.  It's basically a small script that takes sub-commands.  It generally reads from `stdin` and writes to `stdout`.  Since I'm using SHA256, I choose a convention of using `\n` as the EOL designator instead of `\r\n` that GPG uses.  So here are the basic subcommands of the script and how they work:

* `setHash` - Takes markdown from `stdin` and replaces the `[hash]` tag with a freshly computed one, dumping to `stdout`
* `fixupGpg` - Takes the output of `gpg --clear-sign` and turns the GPG meta-data into invisible markdown "comments"
* `prepGpg` - Does the opposite of `fixupGpg` restoring the "fixed-up" metadata with the original GPG format
* `stripGpg` - Strips the GPG meta-data so that the contents can be re-signed
* `stripUnderscore` - Changes "`_`" back to " " in "comments" making them simpler to edit and revise
* `getPost {subreddit} {id}` - Retrieves markdown in post `id` from the named subreddit and dumps to `stdout`

So to prepare or revise an `article.md` file for posting, the following would work:

    < article.md signed-md.py stripGpg | signed-md.py setHash | gpg --clear-sign | signed-md.py fixupGpg > signed-post.md

And to verify a signed post has a valid signature, we can use my example post (id=`smj1ep`, subreddit=`bitcon`)

    signed-md.py getPost bitcoin smj1ep | signed-md.py prepGpg | gpg --verify
    
I could also add commands like `pushPost`, `setFooter`, `pushBlockchain` in future revisions.  And for the curious, YES, I did originally do this is `sed` but decided python would be easier to maintain.  But since `sed` has less "side effects" I kept the regex around as an alternative to `prepGpg`.

[#]:_[end]_____Document_Hash_ENDS_at_the_end_of_this_line_{_EOL=`\n`_}
[#]:_[hash]____634f627d602e358d2278494ac3aedd05d17a53cc011f9a3099e2b2ac0899a0d3
^&copy; ^hash: ^[634f627d602e358d2](https://web.archive.org/web/20220208055804/https://www.blockchain.com/btc-testnet/tx/3685f144f456a500bd90cb58a60e594312dcab0132838fd59067eb26094283d3)

[#]:_[strip]___-----BEGIN_PGP_SIGNATURE-----

[#]:_[strip]___iQFEBAEBCAAuFiEEYoX6CPtntyvk2kGEg18EM6bVGGAFAmICBu0QHGJyaWFuZGRr
[#]:_[strip]___QHJlZGRpdAAKCRCDXwQzptUYYGkDB/9RWJTxKXY1IjB9j/TCUu9cqUMBKcuKQfWb
[#]:_[strip]___YlAlqLvDx6N1A0eS4aAqqjThuItj5eyJ+xgo9us80/e4szmMdGi9uSHNAZYlQDRm
[#]:_[strip]___JkY/IEilN5VCcBFzOixYwWf8NLRoYfpNQ/kuqCaqgE5ReUsR/7/wU5VsA2IRsDjb
[#]:_[strip]___Vaso/mBlp/CUZF4mpx7xt048Xwfd7mj/eITRGVKbNf2zd/9Q/YXl45N9WBMum15b
[#]:_[strip]___ZeNrJzBr2mutJ9qbmIekpbsiHDR92mXYsGiQRkPoNvgRi3Yw1E2SH+6tn1Xx10n0
[#]:_[strip]___73ZAZXt5P2cZXBWbvGv0lf7n1mqfPG3Ec3nPlSUptt1jLxAG5Gnq
[#]:_[strip]___=d5dJ
[#]:_[strip]___-----END_PGP_SIGNATURE-----
