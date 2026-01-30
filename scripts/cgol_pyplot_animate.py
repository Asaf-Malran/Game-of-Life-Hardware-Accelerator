import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

sys.path.append(os.environ['K5_XBOX_ENV']+'/aw/apps/cgol_shared_lib')
import cgol_animate_shared as sas

class cgol_pyplot_animate :
      
    def __init__(self, rows, cols, grid_soc_addr, k5s):
    
      self.k5s  = k5s
      self.rows = rows
      self.cols = cols    
      self.grid_soc_addr = grid_soc_addr  
      self.crnt_grid = np.zeros((self.rows,self.cols))
      self.next_grid = np.zeros((self.rows,self.cols))
           
      rows_tick_freq = 1 if self.rows <= 32 else (5 if self.rows <= 128 else 10)
      self.rows_tick_indexes = np.arange(0.5,self.rows,rows_tick_freq)
      self.rows_tick_labels = np.arange(0,self.rows,rows_tick_freq)        

      cols_tick_freq = 1 if self.cols <= 32 else (5 if self.cols <= 128 else 10)
      self.cols_tick_indexes = np.arange(0.5,self.cols,cols_tick_freq)
      self.cols_tick_labels = np.arange(0,self.cols,cols_tick_freq)            
             
      self.plt_ticks_setup()  # TODO: Not sure why this needs to be called every display update      
      self.set_grid_lines()       
      self.display_grid(itr=0, block=False)

    #-------------------------------------------------------------------------------------    
   
    def set_grid_lines(self):
     # display grid lines     
      DISPLAY_GRID_LINES = (self.rows <= 128) and (self.cols <= 128)
      if DISPLAY_GRID_LINES :
         for x in range(self.rows + 1):
             plt.axhline(x, color='gray', linewidth=0.5) 
         for y in range(self.cols + 1):
             plt.axvline(y, color='gray', linewidth=0.5)
   
    #-------------------------------------------------------------------------------------    
  
    def plt_ticks_setup(self):
    
      # Set ticks in the middle of rows and columns
      plt.xticks(self.cols_tick_indexes, labels=self.cols_tick_labels, fontsize = 8, rotation=90)  # Midpoints for columns
      plt.yticks(self.rows_tick_indexes, labels=self.rows_tick_labels, fontsize = 8)   # Midpoints for rows    
      
    #-------------------------------------------------------------------------------------    
    
    def display_grid(self, itr, block):
             
      plt.title("Generation %d" % itr)   

      sas.get_grid(self,self.crnt_grid)

      plt.pcolormesh(self.crnt_grid, shading='auto', cmap='binary')
 
      plt.gca().invert_yaxis() # we want rows to display from top to bottom 
      plt.gca().set_aspect('equal')  # Ensures square pixels 
      self.set_grid_lines()
      plt.show(block=block)      
      # plt.draw()
      
      plt.pause(0.001) # Not sure why this is needed, miss-displayed if removed.
      if not block : 
        plt.clf() # Clear figure
        
      # Swap current and next grid np references
      prev_crnt_grid = self.crnt_grid        
      self.crnt_grid = self.next_grid
      self.next_grid = prev_crnt_grid
       
      return 1 # Indicates 'done'

 
 
