#!/usr/bin/python

import sys
from scapy.all import *
import argparse

message = "And let's dispel once and for all with this fiction that Barack Obama doesn't know what he's doing. He knows exactly what he's doing."

def main():
    parser = argparse.ArgumentParser(description="Generates one random packet. No arguments will output raw packet")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--hexdump", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    packet = Ether(src="ab:ab:ab:ab:ab:ab", dst="12:12:12:12:12:12")/ IP(src="127.0.0.1", dst="192.168.1.1")/ UDP(sport=80, dport=5355)/message
    # packet = packet.build()
    # print(len(packet))
    if (args.hexdump):
        hexdump(packet)
    if (args.show):
        packet.show2()
    if (args.summary):
        print(packet.summary())
    if (not args.hexdump and not args.show and not args.summary):
        print(packet)

    file_write = open("packet.bin", "wb")
    file_write.write(bytes(packet))


if __name__ == "__main__":
    main()

