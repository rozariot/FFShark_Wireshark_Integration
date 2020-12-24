import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time

"""
Takes filtering instruction as parameter. Compiles the instruction using
compilefilt.c's executable. Sends the filtered program using sendfilter.c's 
executable

compilefilt.c can be found here: https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/compilefilt
sendfilt.c can be found here: https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/mpsoc_sendfilter 
"""
def compile_and_send_filter(instruction):
	bpf_prog = "prog.bpf"
	FILT_INSTR_ADDR = 0xA0010000
	curr_dir = os.getcwd()

	COMPILE_FILT_CMD = curr_dir + '/compilefilt'
	SEND_FILT_CMD = "sudo ./sendfilter " + bpf_prog + " " + str(FILT_INSTR_ADDR)	

	os.system(COMPILE_FILT_CMD + " " + instruction)
	os.system(SEND_FILT_CMD)
	
	

