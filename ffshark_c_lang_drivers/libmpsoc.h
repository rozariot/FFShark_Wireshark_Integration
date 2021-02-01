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
    unsigned size;
    int fd;
    void *map_base;
    long page_size;
} AXILITE; 

void init_axilite(AXILITE *axilite_handler, unsigned addr, unsigned size);

unsigned read_axilite(AXILITE *axilite_handler, unsigned offset);

void write_axilite(AXILITE *axilite_handler, unsigned offset, unsigned data);

#endif