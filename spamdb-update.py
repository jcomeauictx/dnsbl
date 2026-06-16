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

    >>> updatedb('pixiedust.example.net', 'pixiedust.example.net fake msgid')
    >>> updatedb('240.241.242.243', '240.241.242.243 fake message id')
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

def networks(octets, minbits=8, maxbits=30, sep='/'):
    '''
    construct all valid networks for the given address

    >>> networks([127, 0, 0, 1])
    ['127.0.0.0/30', '127.0.0.0/29', '127.0.0.0/28', '127.0.0.0/27', '127.0.0.0/26', '127.0.0.0/25', '127.0.0.0/24', '127.0.0.0/23', '127.0.0.0/22', '127.0.0.0/21', '127.0.0.0/20', '127.0.0.0/19', '127.0.0.0/18', '127.0.0.0/17', '127.0.0.0/16', '127.0.0.0/15', '127.0.0.0/14', '127.0.0.0/13', '127.0.0.0/12', '127.0.0.0/11', '127.0.0.0/10', '127.0.0.0/9', '127.0.0.0/8']
    '''
    result = [
        network(octets, bits, sep, True)
        for bits in range(maxbits, minbits - 1, -1)
    ]
    logging.debug('networks: %s', networks)
    return result

def network(octets, maskbits=32, sep='/', correct=False):
    '''
    construct a network address from octets and maskbits

    check that the corresponding integer is inside the mask (set correct=True
    to change network address to fit)
    
    may need to use a different sep(arator) for filenames, perhaps '.'

    >>> network([127, 0, 0, 1])
    '127.0.0.1/32'
    >>> network([5, 0, 0, 0], 8, sep='.')
    '5.0.0.0.8'
    >>> network([127, 0, 0, 1], 8)
    '''
    octets = map(int, octets)
    reduced = int.from_bytes(octets, 'big')
    logging.debug('octets: %s, reduced: 0x%08x', octets, reduced)
    # convert maskbits into mask
    mask = int(''.rjust(maskbits, '1').ljust(32, '0'), 2)
    if reduced & ~mask:
        if not correct:
            logging.error('network address %s cannot have mask %s',
                          ipv4(reduced), ipv4(mask))
            return None
        else:
            reduced = reduced & mask
    return sep.join([ipv4(reduced), str(maskbits)])

def ipv4(netaddress):
    '''
    convert integer to dotted-quad format

    ipv4(1)
    '0.0.0.1'
    '''
    return '.'.join(map(str, netaddress.to_bytes(4, 'big')))

def integer(dottedquad):
    '''
    convert dotted-quad network address to integer

    >>> hex(integer('127.0.0.1'))
    '0x7f000001'
    '''
    octets = map(int, dottedquad.split('.'))
    return int.from_bytes(octets, 'big')

if __name__ == '__main__':
    updatedb(*sys.argv[1:])
