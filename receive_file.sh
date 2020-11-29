#!/bin/bash

# Good-ish shell script for reading the AXI-Stream FIFO and printing to terminal 
# output onto terminal is like this:

# deadbeeffeedbadbcafedead

. reg_names.sh # Load variable names
 
#read the FIFO occupancy
words=$(poke $RDFO | grep -Eo "0x[[:xdigit:]]+") 

START=1
END=$(($words))

#Check if RDFO is 0 if so don't read any of the following registers as it will cause a hang
if [ $END -eq 0 ]; then
	echo "RDFO is 0, no data read"
else
	#Read in the number of bytes that form the packet
	numbytes=$(poke $RLR | grep -Eo "0x[[:xdigit:]]+")
	#We read in 4 bytes at a time
	END=$(expr $(($numbytes)) '/' 4 )
	#loop and read RDFD to receive packet data
	for i in $(eval echo "{$START..$END}"); do
		reg_read=$(poke $RDFD | grep -Eo "0x[[:xdigit:]]+")
		printf "%08x\n" $reg_read
	done
fi

