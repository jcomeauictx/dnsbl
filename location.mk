SHELL := /bin/bash
install: /etc/init.d/location | .installed/coreutils
/etc/init.d/%: % /root/.local/bin/location.sh
	[ -w "$(@D)" ] || (echo Must be root to install >&2; false)
	cp -i $< $@
	chmod 0744 $@
	rc-update add $* default
	rc-service $* start
/root/.local/bin/%: %
	[ -w /root ] || (echo Must be root to install >&2; false)
	rm -f $@
	mkdir -p $(@D)
	cp $* $@
.installed/coreutils: | .installed
	apk add $(@F) || true  # don't fail on non-Alpine system
	touch $@
.installed:
	mkdir $@
.PRECIOUS: /root/.local/bin/% /etc/init/%
