#!/usr/bin/python
'''
updatedb adds information to the spamdb directory, progressively merging
spamming IP numbers into larger and larger networks, starting at /32,
then /30 and decrementing by 1 all the way to /8.

this eventually should be a 24-hour server, possibly a uwsgi script, but
will start out as a simple script run from exim4 for every spam email
caught by spamassassin or the existing blocklists/blacklists.
'''
import sys, os, logging  # pylint: disable=multiple-imports
#from datetime import datetime
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

def updatedb(source, message_id=None):
    '''
    update database with information on spam received from source
    '''
    parts = source.split('.')
    if all(map(str.isdigit, parts)):
        ipnumber = network(parts)
        domainname = None
    else:
        domainname = source
        parts = reversed(parts)
        ipnumber = None
    logging.debug('updatedb: domainname=%s, ipnumber=%s',
                  domainname, ipnumber)
    path = os.path.join(os.curdir, 'spamdb', *parts, source)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as outfile:
        outfile.write(message_id)

def network(octets, maskbits=32):
    '''
    construct an integer from octets and maskbits

    check that the resulting number is inside the mask

    >>> network([127, 0, 0, 1])
    '127.0.0.1/32'
    >>> network([5, 0, 0, 0], 8)
    '5.0.0.0/8'
    >>> network([127, 0, 0, 1], 8)
    '''
    octets = map(int, octets)
    reduced = int.from_bytes(octets, 'big')
    logging.debug('octets: %s, reduced: 0x%08x', octets, reduced)
    # convert maskbits into mask
    mask = int(''.rjust(maskbits, '1').ljust(32, '0'), 2)
    if reduced & ~mask:
        logging.error('network address %s cannot have mask %s',
                      ipv4(reduced), ipv4(mask))
        return None
    return '/'.join([ipv4(reduced), str(maskbits)])

def ipv4(netaddress):
    '''
    convert integer to dotted-quad format
    '''
    return '.'.join(map(str, netaddress.to_bytes(4, 'big')))

if __name__ == '__main__':
    updatedb(*sys.argv[1:])
