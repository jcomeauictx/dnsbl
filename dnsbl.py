#!/usr/bin/python3
'''
Simple DNS block list (DNSBL), using addresses generated by another script
'''
import sys, os, re, socket, struct, logging  # pylint: disable=multiple-imports

DEFAULT_DIRECTORY = os.path.join('', 'var', 'dnsbl')
DNSBL_DIRECTORY = os.getenv('DNSBL_DIRECTORY', DEFAULT_DIRECTORY)
DNSBL_HOST = os.getenv('DNSBL_HOST', '::1')
DNSBL_PORT = int(os.getenv('DNSBL_PORT', '5353'))
DNSBL_DOMAIN = os.getenv('DNSBL_DOMAIN', 'dnsbl.gnixl.com')
DNSBL_DOMAIN_ASLIST = DNSBL_DOMAIN.split('.')
DNSBL_DOMAIN_PATTERN = DNSBL_DOMAIN.replace('.', '[.]')
PATTERN = re.compile(r'^(\d+\.\d+\.\d+\.\d+)\.%s$' % DNSBL_DOMAIN_PATTERN)
STANDARD = 0x100  # standard query
DNSSEC = 0x20
EXPECTED = STANDARD | DNSSEC

logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

def dnsbl(loop=sys.maxsize):
    '''
    listen for queries and return valid response or NXDOMAIN if not found

    https://realpython.com/python-sockets/
    https://pythontic.com/modules/socket/udp-client-server-example
    '''
    with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as server:
        server.bind((DNSBL_HOST, DNSBL_PORT))
        logging.debug('DNSBL listening...')
        while loop > 0:
            logging.debug('%d loops remaining', loop)
            query, address = server.recvfrom(512)
            parsed, txid = parse(query)
            logging.debug('query: %r, parsed: %r, from %s',
                          query, parsed, address)
            server.sendto(reply(txid, parsed), 0, address)
            loop -= 1
        logging.debug('dnsbl server exiting')

def reply(txid, lookup):
    '''
    reply to address with 127.0.0.2 or NXDomain
    '''
    response = short(txid)  # will contain txid in any case
    path = os.path.join(DNSBL_DIRECTORY, lookup) if lookup else None
    if path and os.path.exists(path):
        response += short(0x8180)  # good answer
        # one question, one answer, no authority, no additional
        response += short(0x1) + short(0x1) + short(0) + short(0)
        response += dnsname(lookup)
        # type 1 ('A', host address), class 1 (IN, Internet address),
        # offset (0xc0) to 1st byte of name (0x0c, 12 bytes into record)
        response += short(0x1) + short(0x1) + short(0xc00c)
    else:
        response += short(0x8183)  # NXDomain
    return response


def ipaddress(host):
    r'''
    convert DNSBL-formatted hostname to matching IP address

    >>> ipaddress('4.3.2.1.dnsbl.gnixl.com')
    '1.2.3.4'
    >>> ipaddress('gnixl.com')
    '''
    match = PATTERN.match(host)
    return reverse(match.group(1)) if match else None

def reverse(ip_address):
    r'''
    reverse octets of IP address

    >>> reverse('1.2.3.4')
    '4.3.2.1'
    '''
    return '.'.join(reversed(ip_address.split('.')))

def hostname(ip_address):
    r'''
    convert IP address to matching DNSBL-formatted hostname

    >>> hostname('1.2.3.4')
    '4.3.2.1.dnsbl.gnixl.com'
    '''
    return '.'.join((reverse(ip_address), DNSBL_DOMAIN))

def short(number):
    r'''
    convert number from network short to int and vice versa

    >>> short(b'\x00\x01')
    1
    >>> short(1)
    b'\x00\x01'
    '''
    try:
        return struct.pack('>H', number)
    except struct.error:
        return struct.unpack('>H', number)[0]

def parse_name(query):
    r'''
    return hostname if Internet host address specified

    >>> query=b'\x07example\x03net\x00\x00\x01\x00\x01\x00\x00'
    >>> parse_name(query)
    'example.net'
    '''
    count = offset = 0
    name = []
    while query[offset] != 0:
        count = query[offset]
        name.append(query[offset + 1:offset + 1 + count].decode())
        offset += count + 1
    querytype = short(query[offset + 1:offset + 3])
    queryclass = short(query[offset + 3:offset + 5])
    logging.debug('name: %s, type: %d, class: %d', name, querytype, queryclass)
    return '.'.join(name) if querytype == queryclass == 1 else None

def dnsname(host_name):
    r'''
    turn host name into DNS format

    >>> dnsname('abcdef.com')
    b'\x06abcdef\x03com\x00'
    '''
    # add empty (0-byte) segment at end
    parts = host_name.encode().split(b'.') + [b'']
    lengths = [len(s) for s in parts] + [0]
    return b''.join([bytes([lengths[i]]) + parts[i] for i in range(len(parts))])

def standard(flags):
    '''
    Check if standard query

    >>> standard(0x101)
    False
    >>> standard(0x120)
    True
    >>> standard(0x100)
    True
    >>> standard(0x80)
    False
    '''
    return flags & ~EXPECTED == 0 and flags & EXPECTED in [STANDARD, EXPECTED]

def parse(query):
    '''
    strip header off query and return the parts
    '''
    txid = short(query[:2])
    flags = short(query[2:4])
    questions = short(query[4:6])
    answers = short(query[6:8])
    authority = short(query[8:10])
    additional = short(query[10:12])
    query = query[12:]
    logging.debug('txid: 0x%04x, flags: 0x%04x, questions: %d',
                  txid, flags, questions)
    logging.debug('answers: %d, authority: %d, additional: %d',
                  answers, authority, additional)
    return parse_name(query) if standard(flags) else None, txid

if __name__ == '__main__':
    sys.argv.append(str(sys.maxsize))  # default
    dnsbl(loop=int(sys.argv[1]))
