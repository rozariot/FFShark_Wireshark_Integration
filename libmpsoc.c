#include "libmpsoc.h"


void init_axilite(AXILITE *axilite_handler, int addr, int size){
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
        perror("Could not openh /dev/mem !");
    }
    
    axilite_handler->map_base = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, axilite_handler->fd, addr);    
    if (axilite_handler->map_base == MAP_FAILED) {
        perror("Could not perform mmap");
    }
}