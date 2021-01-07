import subprocess
import os
import argparse
import string
import random
import sys
import glob
import time

COMPILE_FILT_CMD = os.getcwd() + '/compilefilt'

def main():
	parser = argparse.ArgumentParser(description="Compile packet filtering instruction")
	parser.add_argument("--capture-filter", help="The capture filter")
	args = parser.parse_args()
	filter = args.capture_filter
	
	if (filter):	
		os.system(COMPILE_FILT_CMD + " " + filter)
	

if __name__ == "__main__":
	main()
