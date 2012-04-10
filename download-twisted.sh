#!/bin/sh
# 
# This script will download or update twisted for python3
 
cd $(dirname "$0")

ln -sf t3k/twisted twisted

if [ -e "./t3k" ]; then
  if cd "./t3k" && hg update ; then
    echo "Successfully updated twisted for python3"
    hg merge # might fail if no changes happened in the hg repository
  else
    echo "Update failed, try to delete the t3k folder and run this script again"
  fi
else
  hg clone https://bitbucket.org/pitrou/t3k && \
  echo "Successfully downloaded twisted for python3"
fi

