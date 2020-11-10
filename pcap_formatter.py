import sys, getopt
import binascii
import os
import datetime


## Reference: https://www.tcpdump.org/manpages/pcap-savefile.5.html
## Reference : https://wiki.wireshark.org/Development/LibpcapFileFormat

#Global header for pcap 2.4
pcap_global_header =   ('D4 C3 B2 A1'   
                        '02 00'         #File format major revision (i.e. pcap <2>.4)  
                        '04 00'         #File format minor revision (i.e. pcap 2.<4>)   
                        '00 00 00 00'     
                        '00 00 00 00'     
                        'FF FF 00 00'     
                        '01 00 00 00')

#pcap packet header that must preface every packet
pcap_packet_header =   ('SS SS SS SS'   #Time stamp seconds since Jan 1 1970  
                        'UU UU UU UU'   #Time stamp additional microseconds   
                        'XX XX XX XX'   #Frame Size (little endian) 
                        'YY YY YY YY')  #Frame Size (little endian)

MICROSECS_PER_SEC = 1000000

def writeByteStringToFile(bytestring, filename):
    bytelist = bytestring.split()  
    #print(''.join(bytelist))
    bytes = binascii.a2b_hex(''.join(bytelist))
    bitout = open(filename, 'wb')
    bitout.write(bytes)

# set time stamp with reference to jan 1 1970               
def get_unix_timestamp_secs():
    curr_date = datetime.datetime.now()
    ref_date = datetime.datetime(1970, 1, 1)
    delta = curr_date - ref_date
    return delta.total_seconds()

def generatePCAP(raw_packet_file,pcapfile): 

    readfile = open(raw_packet_file, 'rb')
    readfile_size = os.path.getsize(raw_packet_file)
    raw_packet_data = readfile.read(readfile_size)   
    #raw_packet_hex = raw_packet_data.hex()

    #set packet size
    hex_str_filesize = "%08x"%readfile_size
    reverse_hex_str_filesize = hex_str_filesize[6:] + hex_str_filesize[4:6] + hex_str_filesize[2:4] + hex_str_filesize[:2]
    pcaph = pcap_packet_header.replace('XX XX XX XX',reverse_hex_str_filesize)
    pcaph = pcaph.replace('YY YY YY YY',reverse_hex_str_filesize)

    #set seconds and microseconds time stamp
    time_total_secs = get_unix_timestamp_secs()
    time_secs = int(time_total_secs)
    time_usecs = (time_total_secs - time_secs) * MICROSECS_PER_SEC 
    hex_str_secs = "%08x"%(time_secs)
    reverse_hex_str_secs = hex_str_secs[6:] + hex_str_secs[4:6] + hex_str_secs[2:4] + hex_str_secs[:2]
    hex_str_usecs = "%08x"%(int(time_usecs))
    reverse_hex_str_usecs = hex_str_usecs[6:] + hex_str_usecs[4:6] + hex_str_usecs[2:4] + hex_str_usecs[:2]
    pcaph = pcaph.replace('UU UU UU UU',reverse_hex_str_usecs)
    pcaph = pcaph.replace('SS SS SS SS',reverse_hex_str_secs)

    pcap_headers_string = pcap_global_header + pcaph
    bytestring = binascii.a2b_hex(''.join((pcap_headers_string.split()))) + raw_packet_data
    writefile = open(pcapfile, 'wb')
    writefile.write(bytestring)

"""------------------------------------------"""
""" End of functions, execution starts here: """
"""------------------------------------------"""
def main():

    inputfile = ''
    outputfile = ''
    try:
       opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
       print ('pcap_formatter.py -i <inputfile> -o <outputfile>')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print ('test.py -i <inputfile> -o <outputfile>')
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg
       elif opt in ("-o", "--ofile"):
          outputfile = arg


    # create a .pcap file and then output it to the stdout terminal 
    # for it to be recognized remotely through sshdump
    generatePCAP(inputfile, outputfile)
    file = open(outputfile, 'rb')
    print(file.read())

if __name__ == "__main__":
    main()



