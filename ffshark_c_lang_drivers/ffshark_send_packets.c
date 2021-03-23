#include "libmpsoc.h"
#include <glob.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>
#include <inttypes.h>
#include <getopt.h>
#include <errno.h>
#include <math.h>

// Register constants
// The base addr can vary depending on FFShark and PS config, we really shouldn't hard code
#define FFSHARK_BASE 0xA0010000
#define FFSHARK_SIZE 0x1000 // 4KB mem map region
#define FFSHARK_ENABLE_OFFSET 0x4
#define FIFO_BASE 0xA0011000
#define FIFO_SIZE 0x1000 // 4KB mem map region
#define FIFO_TDFV_OFFSET 0xC
#define FIFO_TDFD_OFFSET 0x10
#define FIFO_TLR_OFFSET 0x14
#define FIFO_SRR_OFFSET 0x28
#define FIFO_SRR_RST_VAL 0xA5
#define FIFO_DATA_WIDTH 4 //in bytes

void print_help(){
    printf("usage: ffshark_send_packets [-n NUM] [-d DIRECTORY] [-r NUM] [-h]\n\n"
        "send pregenerated packets from text files to FFSHark.\n\n"
        "Optional Arguments:\n"
        "  -h, --help\n"
        "          Show this help message and exit\n"
        "  -n, --num-packets=NUM\n"
        "          The number of packets to send.\n"
        "          A value of -1 or less is equivalent to infinity. It is -1 by default\n"
        "  -r, --reset-fifo=NUM\n"
        "          Set it to any number besides 0 to reset the AXI send fifo. Set it to 0 to disable reset.\n" 
        "          Reset is disabled by default\n"
        "Mandatory Arguments:\n"
        "  -d, --directory=DIRECTORY\n"
        "          This is the directory of pregenerated test packets. These packets must be in .txt files \n"
);
    return;

}

int main(int argc, char **argv) {
    //Get user arguments
    int opt;
    int num_packets = -1;
    char *directory = NULL;
    char directory_pattern[1024];
    char *endptr;
    int option_index;
    int reset_fifo = 0;
    struct option long_options[] = {
        {"help", no_argument, NULL, 'h'},
        {"directory", required_argument, NULL, 'd'},
        {"num-packets", required_argument, NULL, 'n'},
        {"reset-fifo", required_argument, NULL, 'r'},
        {0, 0, 0, 0}
    };

    while ((opt = getopt_long(argc, argv, "n:f:h", long_options, &option_index)) != -1){
        switch(opt){
            case 'n':
                num_packets = strtol(optarg, &endptr, 10);
                if (endptr == optarg || *endptr != '\0'){
                    printf("ERROR: -n or --num-packets argument was not a valid integer.\nExiting.\n");
                    return 1;
                } else if (errno == ERANGE){
                    printf("ERROR: -n or --num-packets argument was too large and overflowed.\n"
                        "Try reducing NUM or setting to -1 for infinity.\nExiting\n");
                    return 1;
                }
                break;
            case 'd':
                directory = optarg;
                break;
            case 'r':
                reset_fifo = strtol(optarg, &endptr, 10);
                if (endptr == optarg || *endptr != '\0'){
                    printf("ERROR: -r or --reset-fifo argument was not a valid integer.\nExiting.\n");
                    return 1;
                } else if (errno == ERANGE){
                    printf("ERROR: -r or --reset-fifo argument was too large and overflowed.\n"
                        "to disable fifo --reset-fifo needs to be 0. To turn it on, --reset-fifo can be any other number.\n" 
                        "It does not have to be so large.\nExiting\n");
                    return 1;
                }
                break;
            case 'h':
                print_help();
                return 0;
            default:
                print_help();
                return 1;
        }
    }
  
    
    //get the directory pattern
    if (directory == NULL){
        printf ("You did not provide directory of packets");
        return -1;
    }
    strcpy(directory_pattern, directory);
    if (directory_pattern[strlen(directory_pattern)-1] == '/'){
        strcat(directory_pattern, "*.txt");
    }
    else {
        strcat(directory_pattern, "/*.txt");
    }
    
    //initialize locking mechanism
    lock_init();
    
    int lock_fd = lock();    
    //initialize axi lite mem maps for FFShark and FIFO
    AXILITE axil_ffshark;
    AXILITE axil_fifo;
    init_axilite(&axil_fifo, FIFO_BASE, FIFO_SIZE);
    init_axilite(&axil_ffshark, FFSHARK_BASE, FFSHARK_SIZE);
    
    //init FFShark and FIFO
    write_axilite(&axil_ffshark, FFSHARK_ENABLE_OFFSET, 0x1);
    if (reset_fifo != 0)
        write_axilite(&axil_fifo, FIFO_SRR_OFFSET, FIFO_SRR_RST_VAL);
    unlock(lock_fd);
    
    //get all the packet text files in the given directory
    glob_t file_names;
    int glob_res;    
    glob_res =  glob(directory_pattern, 0, NULL, &file_names);
    if (glob_res == GLOB_NOMATCH || glob_res == GLOB_ABORTED || glob_res == GLOB_NOSPACE){
        printf("Could not find matching pattern for files\n");
        printf("Either directory does not exist, or the directory does not have .txt files for its packets\n");
        return -1;
    }
    
    FILE *fp;
    struct stat st;
    int iteration_count = 0;
    int packet_file_index;
    unsigned num_vacant_words, num_words;
    unsigned packet_data;
    unsigned char word_buffer[10];
    word_buffer[0] = '0';
    word_buffer[1] = 'x';
        
    srand(time(NULL));

    //for profiling    
    double total_bytes = 0;
    double file_read_time = 0;
    double total_write_time = 0;
    double write_word_no_lock_time = 0;
    clock_t start_time = clock();
    
    while(iteration_count < num_packets || num_packets <= -1){
        
        //choose random packet file 
        packet_file_index = rand() % file_names.gl_pathc;
        if(stat(file_names.gl_pathv[packet_file_index], &st) != 0) {
            printf("invalid packet file");
            return -1;
        }
        
        //divide by 8 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        num_words = st.st_size / 8;
        total_bytes += st.st_size / 2;        
        
        //check if FIFO has enough space for packet
        lock_fd = lock();
        num_vacant_words = read_axilite(&axil_fifo, FIFO_TDFV_OFFSET);
        unlock(lock_fd);
        while (num_words - 8 > num_vacant_words){
            lock_fd = lock();
            num_vacant_words = read_axilite(&axil_fifo, FIFO_TDFV_OFFSET);
            unlock(lock_fd);
            printf("num vacant words: %u\n", num_vacant_words);
        }
        
        //write the packet one word at a time
        fp = fopen(file_names.gl_pathv[packet_file_index], "r");
        if (fp == NULL){
            printf("file open failed");
            return -1;
        }
        
        clock_t write_start = clock();
        lock_fd = lock();
        while (fread(&word_buffer[2], 8, 1, fp) > 0){
            //profile the amount of time to read out packet file
            clock_t file_start_time = clock();
            packet_data = strtoul((char *)word_buffer, NULL, 0);
            file_read_time += (double) (clock() - file_start_time)/(CLOCKS_PER_SEC/1000000);
            
            //profile register writing time
            clock_t write_word_start = clock();
            write_axilite(&axil_fifo, FIFO_TDFD_OFFSET, packet_data);
            write_word_no_lock_time += (clock() - write_word_start)/(CLOCKS_PER_SEC/1000000);
        }
        fclose(fp);        
        
        //Write the number of bytes to TLR
        //divide by 2 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        write_axilite(&axil_fifo, FIFO_TLR_OFFSET, (unsigned)(st.st_size / 2));
        unlock(lock_fd);        
        total_write_time += (double)(clock() - write_start)/(CLOCKS_PER_SEC/1000000);
        
        iteration_count+=1;
        //printf("iteration count: %d\n", iteration_count);
        
    }
    
    //print out profiling data
    clock_t end_time = clock();    
    double total_time = (double) (end_time - start_time)/(CLOCKS_PER_SEC/1000000);
    double bit_rate = ((total_bytes * 8)/total_time) * 1000000;
    printf("Total time : %f seconds\n", total_time / 1000000 );
    printf("Write time : %f seconds\n ", total_write_time / 1000000);
    printf("Write with no locking time : %f seconds\n ", write_word_no_lock_time / 1000000);
    printf("File read time: %f seconds\n", file_read_time / 1000000);
    printf("Bit rate : %f bits per second \n", bit_rate);

}