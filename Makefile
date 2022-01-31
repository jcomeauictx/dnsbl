test:	dnsbl.py
	sudo ngrep -e -x -dlo . port 5353 &
	./$< &
	dig example.net -p 5353 @localhost
	kill -1
