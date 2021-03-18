#include "libmpsoc.h"
#include <fcntl.h> //open
#include <unistd.h> //close
#include <stdio.h> //printf
#include <stdlib.h> //malloc
#include <string.h> //perror, sprintf
#include <errno.h>
#include <sys/mman.h> //mmap
#include <sys/file.h> //flock
#include <linux/limits.h>


//Locking Mechanism APIs
//references:
//https://man7.org/tlpi/code/online/dist/filelock/t_flock.c.html
//https://manpages.debian.org/buster/manpages-dev/flock.2.en.html
void lock_init(){
    /*
    Locking file function. Returns file descriptor.

    example:
    lock_init()
    int fd = lock() //locks

    ... some code operations ...

    unlock(fd); //unlock with the unlock function

    */
    FILE *file = fopen((char *)LOCK_FILE, "r");

    if (!file){
        fopen(LOCK_FILE, "w");
    }
    else {
        fclose(file);
    }
}

int lock(){
    //example usage in description under lock_init()
    int fd;
    fd = open(LOCK_FILE, O_RDONLY);
    if (fd == -1) perror("Lock file not found");
    flock(fd, LOCK_EX);
    return fd;
}

void unlock(int fd){
    //example usage in description under lock_init()
    flock(fd, LOCK_UN);
    close(fd);
}

// APIs for compiling and sending filtering 
// instructions to FFShark. 
void compile_filter(char * filt_instr){
    /*
    Compiles the filter from the filtering instruction.
    It creates a file called prog.bpf.
    
    Uses the compilefilt executable found in link:
    https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/compilefilt
    
    example:
    char filter[] = tcp;
    compile_filter(tcp); //compile filter for tcp
    send_filter(false, 0xA0010000); //send tcp filter by sending prog.bpf
    */ 

    char instr[1024];
    strcpy(instr, COMPILE_FILT_CMD);    
    strcat(instr, SUPPRESS_OUTPUT);
    strcat(instr, filt_instr);
    system(instr);
}

void send_filter(bool accept_all, unsigned filt_instr_addr){
    /*
    accept_all : 
    If it is true, acceptall.bpf file gets programmed as the filter.
    Otherwise, prog.bpf gets sent as the filter, which needs to have been
    compiled by compile_filter.
    
    filt_instr_addr:
    Memory Address where FFShark programs the filter.
    
    Uses the sendfilt executable found in the 2 links:
    https://github.com/UofT-HPRC/fpga-bpf/tree/main/utilities/mpsoc_sendfilter

    Example usage under the description in compile_filter() 
    */
    
    //setting up prog.bpf string
    char cwd[PATH_MAX];
    char prog_file[PATH_MAX];
    getcwd(cwd, sizeof(cwd));    
    strcpy(prog_file, cwd);
    strcat(prog_file, "/prog.bpf ");

    char acceptall_file[] = "/home/savi/filterexecutables/acceptall.bpf ";
    char instr[1024];
    

    strcpy(instr, SEND_FILT_CMD);
    char addr[16];
    char hex_adr[16] = "0x";
    
    sprintf(addr, "%x", filt_instr_addr);
    strcat(hex_adr, addr);
    
    if (accept_all){
        strcat(instr, acceptall_file);
    }
    else {
        strcat(instr, prog_file);
    }
    strcat(instr, hex_adr);
    strcat(instr, SUPPRESS_OUTPUT);
    system(instr);
}

// Axi APIs
void init_axi(AXI *axi_handler, unsigned addr, unsigned size){
    /*
    AXI initializer.

    example:
    AXI axil_ffshark;
    init_axi(&axil_ffshark, 0xA0010000, 0x1000);

    ... some code operations ...

    uint64_t data = read_axi(&axil_ffshark, 0x10)

    ... some code operations ...

    write_axi(&axil_ffshark, 0x10, 0x25);

    */

    axi_handler->page_size = sysconf(_SC_PAGE_SIZE);

    if (addr % axi_handler->page_size != 0){
        perror("The address you want to map is not page aligned, exiting!");
    }
    if (size % axi_handler->page_size != 0){
        perror("Minimal allocating unit is one PAGE, exiting!");
    }
    axi_handler->size = size;
    axi_handler->fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (axi_handler->fd < 0){
        perror("Could not open /dev/mem !");
    }

    axi_handler->map_base = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, axi_handler->fd, addr);
    if (axi_handler->map_base == MAP_FAILED) {
        perror("Could not perform mmap");
    }
}

uint64_t read_axi(AXI *axi_handler, unsigned offset){
    //example usage in description under init_axi()
    return (*(volatile uint64_t *)(axi_handler->map_base + offset));
}

void write_axi(AXI *axi_handler, unsigned offset, uint64_t data){
    //example usage in description under init_axi()
    *(volatile uint64_t *)(axi_handler->map_base + offset) = data;
}

// Axilite APIs
void init_axilite(AXILITE *axilite_handler, unsigned addr, unsigned size){
    /*
    AXILITE initializer.

    example:
    AXILITE axil_ffshark;
    init_axilite(&axil_ffshark, 0xA0010000, 0x1000);

    ... some code operations ...

    unsigned data = read_axilite(&axil_ffshark, 0x10)

    ... some code operations ...

    write_axilite(&axil_ffshark, 0x10, 0x25);

    */

    axilite_handler->page_size = sysconf(_SC_PAGE_SIZE);

    if (addr % axilite_handler->page_size != 0){
        perror("The address you want to map is not page aligned, exiting!");
    }
    if (size % axilite_handler->page_size != 0){
        perror("Minimal allocating unit is one PAGE, exiting!");
    }
    axilite_handler->size = size;
    axilite_handler->fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (axilite_handler->fd < 0){
        perror("Could not open /dev/mem !");
    }

    axilite_handler->map_base = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, axilite_handler->fd, addr);
    if (axilite_handler->map_base == MAP_FAILED) {
        perror("Could not perform mmap");
    }
}

unsigned read_axilite(AXILITE *axilite_handler, unsigned offset){
    //example usage in description under init_axilite()
    return (*(volatile unsigned *)(axilite_handler->map_base + offset));
}

void write_axilite(AXILITE *axilite_handler, unsigned offset, unsigned data){
    //example usage in description under init_axilite()
    *(volatile unsigned *)(axilite_handler->map_base + offset) = data;
}