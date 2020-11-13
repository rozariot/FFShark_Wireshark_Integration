# Sample Packets Info

These packets were generated using the `test_packets.py` script. The eEhernet MAC and IP addresses are all randomly generated.

## Naming convention
`<network_layer>_<transport_layer>_<application_layer>_<min>_to_<max>.txt`

### HTTP
For HTTP, the payload is randomly generated letters, digits, and spaces of size varying between min to max.
The type is an HTTP request.

### DNS
For DNS, the payload is simply some URL.
The type is a DNS query request.

### Raw
This is just a raw packet with some random string of size varying between min to max.

## Commands to generate files
```
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ for i in {1..10}
> do
> ../test_packets.py --layer-network IPv4 --layer-transport TCP --layer-application HTTP --rand-payload-min 100 --rand-payload-max 1000 > ipv4_tcp_http_100_to_1000_${i}.txt
> done

alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ for i in {1..10} ; do ../test_packets.py --layer-network IPv6 --layer-transport TCP --layer-application HTTP --rand-payload-min 100 --rand-payload-max 1000 > ipv6_tcp_http_100_to_1000_${i}.txt; done

alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ for i in {1..10} ; do ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application HTTP --rand-payload-min 100 --rand-payload-max 1000 > ipv4_udp_http_100_to_1000_${i}.txt; done

alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application DNS --payload www.google.ca > ipv4_udp_dns_1.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application DNS --payload www.utoronto.ca > ipv4_udp_dns_2.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application DNS --payload www.wikipedia.com > ipv4_udp_dns_3.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application DNS --payload www.alexbuck.ca > ipv4_udp_dns_4.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv4 --layer-transport UDP --layer-application DNS --payload www.canada.gov > ipv4_udp_dns_5.txt

alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv6 --layer-transport UDP --layer-application DNS --payload www.google.ca > ipv6_udp_dns_1.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv6 --layer-transport UDP --layer-application DNS --payload www.utoronto.ca > ipv6_udp_dns_2.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv6 --layer-transport UDP --layer-application DNS --payload www.wikipedia.com > ipv6_udp_dns_3.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv6 --layer-transport UDP --layer-application DNS --payload www.alexbuck.ca > ipv6_udp_dns_4.txt
alex@capstone:~/FFShark_Wireshark_Integration/sample_packets$ ../test_packets.py --layer-network IPv6 --layer-transport UDP --layer-application DNS --payload www.canada.gov > ipv6_udp_dns_5.txt

```


