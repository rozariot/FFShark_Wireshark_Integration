import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time
import fcntl

"""
Takes filtering instruction as parameter. Compiles the instruction using
compilefilt.c's executable. Sends the filtered program using sendfilter.c's 
executable

compilefilt.c can be found here: https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/compilefilt
sendfilt.c can be found here: https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/mpsoc_sendfilter 
"""
# Lock file used to maintain thread safety for multiple 
# processes running on the FPGA
LOCK_FILE = "/var/lock/pokelockfile"

def compile_and_send_filter(instruction):
    bpf_prog = "prog.bpf"
    FILT_INSTR_ADDR = 0xA0010000
    SUPPRESS_OUTPUT = "> /dev/null"
    curr_dir = os.getcwd()

    # init lock file
    if not os.path.exists(LOCK_FILE):
        os.system("touch " + LOCK_FILE)
    lock = open(LOCK_FILE, "r")

    COMPILE_FILT_CMD = curr_dir + '/compilefilt' + " " + SUPPRESS_OUTPUT
    
    if (instruction == "all"):
        prog = "/home/savi/filterexecutables/acceptall.bpf"
    else: 
        prog = bpf_prog
        os.system(COMPILE_FILT_CMD + " " + instruction)
    
    SEND_FILT_CMD = "sudo ./sendfilter " + prog + " " + str(FILT_INSTR_ADDR) + " " + SUPPRESS_OUTPUT	

    

    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    os.system(SEND_FILT_CMD)
    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


