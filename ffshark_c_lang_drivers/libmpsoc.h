#ifndef LIBMPSOC_H
#define LIBMPSOC_H

#include <stdint.h> //uintN_t
#include <stdbool.h>

// ****************************************
// Lock file and command to create lock file
// ****************************************
#define LOCK_FILE "/var/lock/pokelockfile"
#define MAKE_LOCK_FILE_CMD "touch /var/lock/pokelockfile"

// ****************************************
// Compiling and sending filters commands
// ****************************************
#define COMPILE_FILT_CMD "/home/savi/filterexecutables/compilefilt "
#define SEND_FILT_CMD "sudo /home/savi/filterexecutables/sendfilter "
#define SUPPRESS_OUTPUT " > /dev/null "


// ****************************************
// APIs that use lock file to maintain thread safety
// for multiple processes running on FPGA.
// ****************************************
void lock_init();
int lock();
void unlock(int fd);

// ****************************************
// APIs for compiling and sending filtering 
// instructions to FFShark. 
void compile_filter(char * filt_instr);
void send_filter(bool accept_all, unsigned filt_instr_addr);

// ****************************************
// AXI APIs. Works specifically with 64 bit datawidth
// ****************************************
typedef struct {
    unsigned size;
    int fd;
    void *map_base;
    long page_size;
} AXI;

void init_axi(AXI *axi_handler, unsigned addr, unsigned size);

uint64_t read_axi(AXI *axi_handler, unsigned offset);

void write_axi(AXI *axi_handler, unsigned offset, uint64_t data);

// ****************************************
// Axilite APIs. Works specifically with 32 bit datawidth
// ****************************************
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