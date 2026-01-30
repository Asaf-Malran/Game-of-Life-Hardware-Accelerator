import numpy as np
import pygame
import time
import sys
import os

if 'K5_ENV' in os.environ : # RC3 case
  sys.path.append(os.environ['MY_K5_PROJ']+'/sw/apps/cgol_shared_lib')
else : # FPGA win env case
  sys.path.append(os.environ['K5_XBOX_FPGA']+'/sw/apps/cgol_shared_lib')

import cgol_animate_shared as sas

#------------------------------------------------------------------------------------- 

class cgol_pygame_animate :
      
    def __init__(self, rows, cols, grid_soc_addr, k5s, thread_id):
   
      self.k5s = k5s
      self.thread_id = thread_id


      self.GRID_MAX_WIDTH = 256
      self.GRID_MAX_HEIGHT = 256
      
      self.pat_name = None
      
      self.rows = rows
      self.cols = cols      
      
      self.grid_soc_addr = grid_soc_addr
      
      self.grid = np.zeros((self.rows,self.cols))
      
      self.CELL_SIZE = int(640/max(self.cols,self.rows))
      
      self.WINDOW_WIDTH  = self.CELL_SIZE * self.cols
      self.WINDOW_HEIGHT = self.CELL_SIZE * self.rows + 30  # extra space for text
      self.FPS = 1
      
      # Colors        
      self.GRID_COLOR =  ( 40,  40,  40)
      self.BG_COLOR    = (  0,   0,  80)    # Dark blue background
      self.ALIVE_COLOR = (255, 255,   0)   # Bright yellow live cells
      self.TEXT_COLOR  = (200, 200, 200)
      
      self.screen = None
      self.clock = None    
      self.font = None 
      self.disp_init_done = False 
      # self.ref = None      
      
    #-------------------------------------------------------------------------------------    

    def set_pat_name(self,pat_name):      
      self.pat_name = pat_name

    #-------------------------------------------------------------------------------------    


    def init_display(self):

      pygame.init()
      self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
      pygame.display.set_caption("Conway's Game of Life (Pygame)")
      self.clock = pygame.time.Clock()     
      self.font = pygame.font.SysFont("consolas", 20) 
      self.disp_init_done = True     


    #--------------------------------------------------------------------------------------  
    
    def display_grid(self, itr, block, animate, val_str):
                
        if animate and not self.disp_init_done :
            self.init_display()
            
        sas.get_grid(self,self.grid)        
                                                                  
        # self.clock.tick(self.FPS)

        if not block :                                    
           self.screen.fill(self.BG_COLOR)
           self.draw_generation(itr)
           self.draw_grid(self.grid)        
           pygame.display.flip()
           
        else : # block till clicked (applied last generation)
 
           pygame.quit()
           

           ref = sas.check_grid(self,itr) # Check Correctness of final grid
                    
           sas.save_ref_grid_img(self,ref,val_str) 
              
                 
    #------------------------------------------------------------------------------------
    
    # Draw grid and cells
    def draw_grid(self, grid):
        for y in range(self.rows):
            for x in range(self.cols):
                color = self.ALIVE_COLOR if grid[y, x] == 1 else self.BG_COLOR
                rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE + 30, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
    
        # Draw grid lines
        for x in range(0, self.cols * self.CELL_SIZE, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 30), (x, self.WINDOW_HEIGHT))
        for y in range(30, self.rows * self.CELL_SIZE + 30, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.WINDOW_WIDTH, y))
    
    #------------------------------------------------------------------------------------
    
    # Draw generation text
    def draw_generation(self, generation):
        text = self.font.render(f"Generation: {generation}", True, self.TEXT_COLOR)
        self.screen.blit(text, (10, 5))
    
    #------------------------------------------------------------------------------------
    
    def print_in_box(self,text):
        lines = text.split('\n')
        max_len = max(len(line) for line in lines)

        print('\n')        
        # Top border
        print(" +" + "-" * (max_len + 2) + "+", flush=True)         
        # Text lines
        for line in lines:
            print(" | " + line.ljust(max_len) + " |", flush=True)            
        # Bottom border
        print(" +" + "-" * (max_len + 2) + "+", flush=True)
        print('\n')

    #------------------------------------------------------------------------------------
   
    def report_mesure_elapse(self,val_str,itr):

       elps_cyc_cnt = int(val_str.replace(',', '')) 

       cyc_per_sec = 50000000 ; #  Per 50 MHz
       elps_time_sec = elps_cyc_cnt/cyc_per_sec
              
       text = '\nPERFORMANCE:\n'
       text+= 'Measured %s elapse cycles for %d generations\n' %(val_str,itr)
       text+= 'Total %.3f seconds at 50 MHz for %d generations\n' % (elps_time_sec,itr)

       if itr!=0 :

         cyc_per_itr = elps_cyc_cnt/itr ;         
         text+='%.2f Cycles per Generation\n' % cyc_per_itr
         text+='%.2f Cycles per row\n' % (cyc_per_itr/self.rows)
         text+='%.2f Cycles per grid element\n' % (cyc_per_itr/(self.rows*self.cols))
         
       self.print_in_box(text)
        
            
    #------------------------------------------------------------------------------------

