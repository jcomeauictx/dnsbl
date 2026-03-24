install: /etc/init.d/location
/etc/init.d/%: %
	cp -i $< $@
	chmod 0744 $@
	rc-update add $* default
	rc-service $* start
