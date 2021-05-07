Cournal is a collaborative note taking and journal application using a stylus.

## Huh? ##

Cournal allows multiple users to annotate PDF files in real-time.

The goal of this project is a full featured note taking application (like
[Xournal](http://xournal.sf.net/) or Windows Journal), which allows multiple
people to collaborate (like [Gobby](http://gobby.0x539.de/)).

### Why not extend Xournal? ###

There have been numerous discussions over many years on the Xournal mailing list
and Xournal++ even had experimental networking support, but it didn't work out.
So I started Cournal, which got networking support just after PDF viewing and
simple drawing was done. Therefore it was designed with networking in mind from 
scratch.

## Does it work yet? ##

Yes, but you might miss some features (to change that, see next section ;-)).

## How to help ##

You are very welcome to support the project!

To get into Cournal hacking, have a look at LINKS.md, which contains a list of
most things you need to know.
Feel free to contact me, if questions arise or if you want to improve Cournal,
but don't know how to get started.

## Dependencies ##

 * Python 3.x
 * Poppler 0.18 or newer
 * Cairo
 * GObject Introspection
 * GTK+ 3.2 or newer (GTK+ 3.4 or newer is strongly recommended)
 * Python bindings for all above this line
 * ZopeInterface 3.6.0 or newer
 * Twisted
 * Build-time: Gettext, Intltool

## Installation ##

There are packages for [Gentoo](https://github.com/flyser/cournal-gentoo)
and [Arch Linux](https://aur.archlinux.org/packages/cournal).
Users of other distributions can use the following guide:

1. [Download the latest Cournal release](https://github.com/flyser/cournal/releases)
2. `tar xvf cournal-?.?.?.tar.gz`
3. `cd cournal-?.?.?`
4. `python3 -m pip install -r requirements.txt`
5. `sudo python3 setup.py install`
6. `cournal`

## Usage ##

##### Server ######

    ./cournal-server.py -p [portnumber]

##### Client ######
    
Start Cournal, select "Annotate PDF" and then "Connect to Server".

## Bugs ##

Please report bugs on <https://github.com/flyser/cournal/issues>.

## File Format ##

The file format is compatible to Xournals .xoj files, but Cournal is not
able to open some .xoj files created by Xournal, because it doesn't support
all features of the file format. The other way around should work though.
