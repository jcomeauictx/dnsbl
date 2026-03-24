SHELL := /bin/bash
install: /etc/init.d/location
/etc/init.d/%: % /root/.local/bin/location.sh
	sudo cp -i $< $@
	sudo chmod 0744 $@
	sudo rc-update add $* default
	sudo rc-service $* start
/root/.local/bin/%: %
	sudo ln -sf $(PWD)/$* $@
