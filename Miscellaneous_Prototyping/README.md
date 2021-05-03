This directory contains scripts we have used to prototype aspects of our design

## Displaying generated packets on Wireshark (without going through FFShark)

1. Copy the `read_packet.py` script and a random packet in the `sample_packet` directory over to savi@10.10.14.215.
2. Then use "sshdump" on the container and connect to savi. Used capture command as `python3 /home/savi/alex/test_pcap/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/test_pcap/ipv4_tcp_http_100_to_1000_2.txt`. Turn off "use sudo mode" option. Also turn off capture filter.
3. Run and you should see one packet.

### Running two packets  (without going through FFShark)

To run two packets, you need to get rid of the "global header" portion of the PCAP file, i.e., the first 24 bytes. Using the `read_packets.py` script, this can be accomplished by using the `--skip-header` option. Example command for sshdump:
`python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_3.txt; python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/FFShark_Wireshark_Integration/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_4.txt --skip-header`

More info on running sshdump in general can be found [here](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing).
