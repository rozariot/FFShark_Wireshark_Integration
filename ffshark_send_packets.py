import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time
# import libmpsoc provided by Clark
# make sure it's installed as python module by running sudo pip3 install libmpsoc
# should already be installed but incase it isn't refer to above comment
import libmpsoc as mp

# The following script randomly selects packets from a directory containing packet text files to ffshark. It will check if the fifo has
# enough space for txt file packet. 

# Register constants
# The base addr can vary depending on FFShark and PS config, we really shouldn't hard code 
FFSHARK_BASE = 0xA0010000
FFSHARK_SIZE = 0x1000 # 4KB mem map region
FFSHARK_ENABLE_OFFSET = 0x4
FIFO_BASE = 0xA0011000
FIFO_SIZE = 0x1000 # 4KB mem map region
FIFO_TDFV_OFFSET = 0xC
FIFO_TDFD_OFFSET = 0x10
FIFO_TLR_OFFSET = 0x14
FIFO_SRR_OFFSET = 0x28
FIFO_SRR_RST_VAL = 0xA5
FIFO_DATA_WIDTH = 4 #in bytes

# Commands
# no longer used as poke is retired use libmpsoc instead
# READ_CMD = "./spoke.sh"
# WRITE_CMD = "./spoke.sh "
# HIDE_OUTPUT = " > /dev/null"
# WRITE_FILE_CMD = "./send_file_safe.sh "

def get_file_size_in_words(file):
    size_bytes = os.path.getsize(file)
    # divide by 8 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data 
    return int(size_bytes/8) # convert to int so round down to to multiple of 8, fix later

def main():
    parser = argparse.ArgumentParser(description="Sends packets randomly one by one to ffshark when given packet text files directory")
    parser.add_argument("--packets-directory", action="store", help="Provide directory of packet text files", required="true")
    parser.add_argument("--send-wait-time", action="store", type=float, default=0, help="Specify wait time in seconds between sending packets.")
    parser.add_argument("--num-packets", action="store", type=int, default=0, help="Specify how many random packets to send.")
    args = parser.parse_args()

    directory = args.packets_directory
    wait_time = args.send_wait_time
    num_packets = args.num_packets

    directory = args.packets_directory
    assert(os.path.exists(directory)), "directory doesn't exist"
    directory = os.path.join(directory, '')
    packet_files_list = glob.glob(directory + "*.txt")

    # init the axi lite mem map for FFShark and FIFO
    axil_FFShark = mp.axilite(addr=FFSHARK_BASE,size=FFSHARK_SIZE)
    axil_FIFO = mp.axilite(addr=FIFO_BASE,size=FIFO_SIZE)

    # initialize FFShark and FIFO
    print(axil_FFShark.write32(value=0x1,offset=FFSHARK_ENABLE_OFFSET))
    print(axil_FIFO.write32(value=FIFO_SRR_RST_VAL,offset=FIFO_SRR_OFFSET))

    # sending packets
    iteration_count = 0
    while (iteration_count < num_packets):
        # pick a random file
        packet_file_index = random.randint(0, len(packet_files_list) - 1)
        file = packet_files_list[packet_file_index]
        num_words = get_file_size_in_words(file)
        print(num_words)
        num_vacant_words = axil_FIFO.read32(offset=FIFO_TDFV_OFFSET)
        print("num vacant words ::: " + str(num_vacant_words))
        # check if the FIFO has enough space for the packet and if not wait
        while (num_words > num_vacant_words):
            num_vacant_words = axil_FIFO.read32(offset=FIFO_TDFV_OFFSET)
            print("num vacant words ::: " + str(num_vacant_words)) 
        # write the packet a word at a time
        with open(file) as f:
            for i in range(num_words):
                file_val = int(f.read(8),16)
                print(hex(file_val))
                print(axil_FIFO.write32(value=file_val,offset=FIFO_TDFD_OFFSET))
        # Write the number of bytes to TLR
        print(axil_FIFO.write32(value=(num_words * 4),offset=FIFO_TLR_OFFSET))
        if (wait_time > 0):
            time.sleep(wait_time)
        iteration_count += 1 


if __name__ == "__main__":
    main()
