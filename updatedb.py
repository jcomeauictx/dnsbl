#!/usr/bin/python
'''
updatedb adds information to the spamdb directory, progressively merging
spamming IP numbers into larger and larger networks, starting at /32,
then /30 and decrementing by 1 all the way to /8.

this eventually should be a 24-hour server, possibly a uwsgi script, but
will start out as a simple script run from exim4 for every spam email
caught by spamassassin or the existing blocklists/blacklists.
'''
import sys, os  # pylint: disable=multiple-imports
from datetime import datetime

def updatedb(source, message_id=None):
    '''
    update database with information on spam received from source
    '''
    parts = source.split('.')
    if all(map str.isdigit, parts):
        ipnumber = network(parts)
        domainname = None
    else:
        domainname = source
        parts = reversed(parts)
        ipnumber = None
    path = os.path.join(os.curdir, 'spamdb', *parts, source)
    os.makedirs(os.path.dirname(path), exists_ok=True)
    with open(path, 'a') as outfile:
        outfile.write(message_id)

def network(octets, maskbits=32):
    '''
    construct an integer from octets and maskbits

    check that the resulting number is inside the mask
    '''
    integers = map(int, octets)
    reduced = int.from_bytes(integers, 'big')

if __name__ == '__main__':
    updatedb(*sys.argv[1:])
