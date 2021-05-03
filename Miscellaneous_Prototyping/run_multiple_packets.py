#!/usr/bin/python3

import sys
import os.path
from scapy.all import *
from scapy.layers.http import *
import argparse
import string
import random
import binascii
import glob
import time
import read_packets


def main():
    parser = argparse.ArgumentParser(description="Will output multiple packets for Wireshark testing with multiple packets.")
    # parser.add_argument("--hexdump", action="store_true", help="Prints a hexdump of the packet")
    # parser.add_argument("--summary", action="store_true", help="Prints a summary of the packet")
    # parser.add_argument("--binary", action="store_true", help="Outputs the packet as binary")
    # parser.add_argument("--pcap", action="store", help="Output as PCAP file format to file provided as argument.")
    # parser.add_argument("--pcap-print", action="store_true", help="If pcap option selected above, also print the pcap to stdout.")
    parser.add_argument("--num-packets", action="store", default=1, type=int, help="Number of packets to send.")
    parser.add_argument("directory", action="store", help="The directory where sample packets are located.")

    args = parser.parse_args()

    if (not os.path.exists(args.directory)):
        sys.stderr.write("Error. Provided directory does not exist")
        return 1
    directory = os.path.join(args.directory, '')
    packet_files_list = glob.glob(directory + "*.txt")

    for i in range(args.num_packets):
        packet_file_index = random.randint(0, len(packet_files_list) - 1)
        filename = packet_files_list[packet_file_index]
        # with open(filename, 'rb') as file:
        if (i != 0):
        # if (i % 5 != 0):
            read_packets.main(["--pcap", "/home/savi/alex/FFShark_Wireshark_Integration/test.pcap", "--pcap-print", "--skip-header", filename])
        else:
            read_packets.main(["--pcap", "/home/savi/alex/FFShark_Wireshark_Integration/test.pcap", "--pcap-print", filename])
        time.sleep(0.1)

    return 0


if __name__ == "__main__":
    main()

