#!/bin/bash
# iOS keeps apps open in background only 30 seconds unless
# location being actively used.
# https://medium.com/@der.loste.kitkat/get-started-with-ish-b29add1f72a3
while read line; do
 echo $line
 sleep 15
done < /dev/location
