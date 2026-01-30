import argparse
import os

# Convert cgol binary picture to hex format.

ap = argparse.ArgumentParser(description='Convert cgol binary picture to hex format',formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument('pic', metavar='<inpat_name>', default=None, type=str, help='Input pattern name') 
args = ap.parse_args()

K5_SW_APPS_PATH = os.environ["K5_SW_APPS"].replace('/c/','c:/')
pic_file = open(K5_SW_APPS_PATH + '/cgol_shared_lib/cgol_patterns/' + args.pic + '.txt','r')

hex_file = open('cgol_hex_in.txt','w') ;
conf_file = open('cgol_conf.txt','w') ;

byte_val = 0
bit_idx = 0
bytes_list = []

# Capture bytes
total_bits = 0 
for orig_line_count, line in enumerate(pic_file) :
  for p in line[:-1] : # exclude eol
    if p=='#' :
      byte_val+= 1<<bit_idx
    bit_idx+=1
    if bit_idx==8 :
       bytes_list.append(byte_val)
       byte_val = 0
       bit_idx  = 0
       
    if p in ['#','.'] :
      total_bits +=1       
       
if len(line.split())>0 :
  orig_line_count+=1       
       
# Generate hex file

width = total_bits//orig_line_count

# pad with zeros in case not word divided.
if len(bytes_list)%4 != 0 :
  for i in range (4-(len(bytes_list)%4)) :
    bytes_list.append(0)
        
bytes_per_line = len(bytes_list)//orig_line_count
gen_line_bytes_cnt = 0
for byte in bytes_list :
   hex_file.write(' %02x' % byte)
   gen_line_bytes_cnt+=1
   if gen_line_bytes_cnt >= bytes_per_line :
      hex_file.write('\n')
      gen_line_bytes_cnt = 0
  
conf_file.write('%s %d %d\n' %(args.pic, orig_line_count, width))
  
pic_file.close()
hex_file.close()
conf_file.close()