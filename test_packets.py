#!/usr/bin/python

import sys
from scapy.all import *
from scapy.layers.http import *
import argparse
import string
import random

message = "And let's dispel once and for all with this fiction that Barack Obama doesn't know what he's doing. He knows exactly what he's doing."

def random_ip_addr():
    n1 = random.randint(0,255)
    n2 = random.randint(0,255)
    n3 = random.randint(0,255)
    n4 = random.randint(0,255)
    str_ip = str(n1) + "." + str(n2) + "." + str(n3) + "." + str(n4)
    return str_ip

def random_ipv6_addr():
    n1 = random.randint(0,65535)
    n2 = random.randint(0,65535)
    n3 = random.randint(0,65535)
    n4 = random.randint(0,65535)
    n5 = random.randint(0,65535)
    n6 = random.randint(0,65535)
    n7 = random.randint(0,65535)
    n8 = random.randint(0,65535)
    str_ip = hex(n1)[2:] + ":" + hex(n2)[2:] + ":" + hex(n3)[2:] + ":" + hex(n4)[2:] + ":" + hex(n5)[2:] + ":" + hex(n6)[2:] + ":" + hex(n7)[2:] + ":" + hex(n8)[2:]
    return str_ip

def random_eth_addr():
    n1 = random.randint(0,255)
    n2 = random.randint(0,255)
    n3 = random.randint(0,255)
    n4 = random.randint(0,255)
    n5 = random.randint(0,255)
    n6 = random.randint(0,255)
    str_eth = hex(n1) + ":" + hex(n2) + ":" + hex(n3) + ":" + hex(n4) + ":" + hex(n5) + ":" + hex(n6)
    return str_eth

def set_ip_addr(args):
    if (args.layer_network == "IPv4" or args.layer_network == "ICMP"):
        if (args.ip_src):
            src_ip = args.ip_src
        else:
            src_ip = random_ip_addr()
        if (args.ip_dst):
            dst_ip = args.ip_dst
        else:
            dst_ip = random_ip_addr()
    elif (args.layer_network == "IPv6"):
        if (args.ip_src):
            src_ip = args.ip_src
        else:
            src_ip = random_ipv6_addr()
        if (args.ip_dst):
            dst_ip = args.ip_dst
        else:
            dst_ip = random_ipv6_addr()
    else:
        sys.stderr.write("Error. Unrecognized network layer")
        return None
    return src_ip, dst_ip

def get_random_payload(min_size=10, max_size=100):
    N = random.randint(min_size, max_size)
    rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits + " " * 4) for _ in range(N))
    return rand_str


def main():
    parser = argparse.ArgumentParser(description="Generates one random packet. No arguments will output packet as hex to terminal.")
    parser.add_argument("--show", action="store_true", help="Print packet in human readable form")
    parser.add_argument("--hexdump", action="store_true", help="Prints a hexdump of the packet")
    parser.add_argument("--summary", action="store_true", help="Prints a summary of the packet")
    parser.add_argument("--binary", action="store_true", help="Outputs the packet as binary")
    parser.add_argument("--seed", action="store", type=int, help="Provide a seed so can reproduce random packet. If not provided, will use current time.")
    parser.add_argument("--layer-network", action="store", choices=["IPv4", "IPv6", "ICMP"], default="IPv4", help="Specify which network layer to use. Selecting ICMP will also use IPv4.")
    parser.add_argument("--layer-transport", action="store", choices=["UDP", "TCP"], default="TCP", help="Specify which transport layer to use.")
    parser.add_argument("--layer-application", action="store", choices=["DNS", "HTTP", "raw"], default="HTTP", help="Specify which application layer to use.")
    parser.add_argument("--payload", action="store", help="For DNS, will be name of address to query. For HTTP, is the message. For raw is the string to be sent."
                        "If no arg is given, will generate a random string using uppercase letters and digits with size between --rand-payload-min and --rand-payload-max.")
    parser.add_argument("--rand-payload-min", action="store", type=int, default=10, help="Minimum size for randomly generated payload")
    parser.add_argument("--rand-payload-max", action="store", type=int, default=100, help="Maximum size for randomly generated payload")
    parser.add_argument("--ip-src", action="store", help="Set the IP source address manually")
    parser.add_argument("--ip-dst", action="store", help="Set the IP destination address manually")
    parser.add_argument("--eth-src", action="store", help="Set the Ethernet source address manually")
    parser.add_argument("--eth-dst", action="store", help="Set the Ethernet destination address manually")
    args = parser.parse_args()


    random.seed(args.seed)
    #Set IP Addresses
    src_ip, dst_ip = set_ip_addr(args)

    #Set Ethernet addresses
    if (args.eth_src):
        src_eth = args.eth_src
    else:
        src_eth = random_eth_addr()
    if (args.eth_dst):
        dst_eth = args.eth_dst
    else:
        dst_eth = random_eth_addr()

    if (args.layer_network == "IPv4"):
        network_layer = IP(src=src_ip, dst=dst_ip)
    elif (args.layer_network == "IPv6"):
        network_layer = IPv6(src=src_ip, dst=dst_ip)
    elif (args.layer_network == "ICMP"):
        network_layer = IP(src=src_ip, dst=dst_ip) / ICMP()
    else:
        sys.stderr.write("Error. Unrecognized network layer")
        return 1

    if (args.layer_transport == "UDP"):
        transport_layer = UDP()
    elif (args.layer_transport == "TCP"):
        transport_layer = TCP()
    else:
        sys.stderr.write("Error. Unrecognized transport layer")
        return 1

    if (args.payload):
        payload = args.payload
    else:
        payload = get_random_payload(min_size=args.rand_payload_min, max_size=args.rand_payload_max)

    if (args.layer_application == "DNS"):
        application_layer = DNS(rd=1, qd=DNSQR(qname=payload))
    elif (args.layer_application == "HTTP"):
        application_layer = HTTP()/HTTPResponse() / payload
    elif (args.layer_application == "raw"):
        application_layer = payload
    else:
        sys.stderr.write("Error. Unrecognized application layer")
        return 1

    packet = Ether(src=src_eth, dst=dst_eth)/network_layer
    if (args.layer_network != "ICMP"):
        packet = packet / transport_layer / application_layer

    if (args.hexdump):
        hexdump(packet)
    if (args.show):
        packet.show2()
    if (args.summary):
        print(packet.summary())
    if (args.binary):
        print(packet)
    if (not args.hexdump and not args.show and not args.summary):
        print(bytes_hex(packet))

    return 0


if __name__ == "__main__":
    main()

