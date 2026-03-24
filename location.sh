#!/bin/bash
# iOS keeps apps open in background only 30 seconds unless
# location being actively used.
# https://medium.com/@der.loste.kitkat/get-started-with-ish-b29add1f72a3
# example output of /dev/location:
# +24.163419,-110.311692
DEBUGGING=$1
LOGDIR=/var
if [ ! -w $LOGDIR ]; then LOGDIR=$HOME$LOGDIR; fi
LOGDIR=$LOGDIR/log/location
if [ "$DEBUGGING" ]; then echo LOGDIR=$LOGDIR >&2; fi
mkdir -p -m 0755 $LOGDIR
lastseen=
while read line; do
 timestamp=$(date -u --iso-8601=ns)
 date=${timestamp%%T*}
 if [ "$DEBUGGING" ]; then echo $date $timestamp $line >&2; fi
 if [ "$line" != "$lastseen" ]; then
  echo $timestamp ${line%%,*} ${line##*,} >> $LOGDIR/$date.log
  lastseen=$line
 fi
 sleep 15
done < /dev/location
