# google-reader-iphone-sync

This is a small command-line tool which allows you to sync your Google
Reader feed items to your iPhone or iPod Touch for offline reading. It
handles pre-downloading of images, and includes a lighttpd module for
viewing and navigating your feed items directly in MobileSafari.

## Dependencies:
Since the tool is thrown together with what I had around, its
dependencies are a bit all over the place:

* some kind of *nix environment (OSX or Linux should be fine. Using cygwin _hopefully_ works on windows)
* Python
* Ruby
* Capistrano (sudo gem install capistrano)

On your iPhone / iPod Touch, you will need:

* To be jailbroken, for starters.
* SSH server (this is part of the "BSD Subststem")
* lighttpd
* python

## Setup:

Open "config_example.yml", fill it in with your details and preferences,
and save it as "config.yml".

Then run "install.command". You will probably then need to restart your ipod for these settings to take effect.

## Using:
Run sync.command. This will

* grab any unread items off your iPhone
* mark items that have been deleted (since your last sync) as "read" on Google Reader
* fetch unread entries on Google Reader (the max number of items to fetch is changeable in config.yml)
* push them out to your iPhone, ready for reading on-the-go

To read your items, go to the following address (on your iPhone)
http://127.0.0.1/RSS/
(or the appropriate path, if you change iphone\_destination_path in config.yml)

To mark an item as read on google reader, you just delete the file from your iPhone.
Google reader will be updated when you next run the sync command.

_**power users**: you can run subsets of tasks (like just pushing or pulling items to/from your iPhone,_
_as well as syncing to google-reader without downloading any new items._
_Run `cap -T` from the base directory to see what's available._


## Issues:
To transfer things, it actually ssh's into your iPhone and pushes/pulls
files from there to your mac (using rsync). This is because I found that
rsync from my mac to my iPod dropped out constantly, whereas this method
seems quite stable.

This means you need to put your mac account password into config.yml.
If (like me) you realise that this is a terrible idea, you should instead
invest in setting up ssh-keys on both your iPhone and mac.

## Thanks:

* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [pyrfeed](http://code.google.com/p/pyrfeed/)
* [lighttpd](http://www.lighttpd.net/)
* [dirlist](http://modmyifone.com/forums/native-iphone-ipod-touch-app-launches/52021-pdf-chm-doc-xls-photo-viewer-all-one-safari-lighttpd-based-complete-instruct.html)

