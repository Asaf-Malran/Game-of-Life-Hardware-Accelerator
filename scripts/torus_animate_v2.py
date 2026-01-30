import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import os
from scipy.signal import convolve2d

#------------------------------------------------------------------------

class cgol_torus_animate :
      
    def __init__(self):
    
      self.GRID_MAX_H = 256
      self.GRID_MAX_W = 256
      self.GRID_H = None
      self.GRID_W = None
      self.grid   = None
      self.surf   = None
      self.fig    = None
      self.ax     = None
    
    #--------------------------------------------------------------------
   
    # --- Game of Life logic (toroidal) ---
    def count_neighbors(self, grid):
        return sum(np.roll(np.roll(grid, i, 0), j, 1)
                   for i in [-1, 0, 1] for j in [-1, 0, 1]
                   if not (i == 0 and j == 0))

    #-------------------------------------------------------------------- 
 
    def step(self, grid):
        #neighbors = self.count_neighbors(grid)
        #return (neighbors == 3) | ((grid == 1) & (neighbors == 2))

        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])
        
        # Count neighbors using 2D convolution

        neighbors = convolve2d(self.grid, kernel, mode='same', boundary='wrap')
        
        # Apply Conway's Game of Life rules
        birth = (self.grid == 0) & (neighbors == 3)
        survive = (self.grid == 1) & ((neighbors == 2) | (neighbors == 3))
        
        # Return the next generation
        return np.where(birth | survive, 1, 0)        



    #--------------------------------------------------------------------
    
    # --- Convert 2D grid to torus coordinates ---
    def torus_coordinates(self, grid, R=3, r=2):
        m, n = grid.shape
        theta = np.linspace(0, 2 * np.pi, m, endpoint=False)
        phi = np.linspace(0, 2 * np.pi, n, endpoint=False)
        theta, phi = np.meshgrid(theta, phi, indexing='ij')
    
        X = (R + r * np.cos(phi)) * np.cos(theta)
        Y = (R + r * np.cos(phi)) * np.sin(theta)
        Z = r * np.sin(phi)
        return X, Y, Z

    #--------------------------------------------------------------------
    
    # --- Animate Game of Life on torus ---
    def animate_game_on_torus(self, grid, frames=100, interval=200):
        self.fig = plt.figure(figsize=(8,6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.axis('off')
        self.ax.set_box_aspect([1, 1, 1])
    
        X, Y, Z = self.torus_coordinates(grid)
        facecolors = plt.cm.binary(grid.astype(float))
        self.surf = [self.ax.plot_surface(X, Y, Z, facecolors=facecolors,
                                rstride=1, cstride=1, antialiased=False)]
                                
        ani = FuncAnimation(self.fig, self.update, frames=frames, interval=interval, blit=False)
        plt.show()
                            
    #--------------------------------------------------------------------
    
    def update(self, _):

        self.grid = self.step(self.grid)
        X, Y, Z = self.torus_coordinates(self.grid)
    
        # Remove previous surface correctly
        self.surf[0].remove()
    
        # Add new surface
        facecolors = plt.cm.binary(self.grid.astype(float))
        self.surf[0] = self.ax.plot_surface(X, Y, Z, facecolors=facecolors,
                                  rstride=1, cstride=1, antialiased=False)
        return self.surf


    
    #------------------------------------------------------------------------------------
 
    def get_start_pic (self, args) :
    
       K5_SW_APPS_PATH = os.environ["K5_SW_APPS"].replace('/c/','c:/')
       pic_file = open(K5_SW_APPS_PATH + '/cgol_shared_lib/cgol_patterns/' + args.pic + '.txt','r')

       self.grid = np.zeros((self.GRID_MAX_H, self.GRID_MAX_W), dtype=int)

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
                    self.grid[row_idx][col_idx] = 1
             col_idx+=1    
             
         if row_present:
           row_idx+=1
         
       if len(line.split())>0 :
         orig_line_count+=1
                     
       width = total_elements//orig_line_count
                      
       self.GRID_H = orig_line_count
       self.GRID_W = width
       
       self.grid = self.grid[:self.GRID_H, :self.GRID_W]
                 
       pic_file.close()       

#-----------------------------------------------------------------------------------

if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='Cgol Animate',formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('pic',  metavar='<inpat_name>', default=None, type=str, help='Input pattern name')
    # ap.add_argument('-itr', metavar='<num_itr>' , type=int, default=0 , help='Number of iterations (generations)')  
    # ap.add_argument('-wrap' , action='store_true', help='Wrap Mode')  
    # ap.add_argument('-fftl' , action='store_true', help='fast forward to last')    
    args = ap.parse_args()
  
    cta = cgol_torus_animate() 
    cta.get_start_pic(args)    
    cta.animate_game_on_torus(cta.grid)
