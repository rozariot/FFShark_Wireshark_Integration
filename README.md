# FFShark_Wireshark_Integration

`test_packets.py` is used to generate "random" packets. Running it with the `--help` option will provide details on all arguments that can be provided.

`read_packets.py` is used to read the generated packets into human readable. It can also output packets into PCAP format. Again, use the `--help` option to see more about it.

`pcap_formatter.py` is used to read a packet stored as a binary file (.bin) and formats it into pcap format. Use `-h` to see what to place as arguments.

`spoke.sh` is a wrapper around "poke" to use a locking file so only one thread may run poke at a time. Otherwise we can end up with corrupted data if we use "poke" in multithreaded situations.

`sdpoke.sh` is a wrapper around "dpoke" to use a locking file so only one thread may run poke/dpoke at a time. Otherwise we can end up with corrupted data if we use "poke" or "dpoke" in multithreaded situations.

`send_file_safe.sh` thread safe version of send_file.sh. Takes an input packet text file and sends it to ffshark.

`ffshark_send_packets.py` used to send packets to ffshark. user must provide a directory of packet text files as argument. the script will then randomly select packets from this directory to send to ffshark. this script uses `send_file_safe.sh` to send the packets. use the `--help` option to see more about it.

## Displaying generated packets on Wireshark

1. I copied the `read_packet.py` script and a random packet in the `sample_packet` directory over to savi@10.10.14.217.
2. Then use "sshdump" on the container and connect to savi. Used capture command as `python3 /home/savi/alex/test_pcap/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/test_pcap/ipv4_tcp_http_100_to_1000_2.txt`. Turn off "use sudo mode" option. Also turn off capture filter.
3. Run and you should see one packet.

More info on running sshdump in general can be found [here](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing).


## Issues
- Right now we're writing the PCAP file to an actual file first, then reading it and printing to terminal. This seems unecessary and we should see if we can print directly.

- Have only tried with one packet at a time. How to do two packets?

- savi only has scapy installed for Python3 so need to use that version. I mostly tested using Python2.7, so there could be some new bugs due to different versions. pip is not installed on savi, so I'd need to install it if we want it to run in Python2.7


## Useful links
- [Getting Started Guide by Marco](https://docs.google.com/document/d/1H1frpdz7j3hkfRUXrA85vH-yZl9hWJdxOMbq-1UOPcI/edit?usp=sharing)
- [Running sshdump Guide](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing)
- [FFShark Communication](https://docs.google.com/document/d/1SDM3wdEPB0RHBpBuTw2Wi3w9HchFavyQuaQHs7gsxgM/edit?usp=sharing)
- [Research Doc](https://docs.google.com/document/d/1Hbxfa8hD-htGJ5gdQOzzTYvQEntfUAAulZ1-j-sQjOk/edit?usp=sharing)
