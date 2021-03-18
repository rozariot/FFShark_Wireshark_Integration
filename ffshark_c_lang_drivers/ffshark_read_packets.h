#ifndef FFSHARK_READ_PACKETS_H
#define FFSHARK_READ_PACKETS_H


#include <stdint.h>

// ****************************************
// FFShark Constants
// ****************************************
// The base addr can vary depending on FFShark and PS config, we really shouldn't hard code
#define FIFO_BASE 0xA0011000
#define FIFO_SIZE 0x1000 // 4KB mem map region
#define FIFO_RDFO_OFFSET 0x1C
#define FIFO_RDFD_OFFSET 0x20
#define FIFO_RLR_OFFSET 0x24
#define FILT_INSTR_ADDR 0xA0010000


// ****************************************
// Profiling
// ****************************************
// Flag to print out profiling data
// Keep commented out if you want to view packets on Wireshark

// #define PROFILE


// ****************************************
// PCAP Structs
// ****************************************
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


#endif