#!/bin/bash
# iOS keeps apps open in background only 30 seconds unless
# location being actively used.
# https://medium.com/@der.loste.kitkat/get-started-with-ish-b29add1f72a3
DEBUGGING=$1
LOGDIR=/var
if [ ! -w $LOGDIR ]; then LOGDIR=$HOME$LOGDIR; fi
LOGDIR=$LOGDIR/location
if [ "$DEBUGGING" ]; then echo LOGDIR=$LOGDIR >&2; fi
mkdir -p $LOGDIR
while read line; do
 timestamp=$(date -u --iso-8601=ns)
 date=${timestamp%%T*}
 if [ "$DEBUGGING" ]; then echo $date $timestamp $line >&2; fi
 echo $timestamp ${line%%,*} ${line##*,}
 sleep 15
done < /dev/location
