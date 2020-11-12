#!/usr/bin/python

import sys
from scapy.all import *
import argparse

message = "And let's dispel once and for all with this fiction that Barack Obama doesn't know what he's doing. He knows exactly what he's doing."

def random_ip_addr(seed=None):
    random.seed(seed)
    n1 = random.randint(0,255)
    n2 = random.randint(0,255)
    n3 = random.randint(0,255)
    n4 = random.randint(0,255)
    str_ip = str(n1) + "." + str(n2) + "." + str(n3) + "." + str(n4)
    return str_ip

def random_eth_addr(seed=None):
    random.seed(seed)
    n1 = random.randint(0,255)
    n2 = random.randint(0,255)
    n3 = random.randint(0,255)
    n4 = random.randint(0,255)
    n5 = random.randint(0,255)
    n6 = random.randint(0,255)
    str_eth = hex(n1) + ":" + hex(n2) + ":" + hex(n3) + ":" + hex(n4) + ":" + hex(n5) + ":" + hex(n6)
    return str_eth

def main():
    parser = argparse.ArgumentParser(description="Generates one random packet. No arguments will output raw packet")
    parser.add_argument("--show", action="store_true", help="Print packet in human readable form")
    parser.add_argument("--hexdump", action="store_true", help="Prints a hexdump of the packet")
    parser.add_argument("--summary", action="store_true", help="Prints a summary of the packet")
    parser.add_argument("--ip-src", action="store", help="Set the IP source address manually")
    parser.add_argument("--ip-dst", action="store", help="Set the IP destination address manually")
    parser.add_argument("--eth-src", action="store", help="Set the Ethernet source address manually")
    parser.add_argument("--eth-dst", action="store", help="Set the Ethernet destination address manually")
    args = parser.parse_args()

    #Set IP Addresses
    if (args.ip_src):
        src_ip = args.ip_src
    else:
        src_ip = random_ip_addr()
    if (args.ip_dst):
        dst_ip = args.ip_dst
    else:
        dst_ip = random_ip_addr()

    #Set Ethernet addresses
    if (args.eth_src):
        src_eth = args.eth_src
    else:
        src_eth = random_eth_addr()
    if (args.eth_dst):
        dst_eth = args.eth_dst
    else:
        dst_eth = random_eth_addr()


    packet = Ether(src=src_eth, dst=dst_eth)/ IP(src=src_ip, dst=dst_ip)/ UDP(sport=80, dport=5355)/message
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



if __name__ == "__main__":
    main()

