# simple dnsbl

See <https://en.wikipedia.org/wiki/Domain_Name_System-based_blackhole_list>:
If 192.168.42.23 is spamming, create a record 23.42.168.192.dnsbl.example.com,
returning 127.0.0.2 or another address in the 127/8 range.

<https://cabulous.medium.com/dns-message-how-to-read-query-and-response-message-cfebcb4fe817>
