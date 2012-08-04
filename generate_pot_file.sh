#!/bin/bash

set -e
shopt -s extglob
shopt -s globstar

cd "$(dirname "$0")"

PACKAGE="Cournal"
VERSION=$(grep "__versionstring__ = \".*\"" cournal/__init__.py | cut -f 2 -d \")
OUTPUT="cournal.pot"
AUTHOR="Fabian Henze"
BUGTRACKER="https://github.com/flyser/cournal/issues"

# Generate .glade.h files
for file in cournal/*.glade ; do
  intltool-extract --type=gettext/glade "$file"
done
for file in *.desktop.in ; do
  intltool-extract --type=gettext/ini "$file"
done

# Create .pot file
xgettext --output="$OUTPUT" --language=Python --package-name="$PACKAGE" \
         --copyright-holder="$AUTHOR" --package-version="$VERSION" \
         --msgid-bugs-address="$BUGTRACKER" --from-code=UTF-8 \
         --keyword=N_ --keyword=_ *.py cournal/*.py cournal/!(twisted)/**/*.py cournal/*.h *.h
sed -i -e "2s/YEAR/$(date +%Y)/" "$OUTPUT"

# Clean up
for file in cournal/*.glade.h *.desktop.in.h ; do
  rm "$file"
done

echo ; echo "Created \"$OUTPUT\""
echo "New:    msginit -i cournal.pot --locale=de_DE -o i18n/de.po"
echo "Update: msgmerge --update i18n/de.po cournal.pot"
