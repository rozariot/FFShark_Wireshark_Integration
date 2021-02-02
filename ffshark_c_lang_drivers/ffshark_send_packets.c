#include "libmpsoc.h"
#include <glob.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>

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

#define num_packets 3 //will need to set this as a user parameter later

char directory_pattern[] = "/home/savi/tobias/ffshark_tut/sample_packets/multiple_8/*.txt"; //will need to set this user parameter later

int main(int argc, char **argv) {
    
    
    //initialize axi lite mem maps for FFShark and FIFO
    AXILITE axil_ffshark;
    AXILITE axil_fifo;
    init_axilite(&axil_fifo, FIFO_BASE, FIFO_SIZE);
    init_axilite(&axil_ffshark, FFSHARK_BASE, FFSHARK_SIZE);
    
    //init FFShark and FIFO
    write_axilite(&axil_ffshark, FFSHARK_ENABLE_OFFSET, 0x1);
    write_axilite(&axil_fifo, FIFO_SRR_OFFSET, FIFO_SRR_RST_VAL);
    
    //get all the packet text files in the given directory
    glob_t file_names;
    int glob_res;    
    glob_res =  glob(directory_pattern, 0, NULL, &file_names);
    if (glob_res == GLOB_NOMATCH || glob_res == GLOB_ABORTED || glob_res == GLOB_NOSPACE){
        printf("Could not find matching pattern for files");
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
    while(iteration_count < num_packets){
        
        //choose random packet file 
        packet_file_index = rand() % file_names.gl_pathc;
        if(stat(file_names.gl_pathv[packet_file_index], &st) != 0) {
            printf("invalid packet file");
            return -1;
        }
        
        //divide by 8 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        num_words = st.st_size / 8; 
        
        //check if FIFO has enough space for packet
        num_vacant_words = read_axilite(&axil_fifo, FIFO_TDFV_OFFSET);
        while (num_words - 8 > num_vacant_words){
            num_vacant_words = read_axilite(&axil_fifo, FIFO_TDFV_OFFSET);
            printf("num vacant words: %u\n", num_vacant_words);
        }
        
        //write the packet one word at a time
        fp = fopen(file_names.gl_pathv[packet_file_index], "r");
        if (fp == NULL){
            printf("file open failed");
            return -1;
        }
        while (fread(&word_buffer[2], 8, 1, fp) > 0){
            packet_data = strtoul(word_buffer, NULL, 0);
            write_axilite(&axil_fifo, FIFO_TDFD_OFFSET, packet_data);
        }
        
        //Write the number of bytes to TLR
        //divide by 2 because each hex char is UTF-8 so 1 byte but it represents only 4 bits so it's 2x the data
        write_axilite(&axil_fifo, FIFO_TLR_OFFSET, (unsigned)(st.st_size / 2));
        
        iteration_count+=1;
        
    }

}