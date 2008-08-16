# google-reader-iphone-sync

GRis (Google Reader iPhone Sync) is an RSS feed reader for the iPhone. There are already a few available, but this one features:

* It syncs with Google Reader. So items you read will be marked as read, and you can star items to come back to them later.
* It saves images in feeds for offline viewing. Surprisingly few iPhone RSS readers do this, which sucks if (like me) you own an iPod Touch, the sans-3G bastard son of an iPhone.
* It's free
* ... and it's entirely open source (the best kind of free).

## Using it:
The best way to install is via my cydia repository at [gfxmonk.sysprosoft.com/cydia/](http://gfxmonk.sysprosoft.com/cydia/)

If you want to install a modified package, you should update the `cydia/control` file so that it won't clash with official versions. Then, run `cap package`. Copy this package file to your iPhone and run `dpkg -i GRiS.deb`

See [saurik's tutorial](http://www.saurik.com/id/7) for instructions on creating your own repository.

## Build Dependencies:
Since the tool is thrown together with what I had around, its
dependencies are a bit all over the place:

* some kind of *nix environment (OSX or Linux should be fine. Using cygwin _hopefully_ works on windows)
* Python
* Ruby
* Capistrano (sudo gem install capistrano)

On your iPhone / iPod Touch, you will need:

* To be jailbroken, for starters.
* python
* OpenSSH (to transfer a modified program)

## Thanks:

* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [pyrfeed](http://code.google.com/p/pyrfeed/)

