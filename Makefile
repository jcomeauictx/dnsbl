DNSBL_HOST ?= ::1
DNSBL_PORT ?= 5353
DNSBL_DIRECTORY ?= /tmp/dnsbl
sources := $(wildcard *.py)
export
test:	dnsbl.py lint doctests
	mkdir -p $(DNSBL_DIRECTORY)
	touch $(DNSBL_DIRECTORY)/example.net
	sudo which ngrep  # force typing sudo password here if necessary
	sudo timeout 6 ngrep -e -x -dlo . port $(DNSBL_PORT) &
	sleep 1  # give ngrep time to start up
	timeout 5 ./$< 1 &
	sleep 1  # give dnsbl.py time to start up
	dig example.net -p $(DNSBL_PORT) @$(DNSBL_HOST) +tries=1
	rm $(DNSBL_DIRECTORY)/example.net
%.lint: %.py
	pylint3 $<
lint: $(sources:.py=.lint)
%.doctest: %.py
	python3 -m doctest $<
doctests: $(sources:.py=.doctest)
