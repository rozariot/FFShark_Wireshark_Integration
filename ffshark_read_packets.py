#!/usr/bin/python3

import subprocess
import sys
import os.path
import string
import random
import binascii
import io
from scapy.all import *
from scapy.layers.http import *

def main():

    #f = open("receiveFIFOFile.txt", "w")
   
    file_str = ""
 
    process = subprocess.Popen(["/home/savi/kanver/ffshark_tut/receive_file_safe.sh"], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        file_str += line.rstrip("\n")

    #print(file_str)

    if file_str != "RDFO is 0, no data read":
        #f.write(file_str)
        #fpcap = open("test.pcap", "w")	
        packet = Ether(binascii.a2b_hex(file_str))
        wrpcap('test.pcap', packet)
        with open('test.pcap', 'rb') as file:
            sys.stdout.buffer.write(file.read())

    #f.close()
    
    return 0


if __name__ == "__main__":
    main()
