#!/usr/bin/python3

import sys
import os.path
from scapy.all import *
from scapy.layers.http import *
import argparse
import string
import random
import binascii



def main(args):
    parser = argparse.ArgumentParser(description="Reads one random packet from a file as hex. No arguments will print packet in human readable form")
    parser.add_argument("--hexdump", action="store_true", help="Prints a hexdump of the packet")
    parser.add_argument("--summary", action="store_true", help="Prints a summary of the packet")
    parser.add_argument("--binary", action="store_true", help="Outputs the packet as binary")
    parser.add_argument("--pcap", action="store", help="Output as PCAP file format to file provided as argument.")
    parser.add_argument("--pcap-print", action="store_true", help="If pcap option selected above, also print the pcap to stdout.")
    parser.add_argument("--skip-header", action="store_true", help="If pcap-print option selected above, will not print the header portion.")
    parser.add_argument("filename", action="store", help="The file where packet is stored")

    args = parser.parse_args(args)

    if (not os.path.isfile(args.filename)):
        sys.stderr.write("Error. Provided input file does not exist")
    with open(args.filename, 'r') as file:
        packet_str = file.read().strip('\n')

    packet = Ether(binascii.a2b_hex(packet_str))

    if (args.hexdump):
        hexdump(packet)
    if (args.summary):
        print(packet.summary())
    if (args.binary):
        sys.stdout.buffer.write(raw(packet))
        # print(packet)
    if (args.pcap):
        # print(PcapWriter(packet))
        wrpcap(args.pcap, packet)
        if (args.pcap_print):
            with open(args.pcap, 'rb') as file:
                if (args.skip_header):
                    stripped = file.read()[24:]
                    sys.stdout.buffer.write(stripped)
                else:
                    sys.stdout.buffer.write(file.read())
    if (not args.hexdump and not args.summary and not args.binary and not args.pcap):
        packet.show2()


    return 0


if __name__ == "__main__":
    main(sys.argv[1:])

