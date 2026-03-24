SHELL := /bin/bash
install: /etc/init.d/location
/etc/init.d/%: % /root/.local/bin/location.sh
	[ -w "$(@D)" ] || (echo Must be root to install >&2; false)
	cp -i $< $@
	chmod 0744 $@
	rc-update add $* default
	rc-service $* start
/root/.local/bin/%: %
	[ -w "$(@D)" ] || (echo Must be root to install >&2; false)
	rm -f $@
	cp $(PWD)/$* $@
.PRECIOUS: /root/.local/bin/% /etc/init/%
