# simple dnsbl

See <https://en.wikipedia.org/wiki/Domain_Name_System-based_blackhole_list>:
If 192.168.42.23 is spamming, create a record 23.42.168.192.dnsbl.example.com,
returning 127.0.0.2 or another address in the 127/8 range.

Example:
```
$ dig 157.20.74.45.bl.spamcop.net

; <<>> DiG 9.20.18-1~deb13u1-Debian <<>> 157.20.74.45.bl.spamcop.net
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 34320
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;157.20.74.45.bl.spamcop.net.	IN	A

;; ANSWER SECTION:
157.20.74.45.bl.spamcop.net. 2100 IN	A	127.0.0.2
```

<https://cabulous.medium.com/dns-message-how-to-read-query-and-response-message-cfebcb4fe817>
