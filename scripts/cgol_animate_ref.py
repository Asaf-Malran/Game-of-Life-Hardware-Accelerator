import pygame
import numpy as np
import sys
import argparse
import os
from scipy.signal import convolve2d
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#------------------------------------------------------------------------------------

# Invocation Example: 
# Cloud: python $MY_K5_PROJ/sw/apps/cgol_shared_lib/cgol_animate_ref.py cgol_64x64_edna -itr 1001 -wrap

#------------------------------------------------------------------------------------

class cgol_animate :
      
    def __init__(self,args):

        self.args = args
        self.GRID_MAX_WIDTH = 256
        self.GRID_MAX_HEIGHT = 256
       
        self.GRID_WIDTH = None
        self.GRID_HEIGHT = None
        
        self.start_grid = None
        self.grid = None
        self.checked_grid = None
        self.check_ok = None

        self.rows = None
        self.cols = None
        
        self.get_start_pic()
        
        self.CELL_SIZE = int(640/max(self.GRID_WIDTH,self.GRID_HEIGHT))
        
        self.WINDOW_WIDTH  = self.CELL_SIZE * self.GRID_WIDTH
        self.WINDOW_HEIGHT = self.CELL_SIZE * self.GRID_HEIGHT + 30  # extra space for text
        self.FPS = self.args.fps
        
        # Colors        
        self.GRID_COLOR =  ( 40,  40,  40)
        self.BG_COLOR    = (  0,   0,  80)   # Dark blue background
        self.ALIVE_COLOR = (255, 255,   0)   # Bright yellow live cells
        self.TEXT_COLOR  = (200, 200, 200)
                
    #------------------------------------------------------------------------------------
 
    def get_start_pic (self) :
    
       K5_SW_APPS_PATH = os.environ["K5_SW_APPS"].replace('/c/','c:/')
       pic_file = open(K5_SW_APPS_PATH + '/cgol_shared_lib/cgol_patterns/' + self.args.pic + '.txt','r')

       self.start_grid = np.zeros((self.GRID_MAX_HEIGHT, self.GRID_MAX_WIDTH), dtype=int)

       total_elements = 0 
       row_idx = 0
       for orig_line_count, line in enumerate(pic_file) :
         col_idx = 0
         row_present = False
         for p in line[:-1] : # exclude eol
             if p in ['#','.'] :
                 total_elements +=1
                 row_present = True             
                 if p=='#'  : 
                    self.start_grid[row_idx][col_idx] = 1
             col_idx+=1    
             
         if row_present:
           row_idx+=1
         
       if len(line.split())>0 :
         orig_line_count+=1
                     
       width = total_elements//orig_line_count
                      
       self.GRID_HEIGHT = orig_line_count
       self.GRID_WIDTH  = width

       self.start_grid = self.start_grid[:self.GRID_HEIGHT, :self.GRID_WIDTH]
                 
       pic_file.close()
       
       self.grid =self.create_grid()

    #------------------------------------------------------------------------------------

    # Initialize grid
    def create_grid(self):
         return self.start_grid[:][:]
    
    #------------------------------------------------------------------------------------
        
    # Update grid based on rules
    def update_grid(self,grid):
                  
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        
        # Count neighbors using 2D convolution
        if self.args.wrap :
           neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
        else :
           neighbors = convolve2d(grid, kernel, mode='same', boundary='fill', fillvalue=0)
        
        # Apply Conway's Game of Life rules
        birth = (grid == 0) & (neighbors == 3)
        survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
        
        # Return the next generation
        return np.where(birth | survive, 1, 0)        
            
    #------------------------------------------------------------------------------------

    # Update grid based on rules
    def update_grid_num_itr(self):
    
        seen = {}
        gen = 0 ;
        for gen in range(self.args.itr) : 
        
            h = hash(self.grid.tobytes())
            if h in seen:
                loop_start = seen[h]
                loop_length = gen - loop_start
                remaining = self.args.itr - gen
                fast_forward = remaining % loop_length
                ff_base_itr = remaining-fast_forward
                print('Checker Repeated grid detected at generation %d, fast-forwarding %d generations.\n' % (gen,ff_base_itr))
                
                for ff_i in range(fast_forward):
                   self.grid = self.update_grid(self.grid)                    
                break
 
            seen[h] = gen
            self.grid = self.update_grid(self.grid)
            
        print('Checker: done %d Generations ...' % self.args.itr, flush=True)
            
    #------------------------------------------------------------------------------------
    
    # Draw grid and cells
    def draw_grid(self,screen, grid):
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                color = self.ALIVE_COLOR if grid[y, x] == 1 else self.BG_COLOR
                rect = pygame.Rect(x*self.CELL_SIZE, y * self.CELL_SIZE + 30, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(screen, color, rect)
    
        # Draw grid lines
        for x in range(0, self.GRID_WIDTH * self.CELL_SIZE, self.CELL_SIZE):
            pygame.draw.line(screen, self.GRID_COLOR, (x, 30), (x, self.WINDOW_HEIGHT))
        for y in range(30, self.GRID_HEIGHT * self.CELL_SIZE + 30, self.CELL_SIZE):
            pygame.draw.line(screen, self.GRID_COLOR, (0, y), (self.WINDOW_WIDTH, y))
            
    #------------------------------------------------------------------------------------
    
    # Draw generation text
    def draw_generation(self, screen, generation, font):
        text = font.render(f"{self.args.pic} Generation: {generation}", True, self.TEXT_COLOR)
        screen.blit(text, (10, 5))
    
    #------------------------------------------------------------------------------------


    def save_grid_img(self,thread_id,grid,img_filename):

        # Save a Conway Game of Life grid using Pygame rendering.
                                      
        cell_color = (255, 255,  0) # Alive cell color
        bg_color   = (  0,   0, 80) # background
        grid_color = ( 40,  40, 40) # grid lines
                
        cell_size = self.CELL_SIZE
              
        rows, cols = grid.shape
        self.rows = rows
        self.cols = cols
        width, height = cols * cell_size, rows * cell_size
    
        pygame.init()
        surface = pygame.Surface((width, height))
        surface.fill(bg_color)
    
        for y in range(rows):
            for x in range(cols):
                if grid[y, x] == 1:
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(surface, cell_color, rect)

        # Draw grid lines
        for x in range(0, cols * cell_size, cell_size):
            pygame.draw.line(surface, grid_color, (x,0), (x, height))
        for y in range(0, height, cell_size):
            pygame.draw.line(surface, grid_color, (0,y), (width, y))
    
        pygame.image.save(surface, img_filename)
        pygame.quit()
        print(f"Saved grid to {img_filename}")

    #------------------------------------------------------------------------------------

    def disp_dual_img(self,thread_id,val_str) :
            
        # Load images using matplotlib
        gen_img_filename ='t%d/generated_grid.png' % thread_id       
        exp_img_filename ='t%d/expected_grid.png' % thread_id
            
        gen_img = mpimg.imread(gen_img_filename)    
        exp_img = mpimg.imread(exp_img_filename)
        
        # Create side-by-side plot
        fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    
        axes[0].imshow(gen_img)
        axes[0].axis('off')
        axes[0].set_title('Generated Image')
        
        axes[1].imshow(exp_img)
        axes[1].axis('off')
        axes[1].set_title('Expected Image')

        # Add common title
 
        if self.check_ok :
          title_text = 'PASS! %s after %d generation match expected.\n' % (self.args.pic,self.args.itr)
          
          elps_cyc_cnt = int(val_str.replace(',', '')) 
          
          # print('DBG elps_cyc_cnt = %s'  % str(elps_cyc_cnt))
          if elps_cyc_cnt!=0 :
          
              cyc_per_sec = 50000000 ; #  Per 50 MHz
              elps_time_sec = elps_cyc_cnt/cyc_per_sec
                     
              title_text+= '%s cycles for %d generations, ' %(val_str,self.args.itr)
              title_text+= 'Total time %.3f seconds at 50 MHz.\n' % elps_time_sec
              
              if self.args.itr!=0 :              
                cyc_per_itr = elps_cyc_cnt/self.args.itr ;         
                title_text+='%d Cycles per Generation, ' % cyc_per_itr
                title_text+='%.1f cycles per row, ' % (cyc_per_itr/self.rows)
                title_text+='%.2f cycles per element.' % (cyc_per_itr/(self.rows*self.cols))

          
          plt.suptitle(title_text, fontsize=10, color='green', x=0.0, ha='left')
        else :
          plt.suptitle('FAIL! %s after %d generation NOT matching expected' % (self.args.pic,self.args.itr), fontsize=16, color='red')        
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for suptitle
            
        plt.show()

    #------------------------------------------------------------------------------------

    def save_ref_grid_img(self,thread_id,val_str):
       img_filename ='t%d/expected_grid.png' % thread_id
       self.save_grid_img(thread_id, self.grid,img_filename)
       img_filename ='t%d/generated_grid.png' % thread_id       
       self.save_grid_img(thread_id, self.checked_grid, img_filename)
       print('\nTO PROCEED CLICK X AT THE DISPLAYED WINDOW', flush=True)        
       self.disp_dual_img(thread_id,val_str) 

    #------------------------------------------------------------------------------------

    def check_grid(self,checked_grid):
    
        self.checked_grid = checked_grid
        # Simulate all generations

        self.update_grid_num_itr()

        match = True
        for r in range(self.GRID_HEIGHT):
          for c in range(self.GRID_WIDTH):
            if (self.grid[r,c] != checked_grid[r,c]) :
              match=False
              break
          if not match :
            break
        
        if match :
          self.check_ok = True
          print('\n\nGREAT, Final grid match expected\n')
        else :
          self.check_ok = False        
          print('\n\nERROR, Final grid does not match expected\n')

                           
    #------------------------------------------------------------------------------------
    
    # Main function
    def animate(self):
                
        generation = 0
        running = True

        first_draw = True
        paused = False 
        
        while running :
                
            if (self.args.fftl) and (generation < self.args.itr) : 
                self.grid = self.update_grid(self.grid)
                generation += 1
                print('Done %d Generations ...' % generation, end='\r', flush=True)

            else :
            
                if first_draw :
                    pygame.init()
                    screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
                    pygame.display.set_caption("Conway's Game of Life (Pygame)")
                    clock = pygame.time.Clock()    
                    font = pygame.font.SysFont("consolas", 20)
                    first_draw = False               
                        
                clock.tick(self.FPS)
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE :
                            paused = not paused
                
                if generation==self.args.itr :
                   paused = True
                
                if not paused:
                    self.grid =self.update_grid(self.grid)
                    generation += 1
                    
                screen.fill(self.BG_COLOR)
                self.draw_generation(screen, generation, font)
                self.draw_grid(screen, self.grid)
                
                pygame.display.flip()
    
        pygame.quit()
        sys.exit()
    
    #----------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='Cgol Animate',formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('pic',  metavar='<inpat_name>', default=None, type=str, help='Input pattern name')
    ap.add_argument('-itr', metavar='<num_itr>' , type=int, default=0 , help='Number of iterations (generations)')
    ap.add_argument('-fps', metavar='<gen_per_sec>' , type=int, default=10 , help='Frames (generations) per second')     
    ap.add_argument('-wrap' , action='store_true', help='Wrap Mode')  
    ap.add_argument('-fftl' , action='store_true', help='fast forward to last')    
    
    args = ap.parse_args()

    anim = cgol_animate(args)
    
    anim.animate()
