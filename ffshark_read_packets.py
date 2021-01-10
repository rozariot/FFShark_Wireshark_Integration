#!/usr/bin/python3
import subprocess
import sys
import os.path
import string
import random
import binascii
import io
import math
from scapy.all import *
from scapy.layers.http import *
import fcntl

# import libmpsoc provided by Clark
# make sure it's installed as python module by running sudo pip3 install libmpsoc
# should already be installed but incase it isn't refer to above comment
import libmpsoc as mp

# Register constants
# The base addr can vary depending on FFShark and PS config, we really shouldn't hard code 
FIFO_BASE = 0xA0011000
FIFO_SIZE = 0x1000 # 4KB mem map region
FIFO_RDFO_OFFSET = 0x1C
FIFO_RDFD_OFFSET = 0x20
FIFO_RLR_OFFSET = 0x24
FIFO_DATA_WIDTH = 4 #in bytes

# Lock file used to maintain thread safety for multiple 
# processes running on the FPGA
LOCK_FILE = "/var/lock/pokelockfile"

def init_lock_file():
    if not os.path.exists(LOCK_FILE):
        os.system("touch " + LOCK_FILE)

def main():
    # initialize the lock
    init_lock_file()
    lock = open(LOCK_FILE, "r")

    # init the axi lite mem map for FIFO
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    axil_FIFO = mp.axilite(addr=FIFO_BASE,size=FIFO_SIZE)
    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    
    file_str = ""
    
    # check if Receive FIFO has packets to read, if not don't read
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    num_words_in_FIFO = axil_FIFO.read32(offset=FIFO_RDFO_OFFSET)
    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    #print("num words in fifo " + str(num_words_in_FIFO))
    if (num_words_in_FIFO != 0):
        # read the number of bytes in a packet, this can be less than the num_words_in_FIFO
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        num_bytes_in_packet = axil_FIFO.read32(offset=FIFO_RLR_OFFSET)
        #print(num_bytes_in_packet)
        # this rounds up so we read the next partial words
        # currently this doesn't work as FFShark sends a copy of the 2nd last word
        num_words_in_packet = int(math.ceil(num_bytes_in_packet/4))
        # read the data and convert to hex string
        for i in range(num_words_in_packet):
            data_word = axil_FIFO.read32(offset=FIFO_RDFD_OFFSET)
            #print(hex(data_word))
            file_str = file_str + "{:08x}".format(data_word)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)    
        #print(file_str)
        packet = Ether(binascii.a2b_hex(file_str))
        wrpcap('test.pcap', packet)
        with open('test.pcap', 'rb') as file:
            sys.stdout.buffer.write(file.read())


if __name__ == "__main__":
    main()
