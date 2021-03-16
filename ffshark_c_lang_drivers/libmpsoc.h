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
#include <sys/file.h> //flock

//Lock file and commond to create lock file
#define LOCK_FILE "/var/lock/pokelockfile"
#define MAKE_LOCK_FILE_CMD "touch /var/lock/pokelockfile"

//APIs that use lock file to maintain thread safety 
//for multiple processes running on FPGA.
void lock_init();
int lock();
void unlock(int fd);

// AXI APIs. Works specifically with 64 bit datawidth
typedef struct {
    unsigned size;
    int fd;
    void *map_base;
    long page_size;
} AXI; 

void init_axi(AXI *axi_handler, unsigned addr, unsigned size);

uint64_t read_axi(AXI *axi_handler, unsigned offset);

void write_axi(AXI *axi_handler, unsigned offset, uint64_t data);

// Axilite APIs. Works specifically with 32 bit datawidth
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