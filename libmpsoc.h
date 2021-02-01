#ifndef LIBMPSOC_H
#define LIBMPSOC_H 

#include <fcntl.h> //open
#include <unistd.h> //close
#include <stdio.h> //printf
#include <stdlib.h> //malloc
#include <stdint.h> //uintN_t
#include <string.h> //perror, sprintf
#include <errno.h> 
#include <sys/mman.h> //mmap


typedef struct {
    int size;
    int fd;
    void *map_base;
    long page_size;
} AXILITE; 

void init_axilite(AXILITE *axilite_handler, int addr, int size);



#endif