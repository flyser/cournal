Cournal is a collaborative note taking and journal application using a stylus.

## Why? ##

I need something to allow collaborative annotation of PDF files, Cournal is
therefore heavily inspired by [Xournal](http://xournal.sf.net/) (note taking)
and [Gobby](http://gobby.0x539.de/) (collaboration).

## Aim ##

The goal of this project is a note taking application similar
to Xournal, but with networking support.

### Why not extend Xournal? ###

There has been numerous discussions over many years on the Xournal mailing list
and Xournal++ even had experimental networking support, but it didn't work out.
So I started Cournal, which got networking support just after PDF viewing and
simple drawing was done. Therefore it is designed with networking in mind from 
scratch.

## Does it work yet ##

Yes, but you might miss some features (to change that, see next section ;-)). 

## How to help ##

You are very welcome to support the project!

To get into Cournal hacking, have a look at LINKS.md, which contains a list of
most things you need to know.
Feel free to contact me, if questions arise or if you want to improve Cournal,
but don't know what needs work.

## Dependencies ##

 * Python 3.x
 * Poppler 0.18 or newer
 * GObject Introspection
 * ZopeInterface 3.6.0 or newer
 * GTK+ 3.x
 * Twisted for python3 (download script: download-twisted.sh)

## Installation ##

A proper installation is unsupported at the moment. To download twisted for
python3, run
    ./download-twisted.sh
in Cournals base directory

Patches to support system-wide installation are very welcome.

## Usage ##

##### Server ######

    cournal-server.py -p [portnumber]

##### Client ######
    
Start Cournal, select "Annotate PDF" and then "Connect to Server".

## File Format ##

The file format is compatible to Xournals .xoj files, but Cournal might not be
able to open some .xoj files created by Xournal, because it doesn't support
all features of the file format. The other way around should work though.
