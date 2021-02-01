DBG=-DDEBUG_ON

read_fifo: *.h *.c
	gcc -g ${DBG} -Wall -fno-diagnostics-show-caret -o read_fifo *.c -lpthread -lm

clean:
	rm -rf read_fifo
