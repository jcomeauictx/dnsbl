DNSBL_HOST ?= ::1
DNSBL_PORT ?= 35353
DNSBL_DIRECTORY ?=
WHICH ?= command -v
PYLINT ?= $(word 1, $(shell $(WHICH) pylint pylint3 2>/dev/null))
SOURCES := $(wildcard *.py)
PYTHON ?= $(word 1, $(shell $(WHICH) python3 python 2>/dev/null))
ifneq ($(SHOWENV),)
export
else
export DNSBL_HOST DNSBL_PORT DNSBL_DIRECTORY
endif
default: test.spam run
test:	dnsbl.py lint doctests
	mkdir -p $(DNSBL_DIRECTORY)
	touch $(DNSBL_DIRECTORY)/example.net
	sudo which ngrep  # force typing sudo password here if necessary
	sudo timeout 6 ngrep -e -x -dlo . port $(DNSBL_PORT) &
	sleep 1  # give ngrep time to start up
	timeout 5 ./$< 2 &
	sleep 1  # give dnsbl.py time to start up
	dig example.net -p $(DNSBL_PORT) @$(DNSBL_HOST) +tries=1
	dig nonesuch.none -p $(DNSBL_PORT) @$(DNSBL_HOST) +tries=1
	rm $(DNSBL_DIRECTORY)/example.net
%.lint: %.py
	$(PYLINT) $<
test.spam: findspam.py
	$(PYTHON) $< abc@xyz fakespool.txt
%.spam: findspam.py
	$(PYTHON) $< "$(@:.spam=)"
lint: $(SOURCES:.py=.lint)
%.doctest: %.py
	python3 -m doctest $<
tests doctests: $(SOURCES:.py=.doctest)
run: dnsbl.py
	python3 $<
env:
ifeq ($(SHOWENV),)
	$(MAKE) SHOWENV=1 $@
else
	$@
endif
