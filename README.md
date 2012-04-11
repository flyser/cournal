Cournal is a collaborative note taking and journal application using a stylus

## Why? ##

I needed something to allow collaborative annotation of PDF files, Cournal is
therefore heavily inspired by [Xournal](http://xournal.sf.net/) (note taking)
and [Gobby](http://gobby.0x539.de/) (collaboration).

## Aim ##

The ultimate goal of this project is a note taking application similar
to Xournal, that is able to connect to an
[infinote server](http://gobby.0x539.de/trac/wiki/Infinote/Infinoted)
(that's the server software Gobby uses).

But there is a lot to do, before this will work.

## Does it work yet ##

No. See next section ;-)

## How to help ##

You are very welcome to support the project!

If you want to work on the server side of this, clone infinote on
<http://git.0x539.de/?p=infinote.git;a=summary> and write a new library
similar to libinftext, which handles Xournal files instead of text files.
You can find [API documentation here](http://gobby.0x539.de/trac/wiki/APIReference)

Another point on the TODO list is to make GObject Introspection work in
infinote/libinfinity to get python bindings for free.
See <https://live.gnome.org/GObjectIntrospection>

The Client side basicly comes down to PDF rendering with
[poppler](http://people.freedesktop.org/~ajohnson/docs/poppler-glib/),
drawing with [cairo](http://cairographics.org/documentation/pycairo/3/),
saving and loading Xournal files with the XML library of your choice (likely
[ElementTree](http://docs.python.org/library/xml.etree.elementtree.html))
and probably a band-aid networking layer till infinote support is in place.

## Dependencies ##

 * Python 3.x
 * Poppler 0.18 or newer
 * GObject Introspection
 * ZopeInterface
 * GTK+ 3.x

## Usage ##

    cournal pdf-file

## File Format ##

The file format should be compatible to Xournals .xoj files.
