#include <k5_libs.h>
#include <../cgol_shared_lib/bit_array.h>   // types and static inline functions
#include <../cgol_shared_lib/cgol_shared_lib.h> // Shared among multiple cgol app versions

//---------------------------------------------------------------------------

/*  
     Method Approach:
   - Single Array Update, instead of using next_grid, we update grid in-place.
   - We process one grid row at a time, caching the previous, current, and next rows in local variables.
   - Bit-wise Operations for Memory Efficiency
   - Each cell is stored as a single bit, reducing memory usage.
   - Updates are performed using bit-wise masks.
*/

/****************************** XLR MACROS ******************************/

// NOTICE following must be compliant with the relative used address in the accelerator code, this is NOT automated.

// XBOX REGISTERS ADDRESS MACROS

enum {
     GRID_BASE_ADDR_REG_IDX,
     GRID_WIDTH_REG_IDX, 
     GRID_HEIGHT_REG_IDX,
     START_REG_IDX, 
     DONE_REG_IDX 
} ;

#define GRID_BASE_ADDR_REG ((volatile unsigned int *) (XBOX_REGS_BASE_ADDR + (4*GRID_BASE_ADDR_REG_IDX))) 
#define GRID_WIDTH_REG     ((volatile unsigned int *) (XBOX_REGS_BASE_ADDR + (4*GRID_WIDTH_REG_IDX))) 
#define GRID_HEIGHT_REG    ((volatile unsigned int *) (XBOX_REGS_BASE_ADDR + (4*GRID_HEIGHT_REG_IDX))) 
#define START_REG          ((volatile unsigned int *) (XBOX_REGS_BASE_ADDR + (4*START_REG_IDX))) 
#define DONE_REG           ((volatile unsigned int *) (XBOX_REGS_BASE_ADDR + (4*DONE_REG_IDX))) 

//---------------------------------------------------------------------------------------------

void cgol_xlr_init(cgol_conf_t* cgol_conf_p) {
            

  *GRID_BASE_ADDR_REG = XSPACE_BASE_ADDR ; ;
  *GRID_HEIGHT_REG    = cgol_conf_p->height ;
  *GRID_WIDTH_REG     = cgol_conf_p->width ;
}

//---------------------------------------------------------------------------------------------

// Compute next generation using grid_row caching

void update_grid(cgol_conf_t* cgol_conf_p) {
            
    *START_REG = 1; // Trigger Start    
    while(!*DONE_REG){
       // bm_printf("Pending DONE_REG\n") ; // Uncomment for debug
    }
}

//---------------------------------------------------------------------------------------------


int main() {
    
    cgol_conf_t cgol_conf ;

    bit_array_t  grid ;

    
    int thread_id =  bm_get_thread_id() ;
    bm_printf("\nHELLO CGOL XLR from thread:%d\n",thread_id); 

    initialize(&grid, &cgol_conf, thread_id,1); // is_xlr=1
    
    bm_printf("\nProcessing %d Generations\n",_NUM_ITR_);
    
    cgol_xlr_init(&cgol_conf);  
    
    mesure_init();        
    
    for (int i = 0; i <  _NUM_ITR_; i++) {  // Run iterations

        display_grid(i,0); // // Always call, Will display (non-blocking) only in-case defined in invocation 
        
        update_grid(&cgol_conf);
        
        mesure_itr() ; 

    }
         
    display_grid(_NUM_ITR_,1); // Always call, Will display (blocking) only in-case applied in invocation 
   
    animate_terminate() ;  // Always call, will terminate animation only in-case applied in invocation  

    report_mesure(0,1) ; // is_mt8=0 , is_xlr=1  
           
    bm_quit_app();
    
    return 0;
}

//---------------------------------------------------------------------------
