# google-reader-iphone-sync

This is a small, cobbled-together tool which allows you to read your Google
Reader feed items offline on your iPhone or iPod Touch.

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

