DNSBL_HOST ?= ::1
DNSBL_PORT ?= 5353
export
test:	dnsbl.py
	sudo which ngrep  # force typing sudo password here if necessary
	sudo timeout 6 ngrep -e -x -dlo . port $(DNSBL_PORT) &
	sleep 1  # give ngrep time to start up
	timeout 5 ./$< &
	sleep 1  # give dnsbl.py time to start up
	dig example.net -p $(DNSBL_PORT) @$(DNSBL_HOST) +tries=1
