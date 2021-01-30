import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time
import math
import fcntl

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

# Lock file used to maintain thread safety for multiple
# processes running on the FPGA
LOCK_FILE = "/var/lock/pokelockfile"

def init_lock_file():
	if not os.path.exists(LOCK_FILE):
		os.system("touch " + LOCK_FILE)

def main():
    parser = argparse.ArgumentParser(description="Sends packets randomly one by one to ffshark when given packet text files directory")
    parser.add_argument("--packets-directory", action="store", help="Provide directory of packet text files", required="true")
    parser.add_argument("--send-wait-time", action="store", type=float, default=0, help="Specify wait time in seconds between sending packets.")
    parser.add_argument("--num-packets", action="store", type=float, default=float("inf"), help="Specify how many random packets to send.")
    parser.add_argument("--debug", action="store_true", help="Enable for more verbosity")
    parser.add_argument("--perf-test", action="store_true", help="measure performance")
    args = parser.parse_args()

    directory = args.packets_directory
    wait_time = args.send_wait_time
    num_packets = args.num_packets
    perf_test = args.perf_test

    directory = args.packets_directory
    assert(os.path.exists(directory)), "directory doesn't exist"
    directory = os.path.join(directory, '')
    packet_files_list = glob.glob(directory + "*.txt")

    # initialize the lock
    init_lock_file()
    lock = open(LOCK_FILE, "r")

    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

    # init the axi lite mem map for FFShark and FIFO
    axil_FFShark = mp.axilite(addr=FFSHARK_BASE,size=FFSHARK_SIZE)
    axil_FIFO = mp.axilite(addr=FIFO_BASE,size=FIFO_SIZE)

    # initialize FFShark and FIFO
    print(axil_FFShark.write32(value=0x1,offset=FFSHARK_ENABLE_OFFSET))
    print(axil_FIFO.write32(value=FIFO_SRR_RST_VAL,offset=FIFO_SRR_OFFSET))

    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    if (perf_test):
        start_time = time.time()
        total_bytes = 0
        total_write_time = 0
        file_read_time = 0
        write_word_no_lock_time = 0

    # sending packets
    iteration_count = 0
    while (iteration_count < num_packets):
        # pick a random file
        packet_file_index = random.randint(0, len(packet_files_list) - 1)
        file = packet_files_list[packet_file_index]
        # get file size and round up to nearest word
        size_bytes = os.path.getsize(file)
        
        if (perf_test):
            total_bytes += size_bytes            
        
        # divide by 8 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        num_words = int(math.ceil(size_bytes/8))
        if (args.debug):
            print(num_words)
            print(size_bytes)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        num_vacant_words = axil_FIFO.read32(offset=FIFO_TDFV_OFFSET)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        if (args.debug):
            print("num vacant words ::: " + str(num_vacant_words))
        
        # check if the FIFO has enough space for the packet and if not wait
        while (num_words > num_vacant_words):
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            num_vacant_words = axil_FIFO.read32(offset=FIFO_TDFV_OFFSET)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            print("num vacant words ::: " + str(num_vacant_words))
        
        # write the packet a word at a time
        if (perf_test):
            write_time = time.time()
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        with open(file) as f:
            for i in range(num_words):
                if (perf_test):
                    file_time = time.time()
                file_val = int(f.read(8),16)
                if (perf_test):
                    file_read_time += time.time() - file_time               
                
                if (perf_test):
                    write_no_lock_time = time.time()
                axil_out = axil_FIFO.write32(value=file_val,offset=FIFO_TDFD_OFFSET)
                if (perf_test):
                    write_word_no_lock_time += time.time() - write_no_lock_time                
                
                if (args.debug):
                    print(hex(file_val))
                    print(axil_out)
        
        # Write the number of bytes to TLR
        # divide by 2 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        axil_out = axil_FIFO.write32(value=int(math.ceil(size_bytes/2)),offset=FIFO_TLR_OFFSET)
        if (args.debug):
            print(int(math.ceil(size_bytes/2)))
            print(axil_out)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        if (perf_test):
            total_write_time += time.time() - write_time
            
        
        if (wait_time > 0):
            time.sleep(wait_time)
        iteration_count += 1
        
    if (perf_test):
        total_time = time.time() - start_time
        bit_rate = (total_bytes * 8) / total_time
        write_bit_rate = (total_bytes * 8) / total_write_time
        print("Total time : " + str(total_time))
        print("Write time : " + str(total_write_time))
        print("Write with no Locking time: " + str(write_word_no_lock_time))
        print("File read time: " + str(file_read_time))
        print("Total Data rate : " + str(bit_rate) + " bits/second")


if __name__ == "__main__":
    main()
