DBG=-DDEBUG_ON

ffshark_send_packets: *.h *.c
	gcc -g ${DBG} -Wall -fno-diagnostics-show-caret -o ffshark_send_packets *.c -lpthread -lm

clean:
	rm -rf ffshark_send_packets
