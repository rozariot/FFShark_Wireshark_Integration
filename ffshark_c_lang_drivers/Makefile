DBG = -DDEBUG_ON
CC =  gcc
CFLAGS = -g -Wall
# CFLAGS = -O2 -Wall

all: ffshark_send_packets ffshark_read_packets

ffshark_send_packets: libmpsoc.o ffshark_send_packets.c
	$(CC) $(CFLAGS) $(DBG) -fno-diagnostics-show-caret libmpsoc.c ffshark_send_packets.c -lpthread -lm -o ffshark_send_packets

ffshark_read_packets: libmpsoc.o ffshark_read_packets.c ffshark_read_packets.h
	$(CC) $(CFLAGS) libmpsoc.c ffshark_read_packets.c -o ffshark_read_packets -lm

libmpsoc.o: libmpsoc.c libmpsoc.h
	$(CC) $(CFLAGS) -c libmpsoc.c


clean:
	rm -f ffshark_send_packets
	rm -f ffshark_read_packets
	rm -f libmpsoc.o
