# google-reader-iphone-sync

GRis (Google Reader iPhone Sync) is an RSS feed reader for the iPhone. There are already a few available, but this one features:

* It syncs with Google Reader. So items you read will be marked as read, and you can star items to come back to them later.
* It saves images in feeds for offline viewing. Surprisingly few iPhone RSS readers do this, which sucks if (like me) you own an iPod Touch, the sans-3G bastard son of an iPhone.
* It's free
* ... and it's entirely open source (the best kind of free).

## Using it:
The best way to install is via my cydia repository at [gfxmonk.sysprosoft.com/cydia/](http://gfxmonk.sysprosoft.com/cydia/)

If you want to distribute a modified package, you *must* edit the `cydia/control` file so that it won't clash with official versions. You should also probably change the icon, so people don't get confused.

See [saurik's tutorial](http://www.saurik.com/id/7) for instructions on creating your own repository.

## Running / building / installing:
To build and run on the iPhone simulator, you'll need
* The iPhone SDK
* Python (I use 2.5.1)
* [nose](http://code.google.com/p/python-nose/)

To install on a device, you'll need (for your mac):
* Ruby
* [capistrano](http://www.capify.org/)
* dpkg binaries (specifically dpkg-deb and dpkg-scanpackages. These come with fink, and presumably all other apt ports)

...and the device will need to have:
* Cydia
* OpenSSH
* Link Identity Editor

the python package is a dependency of GRiS, so it'll be installed if you do not already have it.

### Configuration required:
* see config_example.yml

# Running tasks:
Run `cap -T` to see what you can do.

Most of the time, you'll want to run one of:
* `cap nose` - run the tests
* `cap package:install` - build package and install it on your device

Note that currently, the google\_reader\_test.py tests are very brittle, and require you to have an actual google reader account. I hope to fix this up in the future.

----
#Problems:

If you have any issues building / running, please post them to the [issue tracker](http://code.google.com/p/gris/issues/list).


## Thanks:

* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [pyrfeed](http://code.google.com/p/pyrfeed/)
