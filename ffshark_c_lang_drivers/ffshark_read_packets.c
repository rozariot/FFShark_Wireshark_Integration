#include "libmpsoc.h"
#include <glob.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>

// Register constants
// The base addr can vary depending on FFShark and PS config, we really shouldn't hard code
#define FFSHARK_BASE 0xA0010000
#define FFSHARK_SIZE 0x1000 // 4KB mem map region
#define FFSHARK_ENABLE_OFFSET 0x4
#define FIFO_BASE 0xA0011000
#define FIFO_SIZE 0x1000 // 4KB mem map region
#define FIFO_TDFV_OFFSET 0xC
#define FIFO_TDFD_OFFSET 0x10
#define FIFO_RDFO_OFFSET 0x1C
#define FIFO_TLR_OFFSET 0x14
#define FIFO_RDFD_OFFSET 0x20
#define FIFO_RLR_OFFSET 0x24
#define FIFO_SRR_OFFSET 0x28
#define FIFO_SRR_RST_VAL 0xA5
#define FIFO_DATA_WIDTH 4 //in bytes

#define num_packets 100 //will need to set this as a user parameter later


typedef struct pcap_hdr_s {
    uint32_t magic_number;   /* magic number */
    uint16_t version_major;  /* major version number */
    uint16_t version_minor;  /* minor version number */
    int32_t  thiszone;       /* GMT to local correction */
    uint32_t sigfigs;        /* accuracy of timestamps */
    uint32_t snaplen;        /* max length of captured packets, in octets */
    uint32_t network;        /* data link type */
} pcap_hdr_t;


typedef struct pcaprec_hdr_s {
    uint32_t ts_sec;         /* timestamp seconds */
    uint32_t ts_usec;        /* timestamp microseconds */
    uint32_t incl_len;       /* number of octets of packet saved in file */
    uint32_t orig_len;       /* actual length of packet */
} pcaprec_hdr_t;


//From https://stackoverflow.com/questions/40193322/how-to-fwrite-and-fread-endianness-independant-integers-such-that-i-can-fwrite
//Need to be other endianness from usual fwrite.
//Could optimize this since will always be same size if "malloc()" is too slow.
size_t endian_swap_fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    unsigned char *buffer_src = (unsigned char*)ptr;
    unsigned char *buffer_dst = (unsigned char *) malloc(size*nmemb);
    for (size_t i = 0; i < nmemb; i++)
    {
        for (size_t ix = 0; ix < size; ix++) {
            buffer_dst[size * i + (size - 1 - ix)] = buffer_src[size * i + ix];
        }
    }
    size_t result = fwrite(buffer_dst, size, nmemb, stream);
    free(buffer_dst);
    return result;
}


void init_pcap_header(pcap_hdr_t *pcap_hdr){
    pcap_hdr->magic_number = 0xA1B2C3D4;
    pcap_hdr->version_major = 0x02;
    pcap_hdr->version_minor = 0x04;
    pcap_hdr->thiszone = 0x00;
    pcap_hdr->sigfigs = 0x00;
    pcap_hdr->snaplen = 65535;
    pcap_hdr->network = 1;
    return;
}

void fill_in_pcaprec_hdr(pcaprec_hdr_t *pcaprec_hdr, unsigned num_bytes){
    struct timeval current_time;
    gettimeofday(&current_time, NULL);
    pcaprec_hdr->ts_sec = current_time.tv_sec;
    pcaprec_hdr->ts_usec = current_time.tv_usec;
    pcaprec_hdr->incl_len = num_bytes;
    pcaprec_hdr->orig_len = num_bytes;

}

int main(int argc, char **argv) {


    //initialize axi lite mem maps for FFShark and FIFO
    AXILITE axil_fifo;
    lock_init();
    int lock_fd = lock();
    init_axilite(&axil_fifo, FIFO_BASE, FIFO_SIZE);
    unlock(lock_fd);

    //init FIFO
    // write_axilite(&axil_fifo, FIFO_SRR_OFFSET, FIFO_SRR_RST_VAL);
    //TODO: RELEASE LOCK

    int iteration_count = 0;

    pcap_hdr_t pcap_hdr;
    init_pcap_header(&pcap_hdr);
    fwrite(&pcap_hdr, sizeof(pcap_hdr), 1, stdout);

    pcaprec_hdr_t pcaprec_hdr;

    while(iteration_count < num_packets){

        lock_fd = lock();
        // check if Receive FIFO has packets to read, if not don't read
        unsigned num_words_in_fifo = read_axilite(&axil_fifo, FIFO_RDFO_OFFSET);
        unlock(lock_fd);

        if (num_words_in_fifo > 0){
            lock_fd = lock();
            unsigned num_bytes_in_packet = read_axilite(&axil_fifo, FIFO_RLR_OFFSET);
            unsigned num_words_in_packet = (unsigned) ceil((float) num_bytes_in_packet / 4.0);
            fill_in_pcaprec_hdr(&pcaprec_hdr, num_bytes_in_packet);
            fwrite(&pcaprec_hdr, sizeof(pcaprec_hdr), 1, stdout);

            for (int i = 0; i < num_words_in_packet; i++){
                unsigned data_word = read_axilite(&axil_fifo, FIFO_RDFD_OFFSET);
                endian_swap_fwrite(&data_word, sizeof(unsigned), 1, stdout);
                // printf("%x ", data_word);
            }
            fflush(stdout);
            // printf("\n");
            unlock(lock_fd);
        }
        // printf("iteration %d\n", iteration_count);


        iteration_count+=1;

    }



}