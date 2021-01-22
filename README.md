# FFShark_Wireshark_Integration

`test_packets.py` is used to generate "random" packets. Running it with the `--help` option will provide details on all arguments that can be provided.

`read_packets.py` is used to read the generated packets into human readable. It can also output packets into PCAP format. Again, use the `--help` option to see more about it.

`pcap_formatter.py` is used to read a packet stored as a binary file (.bin) and formats it into pcap format. Use `-h` to see what to place as arguments.

`spoke.sh` is a wrapper around "poke" to use a locking file so only one thread may run poke at a time. Otherwise we can end up with corrupted data if we use "poke" in multithreaded situations.

`sdpoke.sh` is a wrapper around "dpoke" to use a locking file so only one thread may run poke/dpoke at a time. Otherwise we can end up with corrupted data if we use "poke" or "dpoke" in multithreaded situations.

`send_file_safe.sh` thread safe version of send_file.sh. Takes an input packet text file and sends it to ffshark.

`send_file.sh` thread unsafe version of send_file.sh. Takes an input packet text file and sends it to ffshark.

`ffshark_send_packets.py` used to send packets to ffshark. user must provide a directory of packet text files as argument. the script will then randomly select packets from this directory to send to ffshark. this script uses `send_file_safe.sh` to send the packets. use the `--help` option to see more about it.

`receive_file.sh` used to read a packet from the receive FIFO in FFShark. This is the thread unsafe version.

`reg_names.sh` a script that loads the registers offsets for FFShark into a bash shell.

`sendfilter` an exe that programs FFShark with a filter. Requires a .bpf file as input.

`compile_filter.py` gets a filtering instruction through sshdump, and calls the `compilefilt` executable generated from `compilefilt.c` source code to compile a .bpf file containing the filtering instructions. The .bpf file will then need to be sent to the fpga. This code is mainly just for testing how to send a filtering instruction to the ARM chip through SSHdump.

`compilefilt.c` uses pcap library to compile filtering instructions into raw bpf filter. This was taken from https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/compilefilt. This script currently outputs generated bpf instructions into the terminal. These outputs may need to be disabled to avoid interference of pcap packet transaction through sshdump. Run `gcc -o compilefilt compilefilt.c -lpcap` to regenerate `compilefilt` after any changes.

`compile_and_send_filter.py` takes a filtering instruction, compiles it and sends the bpf compiled instructions to FFShark to be configured. Uses `compilefilt` and `sendfilt` to compile and send the filter respectively. This will most likely be called by `ffshark_read_packets.py`, which will need to use `compile_filter.py`'s strategy for taking in user input for filtering instructions

## Displaying generated packets on Wireshark

1. I copied the `read_packet.py` script and a random packet in the `sample_packet` directory over to savi@10.10.14.217.
2. Then use "sshdump" on the container and connect to savi. Used capture command as `python3 /home/savi/alex/test_pcap/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/test_pcap/ipv4_tcp_http_100_to_1000_2.txt`. Turn off "use sudo mode" option. Also turn off capture filter.
3. Run and you should see one packet.

### Running two packets

To run two packets, you need to get rid of the "global header" portion of the PCAP file, i.e., the first 24 bytes. Using the `read_packets.py` script, this can be accomplished by using the `--skip-header` option. Example command for sshdump:
`python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_3.txt; python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/FFShark_Wireshark_Integration/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_4.txt --skip-header`

More info on running sshdump in general can be found [here](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing).


## Running FFShark with Wireshark Guide

1. Ensure no one else using mpsoc
2. On MPSoC,
```
sudo su
set_clocks 100
program ffshark_fifo.bin
exit
```
3. On MPSoC, send in packets `python3 ffshark_send_packets.py --packets-directory sample_packets/multiple_8  --num-packets 100`
4. On sshdump interface in Wireshark, set capture command to `python3 /home/savi/alex/FFShark_Wireshark_Integration/ffshark_read_packets.py`. Can also add a filter like `python3 /home/savi/alex/FFShark_Wireshark_Integration/ffshark_read_packets.py --capture-filter=udp` or set to "tcp".
5. Once done using MPSoC, send message in Slack to say done using.

### Debug log of issue with multiple packets
Issue was the read script increased iteration even if no packet was read. This meant we would always skip header if starting later.

## Issues

- Doesn't look like we ever clean up the interface in ffshark_send/read_packets.py. Should call axilite.clean() at some point. How will interrupts work? Is it safe.
- Still not certain we don't ocassionally hang the board. Is something not thread safe??
- Right now we're writing the PCAP file to an actual file first, then reading it and printing to terminal. This seems unecessary and we should see if we can print directly.



## Useful links
- [Getting Started Guide by Marco](https://docs.google.com/document/d/1H1frpdz7j3hkfRUXrA85vH-yZl9hWJdxOMbq-1UOPcI/edit?usp=sharing)
- [Running sshdump Guide](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing)
- [FFShark Communication](https://docs.google.com/document/d/1SDM3wdEPB0RHBpBuTw2Wi3w9HchFavyQuaQHs7gsxgM/edit?usp=sharing)
- [Research Doc](https://docs.google.com/document/d/1Hbxfa8hD-htGJ5gdQOzzTYvQEntfUAAulZ1-j-sQjOk/edit?usp=sharing)
