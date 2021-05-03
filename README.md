# FFShark_Wireshark_Integration

FFShark is a hardware network debugging tool developed by J.C. Vega and M.A. Merlini at the University of Toronto through P. Chow’s research group. It can be used in high speed data centers capable of 100G speeds, that is, running at 100 Gbit/s. Our project connects FFShark to the industry standard Wireshark network debugging/analyzer tool.

`ffshark_c_lang_drivers` Set of C drivers to allow interfacing Wireshark with FFShark. These drivers are an alternative to the python drivers of `ffshark_read_packets.py` and `ffshark_send_packets.py`. These C drivers perform much faster than the python drivers, thus further optimizations and improvements should be carried on with the C drivers. Find out more in the README in the ffshark_c_lang_drivers directory.

`ffshark_read_packets.py` Reads packets from FFShark. It then outputs packets into PCAP format so that packets can be displayed on Wireshark. It can also take in filtering instructions for Wireshark as user arguments. Use the `--help` option to see more about it.

`ffshark_send_packets.py` Sends test packets to ffshark. User must provide a directory of packet text files as argument. The script will then randomly select packets from this directory to send to ffshark. Use the `--help` option to see more about it.

`test_packets.py` is used to generate "random" packets. These packets can be stored in a directory, then sent to FFShark with `ffshark_send_packets.py` for testing. Running it with the `--help` option will provide details on all arguments that can be provided.

`sendfilter.c` Configures filtering instruction into FFShark. Was used to generate `sendfilter`. Run `gcc -o sendfilter sendfilter.c -lpcap` to regenerate `sendfilter` after any changes.

`sendfilter` an exe that programs FFShark with a filter. Requires a .bpf file as input.

`compilefilt.c` uses pcap library to compile filtering instructions into raw bpf filter. This was taken from https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/compilefilt. This script currently outputs generated bpf instructions into the terminal. These outputs may need to be disabled to avoid interference of pcap packet transaction through sshdump. Run `gcc -o compilefilt compilefilt.c -lpcap` to regenerate `compilefilt` after any changes.

`compilefilt` an exe that compiles a PCAP filter.

`compile_and_send_filter.py` takes a filtering instruction, compiles it and sends the bpf compiled instructions to FFShark to be configured. Uses `compilefilt` and `sendfilt` to compile and send the filter respectively. This is called by `ffshark_read_packets.py` to allow users to set the packet filter on Wireshark.

`acceptall.bpf` used to reset FFshark filter to accept all packets.

`read_packets.py` is used to read the generated packets into human readable. It can also output packets into PCAP format. Mainly for prototyping and learning purposes. Not officially used in the FFShark reading and writing code. Again, use the `--help` option to see more about it.

## Displaying generated packets on Wireshark

1. I copied the `read_packet.py` script and a random packet in the `sample_packet` directory over to savi@10.10.14.217.
2. Then use "sshdump" on the container and connect to savi. Used capture command as `python3 /home/savi/alex/test_pcap/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/test_pcap/ipv4_tcp_http_100_to_1000_2.txt`. Turn off "use sudo mode" option. Also turn off capture filter.
3. Run and you should see one packet.

### Running two packets

To run two packets, you need to get rid of the "global header" portion of the PCAP file, i.e., the first 24 bytes. Using the `read_packets.py` script, this can be accomplished by using the `--skip-header` option. Example command for sshdump:
`python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/test_pcap/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_3.txt; python3 /home/savi/alex/FFShark_Wireshark_Integration/read_packets.py --pcap /home/savi/alex/FFShark_Wireshark_Integration/test.pcap --pcap-print /home/savi/alex/FFShark_Wireshark_Integration/sample_packets/ipv4_udp_http_100_to_1000_4.txt --skip-header`

More info on running sshdump in general can be found [here](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing).


## Running FFShark with Wireshark Guide

This method gets about 81kbps (kilobits per second) with locking but no contention.

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

## Running FFShark with C driver

This method gets about 35Mbps (megabits per second) without any locking.

1. Ensure no one else using mpsoc
2. On MPSoC,
```
sudo su
set_clocks 100
program ffshark_fifo.bin
exit
```
3. `cd ffshark_c_lang_drivers`
4. Run `make ffshark_read_packets` to compile.
5. On MPSoC, send in packets `./ffshark_send_packets --directory ../sample_packets/multiple_8  --num-packets 5`.
6. On sshdump interface in Wireshark, set capture command to `/home/savi/alex/FFShark_Wireshark_Integration/ffshark_c_lang_drivers/ffshark_read_packets`
7. Once done using MPSoC, send message in Slack to say done using.

## Verifying Correct Packets

1. Run `ffshark_send_packets.py` with the `--save-sent-packets` option. E.g. `python3 ffshark_send_packets.py --packets-directory sample_packets/multiple_8  --num-packets 100 --save-sent-packets "saved_packets.log"`
2. On Wireshark, go to "File->Export Packet Dissections->As Plaintext". Then select "Bytes" as Packet Format and deselect the other two options.
3. Save this file. E.g. "received_packets.txt".
4. Copy over the sent file from MPSoC to the Wireshark machine. `scp savi@10.10.14.215:/home/savi/alex/FFShark_Wireshark_Integration/saved_packets.log saved_packets.log`. If you need to find the location on savi, you can use `realpath <file>` and just copy that.
5. Run `diff <(cat received_packets.txt | sed 's/   .*//g' |  awk '{$1="";  print $0}' | sed 's/ //g') saved_packets.log`. If no differences, you're guchi. This command just changes the formatting from the Wireshark file so it's the same as the output from the Python script.

Note, if we have out of order packets, this technique won't work anymore. We could run a sort beforehand though and then do the diff so we'll know all that data was still sent and received.
For example, you could run `diff <(cat received_packets.txt | sed 's/   .*//g' |  awk '{$1="";  print $0}' | sed 's/ //g' | sort) <(sort saved_packets.log)`. However, our script seems to be too slow to go out of order.

If you need to debug, running, `cat received_packets.txt | sed 's/   .*//g' |  awk '{$1="";  print $0}' | sed 's/ //g'` will be useful to get the same output format as saved_packets.log.

If you're trying to verify multiple separate bursts of sending in data, you'd have to save each one to a different file. Then in Wireshark, you need to select the packets to export that correspond to what you sent in and export a separate file for each.

## ToDo's
- Doesn't look like we ever clean up the interface in ffshark_send/read_packets.py. Should call axilite.clean() at some point. How will interrupts work? Is it safe.
- Need to optimize packet filtering throughput. Currently using AXI FIFO interface. Should try AXI DMA



## Reference Documentation links
- [Getting Started Guide by Marco](https://docs.google.com/document/d/1H1frpdz7j3hkfRUXrA85vH-yZl9hWJdxOMbq-1UOPcI/edit?usp=sharing)
- [Running sshdump Guide](https://docs.google.com/document/d/1tAU0yALlJpX_4MjLjqu0NCp0u5kci2d9fFfR4BA_2AM/edit?usp=sharing)
- [FFShark Communication](https://docs.google.com/document/d/1SDM3wdEPB0RHBpBuTw2Wi3w9HchFavyQuaQHs7gsxgM/edit?usp=sharing)
- [Research Doc](https://docs.google.com/document/d/1Hbxfa8hD-htGJ5gdQOzzTYvQEntfUAAulZ1-j-sQjOk/edit?usp=sharing)
