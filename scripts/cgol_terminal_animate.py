import time
import sys
import os
import random
from colorama import deinit,Fore, Cursor
from colorama import init as colorama_init
import numpy as np

if 'K5_ENV' in os.environ : # RC3 case
  sys.path.append(os.environ['K5_ENV']+'/py')
else : # FPGA win env case
  sys.path.append(os.environ['K5_XBOX_FPGA']+'/py')
from k5_common import *

sys.path.append(os.environ['K5_XBOX_ENV']+'/aw/apps/cgol_shared_lib')
import cgol_animate_shared as sas

#------------------------------------------------------

class cgol_terminal_animate:
      
    def __init__(self, rows, cols, grid_soc_addr, thread_id, k5s):
    
      self.rows = rows
      self.cols = cols 
      self.grid_soc_addr = grid_soc_addr    
      self.thread_id = thread_id
      self.k5s = k5s
      
      self.crnt_grid = np.zeros((self.rows,self.cols))
      self.next_grid = np.zeros((self.rows,self.cols))

      self.on_char = Fore.GREEN + '\u25AE' # solid square
      self.off_char = Fore.BLUE + '\u22C5' # (dot-operator)
      self.step_time = 0.01 # Seconds
      
      print('\033[?25l', end="") # Needed to hide the blinking cursor.
          
      colorama_init()
                 
      self.init_display_grid() 
                    
    #-------------------------------------------------------------------------------------    

     # Update a single cell on the grid
    def update_cell(self,row, col, char) :
         # Each cell has a space, so column offset is col * 2
         sys.stdout.write(Cursor.POS(col + 1, row + 1))  # Notice "Cursor" first non-spaced col,row is 1,1 not 0,0
         sys.stdout.write(char)
         sys.stdout.flush()

    #-------------------------------------------------------------------------------------    
     
    def init_display_grid(self):
    
      self.clear_screen() 
    
      for row in range(self.rows):
        for col in range(self.cols):    
          self.update_cell(row, col, self.off_char)
 
      return 1 # Indicates 'done'

    #-------------------------------------------------------------------------------------    
 
    # Clear screen
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
 
    #-------------------------------------------------------------------------------------    
  
    # Print the grid array
    def display_grid(self,gen) :
    
        sas.get_grid(self,self.next_grid)

        for row in range(self.rows):
          for col in range(self.cols):
            if (self.next_grid[row,col] != self.crnt_grid[row,col])   :
               char_type = self.off_char if (self.next_grid[row,col]==0) else self.on_char            
               self.update_cell(row, col, char_type)
        
        self.update_cell(self.rows+1,0, ('Generation %d\n'%gen))
        
        # Swap current and next grid np references
        prev_crnt_grid = self.crnt_grid        
        self.crnt_grid = self.next_grid
        self.next_grid = prev_crnt_grid

        return 1 # Indicate done

    #-------------------------------------------------------------------------------------    
 
    def animate_terminate(self) :
    
       deinit()
       
       # Move cursor below grid to avoid overwriting
       sys.stdout.write(Cursor.POS(1, self.rows + 2))
       
       print('\033[?25h', end="") # Turn on back the blinking cursor.


