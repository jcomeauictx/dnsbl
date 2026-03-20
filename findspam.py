#!/usr/bin/python3
'''
find and print out email matching pattern in specified email file

defaults to /var/mail/$USERNAME
'''
import sys, os, pwd, re, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

CHUNKSIZE = 1024 * 1024

def get_email(searchpattern, folder=None):
    '''
    find email matching search pattern
    '''
    offset = -CHUNKSIZE
    searchtext = b''
    folder = folder or os.path.join(
       os.path.sep, 'var', 'mail', pwd.getpwuid(os.geteuid()).pw_name
    )
    pattern = re.compile(searchpattern.encode())
    mailstart = (re.compile(b'^From ', re.M), re.compile(b' morF$', re.M))
    with open(folder, 'rb') as mailfile:
        # `email` is start, matchstart, matchend, end offsets in file (absolute)
        email = None
        try:
            searchstart = position = mailfile.seek(offset, os.SEEK_END)
        except OSError:
            logging.error(
                'cannot seek to end%d from %d, seeking to start instead',
                offset,
                mailfile.tell()
            )
        searchstart = position = mailfile.seek(0)
        endfile = position - offset
        logging.debug('position in file: %d, end: %d', position, endfile)
        while email is None:
            # now seek from start
            searchstart = position = mailfile.seek(position)
            # keep searchtext size limited to CHUNKSIZE * 2
            searchtext = (
                mailfile.read(CHUNKSIZE) + searchtext
            )[:CHUNKSIZE * 2]
            logging.debug(
                'length of searchtext: %d, snippet: %r',
                len(searchtext),
                searchtext[:80]
            )
            match = pattern.search(searchtext)
            if match:
                start, end = match.span()
                found = [position + start, position + end]
                logging.debug(
                    'found match at offset %d: %s, snippet: %r',
                    found[0], match,
                    searchtext[start:end]
                )
                # now tack on another chunk to each end of searchtext
                append = mailfile.read(CHUNKSIZE)
                searchstart = mailfile.seek(max(0, position - CHUNKSIZE))
                prepend = mailfile.read(position - searchstart)
                # reverse the start so we can find ' morF' (envelope From )
                beginning = bytes(reversed(prepend + searchtext[:found[0]]))
                # trim searchtext to start of pattern match before appending
                searchtext = searchtext[found[0]:] + append
                logging.debug('searchtext length now: %d', len(searchtext))
                # reusing `start` and `end` now as match objects
                start = mailstart[1].search(beginning)
                end = mailstart[0].search(searchtext)
                if end:
                    # trim again, to end of email
                    searchtext = searchtext[:end.span()[1]].rstrip()
                else:
                    logging.warning('end of email not found')
                if start:
                    beginning = bytes(reversed(beginning[:start.span()[1]]))
                else:
                    beginning = bytes(reversed(beginning))
                email = beginning + searchtext
            else:
                logging.debug('did not find match, zooming back')
                position += offset
        return email.decode()

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'fakespool.txt':
        CHUNKSIZE = 16  # for testing
    print(get_email(*sys.argv[1:]))
