import os
import sys

if 'K5_ENV' in os.environ : # RC3 case
  sys.path.append(os.environ['K5_ENV']+'/py')
  sys.path.append(os.environ['MY_K5_PROJ']+'/sw/apps/cgol_shared_lib')  
else : # FPGA win env case
  sys.path.append(os.environ['K5_XBOX_FPGA']+'/py')
  sys.path.append(os.environ['K5_XBOX_FPGA']+'/sw/apps/cgol_shared_lib')

from k5_common import *
import cgol_animate_ref as sar

#-------------------------------------------------------------------------------------    

# Get the grid array (used by all animate methods)

def get_grid(self,np_grid) :

       num_bytes = self.rows*self.cols 
                  
       mem_id = XMEM if (self.grid_soc_addr >= XSPACE_BASE_ADDR) else DMEM ;            
       byteAddr = self.grid_soc_addr
         
       prev_ram_addr = -1     
       r,c,cnt = 0,0,0
       
       for byte_i in range(num_bytes) :         
           ramAddr = int(byteAddr) - int(byteAddr%4)  # Currently host can access only 'word aligned'             
           if (ramAddr!=prev_ram_addr) :
              data_word = self.k5s.read_tcm(mem_id,ramAddr)  
              prev_ram_addr = ramAddr
              
           byte_val = (data_word>>(8*(byteAddr%4))) & 0xff 
                                        
           for bit_i in range(8) :
             r = cnt // self.cols               
             c = cnt % self.cols

             np_grid[r,c] = (byte_val>>bit_i) & 1                                    
             cnt+=1
             
             if (cnt==num_bytes) :
               break

           if (cnt==num_bytes) :
               break
      
           byteAddr = byteAddr+1 ;               
               
#-------------------------------------------------------------------------------------    

def dump_grid(self) :
    
       dump_file_name = 't%d/cgol_post_gen.txt' % self.thread_id
    
       print("Post last generation grid dumped to %s" % dump_file_name)
    
       dump_f = open(dump_file_name,'w')

       for r in range(self.rows):
           for c in range(self.cols):
               dump_f.write('%c' % ('#' if self.grid[r,c]==1 else '.'))
           dump_f.write('\n')
              
       dump_f.close()

#-------------------------------------------------------------------------------------  

class Object(object):
  pass

#-------------------------------------------------------------------------------------  

# import multiprocessing

def check_grid(self,itr) :

     print('Checking Correct result of pattern %s after %d generations' % (self.pat_name,itr))   
     
     thread = self.k5s.threads_info[self.thread_id]
     is_cgol_xlr_tor = 'cgol_xlr_tor' in thread.app_src_dir_path
     if is_cgol_xlr_tor :
        print('Checker Detected wrap mode (torus cgol_xlr_tor)')
     else :
        print('Checker Detected non-wrap mode (base cgol_xlr)')

     
     args = Object()

     args.pic  = self.pat_name   # Input pattern name
     args.itr  = itr             # Number of generations
     args.fps  = 10              # Animation Frames (generations) per second     
     args.wrap = is_cgol_xlr_tor # Wrap Mode (Torus)
     args.fftl = True            # fast forward to last    
     
     ref = sar.cgol_animate(args) 
     
     ref.check_grid(self.grid) 

     return ref     
     
 
#-------------------------------------------------------------------------------------  

def save_ref_grid_img(self,ref,val_str)  :
  
  ref.save_ref_grid_img(self.thread_id,val_str)  

#-------------------------------------------------------------------------------------  


def set_elps_cyc_cnt(elps_cyc_cnt,ref) :  

  ref.set_elps_cyc_cnt(elps_cyc_cnt) 