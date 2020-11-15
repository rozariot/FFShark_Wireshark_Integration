import subprocess
import os
import argparse
import string
import random
import sys


FIFO_VACANCY_ADDR = 0xA001100C
READ_CMD = "./spoke.sh"

def read_reg(addr):
	addr_hex = hex(addr)
	proc = subprocess.Popen([READ_CMD, addr_hex], stdout=subprocess.PIPE)
	vacancy_string_output = proc.communicate()[0]
	vacancy_output_str_list = vacancy_string_output.split()

	assert(len(vacancy_output_str_list) == 4), "read error when using spoke"
	read_val = int(vacancy_output_str_list[2], 0)
	return read_val

def main():
	parser = argparse.ArgumentParser(description="Sends packets randomly one by one to ffshark when given packet files directory")
	parser.add_argument("--packets-directory", action="store", help="Provide directory of packet text files", required="true")
	parser.add_argument("--send-frequency", action="store", type=int, default=10, help="Specify how frequently to send packets.")
	parser.add_argument("--num-packets", action="store", type=int, default=10, help="Specify how many random packets to send.")
	args = parser.parse_args()

	directory = args.packets_directory
	send_frequency = args.send_frequency
	num_packets = args.num_packets
	

	vacancy_val = read_reg(FIFO_VACANCY_ADDR)
	print vacancy_val

if __name__ == "__main__":
	main()
