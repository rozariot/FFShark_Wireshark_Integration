#!/bin/bash

# Good-ish shell script for reading the AXI-Stream FIFO and printing to terminal 
# output onto terminal is like this:

# DEADBEEF
# FEEDBADB
# CAFEDEAD

# Make sure the user gives filename as argument
if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then 
	echo "Usage: receive_file.sh file" >&2 
	return 1 
fi

. reg_names.sh # Load variable names
 
#read the FIFO occupancy
words=$(poke $RDFO | grep -Eo "0x[[:xdigit:]]+") 
echo $words

START=1
END=$(($words))
echo $END

#Check if RDFO is 0 if so don't read any of the following registers as it will cause a hang
if [ $END -eq 0 ]; then
	echo "RDFO is 0, no data read"
else
	echo "FIFO has values to be read "
	#Read in the number of bytes that form the packet
	numbytes=$(poke $RLR | grep -Eo "0x[[:xdigit:]]+")
	#We readin 4 bytes at a time
	END=$(expr $(($numbytes)) '/' 4 )
	echo $numbytes
	echo $END
	#clear input file
	> $1
	#loop and read RDFD to receive packet data
	for i in $(eval echo "{$START..$END}"); do
		data=$(poke $RDFD | grep -Eo "0x[[:xdigit:]]+")
		echo $data | tee -a $1 
	done
fi

