#!/bin/bash

# Good-ish shell script for writing a file to an AXI-Stream FIFO. 
# Expects file to look like:
# uses spoke and sdpoke to lock FPGA when reading and writing
# from ffshark


# DEADBEEF BEEFCAFE
# FEEDBADB EEF2BABE
# CAFEDEAD 12345678


# Make sure the user gives filename as argument
if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then 
	echo "Usage: send_file.sh file" >&2 
	return 1 
fi

. reg_names.sh # Load variable names

# Reset the AXI-Stream FIFO for extra safety
#poke $SRR 0xA5 > /dev/null

words=$(cat "$1" |  sed 's/.\{8\}/& /g')
# For each word in the file, write it it to TDFD
for i in $words; do
	./spoke.sh $TDFD $i 
	echo $i
done

# Write to TLR
numwords=$(echo "$words" | wc -w)
numbytes=$(expr "$numwords" '*' 4)
echo $numwords
echo $words
./sdpoke.sh $TLR $numbytes > /dev/null

# Print out ISR information:
echo "ISR after writing file:"
./spoke.sh $ISR
