import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time

# The following script randomly selects packets from a directory containing packet text files to ffshark. It will check if the fifo has
# enough space for txt file packet. 

# Register constants 
FFSHARK_ENABLE_ADDR = 0xA0010004
FIFO_VACANCY_ADDR = 0xA001100C
SRR_ADDR = 0xA0011028
SRR_RST= 0xA5
FIFO_DATA_WIDTH = 4 #in bytes

# Commands
READ_CMD = "./spoke.sh"
WRITE_CMD = "./spoke.sh "
HIDE_OUTPUT = " > /dev/null"

WRITE_FILE_CMD = "./send_file_safe.sh "

def read_reg(addr):
    addr_hex = hex(addr)
    proc = subprocess.Popen([READ_CMD, addr_hex], stdout=subprocess.PIPE)
    vacancy_string_output = proc.communicate()[0]
    vacancy_output_str_list = vacancy_string_output.split()

    assert(len(vacancy_output_str_list) == 4), "read error when using spoke"
    read_val = int(vacancy_output_str_list[2], 0)
    return read_val

def write_reg(addr, data):
    addr_hex = hex(addr)
    data_hex = hex(data)
    os.system(WRITE_CMD + addr_hex + " " + data_hex + HIDE_OUTPUT) 

def get_file_size_in_words(file):
    size_bytes = os.path.getsize(file)
    return (size_bytes/4)

def main():
    parser = argparse.ArgumentParser(description="Sends packets randomly one by one to ffshark when given packet text files directory")
    parser.add_argument("--packets-directory", action="store", help="Provide directory of packet text files", required="true")
    parser.add_argument("--send-wait-time", action="store", type=float, default=0, help="Specify wait time in seconds between sending packets.")
    parser.add_argument("--num-packets", action="store", type=int, default=float('inf'), help="Specify how many random packets to send.")
    args = parser.parse_args()

    directory = args.packets_directory
    wait_time = args.send_wait_time
    num_packets = args.num_packets

    directory = args.packets_directory
    assert(os.path.exists(directory)), "directory doesn't exist"
    directory = os.path.join(directory, '')
    packet_files_list = glob.glob(directory + "*.txt")
    
    #initialize FFShark and FIFO
    write_reg(FFSHARK_ENABLE_ADDR, 1)
    write_reg(SRR_ADDR, SRR_RST)

    # sending packets
    iteration_count = 0
    while (iteration_count < num_packets):
        packet_file_index = random.randint(0, len(packet_files_list) - 1)
        file = packet_files_list[packet_file_index]
        num_words = get_file_size_in_words(file)
        num_vacant_words = read_reg(FIFO_VACANCY_ADDR)
        print("num vacant words ::: " + str(num_vacant_words))
        while (num_words > num_vacant_words):
            num_vacant_words = read_reg(FIFO_VACANCY_ADDR)
            print("num vacant words ::: " + str(num_vacant_words))    
        os.system(WRITE_FILE_CMD + file)
        if (wait_time > 0):
            time.sleep(wait_time)
        iteration_count += 1 


if __name__ == "__main__":
    main()
