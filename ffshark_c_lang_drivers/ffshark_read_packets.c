#include "ffshark_read_packets.h"
#include "libmpsoc.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/time.h>
#include <math.h>
#include <getopt.h>

#ifdef PROFILE
#include <time.h>
#endif


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
    return;
}

void print_help(){
    printf("usage: ffshark_read_packets [-n NUM] [-f FILTER] [-h]\n\n"
        "Read FFShark filtered packets and prints them to terminal in PCAP format.\n\n"
        "Optional Arguments:\n"
        "  -h, --help\n"
        "          Show this help message and exit\n"
        "  -n, --num-iterations=NUM\n"
        "          The maximum number of packets to read before exiting.\n"
        "          A value of -1 is equivalent to infinity.\n"
        "  -f, --filter=FILTER\n"
        "          The BPF filter to be used in FFShark.\n");
    return;

}

int main(int argc, char **argv) {

    //Get user arguments
    int opt;
    int num_packets = -1;
    char *filter = NULL;
    char *endptr;
    int option_index;
    struct option long_options[] = {
        {"help", no_argument, NULL, 'h'},
        {"filter", required_argument, NULL, 'f'},
        {"num-iterations", required_argument, NULL, 'n'},
        {0, 0, 0, 0}
    };

    while ((opt = getopt_long(argc, argv, "n:f:h", long_options, &option_index)) != -1){
        switch(opt){
            case 'n':
                num_packets = strtol(optarg, &endptr, 10);
                if (endptr == optarg || *endptr != '\0'){
                    printf("ERROR: -n or --num-iterations argument was not a valid integer.\nExiting.\n");
                    return 1;
                } else if (errno == ERANGE){
                    printf("ERROR: -n or --num-iterations argument was too large and overflowed.\n"
                        "Try reducing NUM or setting to -1 for infinity.\nExiting\n");
                    return 1;
                }
                break;
            case 'f':
                filter = optarg;
                break;
            case 'h':
                print_help();
                return 0;
            default:
                print_help();
                return 1;
        }
    }

    //Error checking
    if (num_packets == 0 || num_packets < -1){
        printf("ERROR: -n or --num-iterations argument must be greater than 0 or equal to -1 (for infinity).\n"
            "Input was: %d\nExiting\n", num_packets);
        return 1;
    }

    //initialize axi lite mem maps for FFShark and FIFO
    AXILITE axil_fifo;
    lock_init();
    int lock_fd = lock();
    init_axilite(&axil_fifo, FIFO_BASE, FIFO_SIZE);
    unlock(lock_fd);

    int iteration_count = 0;

    pcap_hdr_t pcap_hdr;
    init_pcap_header(&pcap_hdr);
    fwrite(&pcap_hdr, sizeof(pcap_hdr), 1, stdout);

    pcaprec_hdr_t pcaprec_hdr;

#ifdef PROFILE
    //for profiling
    double total_bytes = 0;
    double fifo_read_time_no_lock = 0;
    double print_to_terminal_time = 0;
    double pcap_format_time = 0;
    clock_t start_time = clock();
#endif

    while(num_packets == -1 || iteration_count < num_packets){

        lock_fd = lock();
        // check if Receive FIFO has packets to read, if not don't read
        unsigned num_words_in_fifo = read_axilite(&axil_fifo, FIFO_RDFO_OFFSET);
        unlock(lock_fd);

        if (num_words_in_fifo > 0){
            lock_fd = lock();
            unsigned num_bytes_in_packet = read_axilite(&axil_fifo, FIFO_RLR_OFFSET);
            unsigned num_words_in_packet = (unsigned) ceil((float) num_bytes_in_packet / 4.0);
#ifdef PROFILE
            clock_t pcap_header_start = clock();
#endif
            fill_in_pcaprec_hdr(&pcaprec_hdr, num_bytes_in_packet);
            fwrite(&pcaprec_hdr, sizeof(pcaprec_hdr), 1, stdout);
#ifdef PROFILE
            pcap_format_time += (double) (clock() - pcap_header_start)/(CLOCKS_PER_SEC/1000000);
#endif
            for (int i = 0; i < num_words_in_packet; i++){
#ifdef PROFILE
                clock_t read_start_time = clock();
#endif
                unsigned data_word = read_axilite(&axil_fifo, FIFO_RDFD_OFFSET);
#ifdef PROFILE
                fifo_read_time_no_lock += (double) (clock() - read_start_time)/(CLOCKS_PER_SEC/1000000);

                clock_t format_start = clock();
#endif
                endian_swap_fwrite(&data_word, sizeof(unsigned), 1, stdout);
#ifdef PROFILE
                pcap_format_time += (double) (clock() - format_start)/(CLOCKS_PER_SEC/1000000);
#endif
                // printf("%x ", data_word);
            }
            unlock(lock_fd);
#ifdef PROFILE
            clock_t terminal_print_start = clock();
#endif
            fflush(stdout);
#ifdef PROFILE
            print_to_terminal_time += (double) (clock() - terminal_print_start)/(CLOCKS_PER_SEC/1000000);

            // printf("\n");


            total_bytes += num_bytes_in_packet;
#endif
            iteration_count+=1;
            // printf("iteration %d\n", iteration_count);
        }
    }

    //print out profiling data
#ifdef PROFILE
    clock_t end_time = clock();
    double total_time = (double) (end_time - start_time)/(CLOCKS_PER_SEC/1000000);
    double bit_rate = ((total_bytes * 8)/total_time) * 1000000;
    printf("\nTotal time : %f seconds\n", total_time / 1000000 );
    printf("Fifo read time without locking : %f seconds\n ", fifo_read_time_no_lock / 1000000);
    printf("Printing to terminal time : %f seconds\n ", print_to_terminal_time / 1000000);
    printf("PCAP formatting time: %f seconds\n", pcap_format_time / 1000000);
    printf("Data rate : %f bits/second \n", bit_rate);
#endif

    return 0;

}
