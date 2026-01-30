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

//---------------------------------------------------------------------------


void calc_new_row(byte* new_row,                    // Pointer to new_row vector to be calculated. 
                  byte* curr_row,                   // Pointer to current row in the sliding window.
                  bit_array_t* triple_rows_arr_p,   // Pointer to entire sliding window triple rows.
                  int grid_row,                     // Index of current row in grid.
                  cgol_conf_t* cgol_conf_p          // Configuration info.
                 ) {
   
    // Default the new row to current row.
    mem_copy(new_row, curr_row, cgol_conf_p->act_bytes_per_row);

    // Iterate over all columns in sliding window to calculate new current row.
    for (int grid_bit_col = 0; grid_bit_col < cgol_conf_p->width; grid_bit_col++) {
        int alive = get_cell_in_row(curr_row, grid_bit_col); // Get current cell at bit granularity
        int neighbors = 0; // Initial count of live neighbors

        // Sum the neighbors using cached rows
        // check borders for defining left and right neighbors offset index
        int left_ofst  = (grid_bit_col==0)  ? 0 : -1 ;
        int right_ofst = (grid_bit_col==(cgol_conf_p->width-1)) ? 0 :  1 ;
        
        // scan the 3x3 sub-window (or 3x2 on borders) for current counting current cell live neighbors
        for (int dx = left_ofst ; dx <= right_ofst; dx++) { // iterate 2 or 3 columns
            for (int i=0;i<3;i++) // iterate 3 rows
              neighbors += get_cell(triple_rows_arr_p, grid_bit_col+dx, i); // count neighbors
        }
                   
        neighbors -= alive; // Deduct the evaluated cell itself
        
        // Apply game rules, since default is the previous, we check if swap from dead/live status is needed       
        char state_swap = (!alive && neighbors==3) || (alive && ((neighbors<2) || (neighbors>=4)));
        if (state_swap) swap_cell_in_row(new_row, grid_bit_col); // Swap state if needed
        
    }
}

//---------------------------------------------------------------------------

// Compute next generation using grid_row caching
void update_grid(bit_array_t* grid_p, cgol_conf_t* cgol_conf_p) {
         
    byte triple_rows_arr_data [3*MAX_BYTES_PER_ROW] ; // A sliding window of 3 rows of grid
    
    bit_array_t triple_rows_arr ; // We use the bit_array_t structure to specify the sliding window

    triple_rows_arr.rows = 3 ;                       // 3 rows
    triple_rows_arr.byte_cols = grid_p->byte_cols ;  // Same number of columns as in the main grid
    triple_rows_arr.data = triple_rows_arr_data ;    // pointer to above allocated array

    // For efficient sliding window we access the sliding window rows indirectly by a pointer to its row data.    
    byte* prev_row = array_row_ptr(&triple_rows_arr, 0); // prev   initially pointing to window row 0
    byte* curr_row = array_row_ptr(&triple_rows_arr, 1); // curent initially pointing to window row 1
    byte* next_row = array_row_ptr(&triple_rows_arr, 2); // next   initially pointing to window row 2
    
    mem_set((byte*)prev_row, 0, grid_p->byte_cols);                 // Set all elements in initial prev to zero
    mem_copy(curr_row, array_row_ptr(grid_p,0), grid_p->byte_cols); // Copy main grid row 0 to window current row
    mem_copy(next_row, array_row_ptr(grid_p,1), grid_p->byte_cols); // Copy main grid row 1 to window next row

    // Iterate over all rows in main grid
    for (int grid_row=0 ; grid_row < cgol_conf_p->height; grid_row++) {
        
        byte new_row[MAX_BYTES_PER_ROW]; // Will capture the new calculated cells of current row. 

        calc_new_row(new_row, curr_row, &triple_rows_arr, grid_row, cgol_conf_p) ;  // Calculate Current row (defined above)
 
        // Copy new grid_row to grid
        mem_copy(array_row_ptr(grid_p,grid_row), new_row, grid_p->byte_cols);

        if ((grid_row+1)<cgol_conf_p->height) { // Prepare next iteration
          // scroll grid_row pointers within window (avoid copy)
          byte* save_prev_row = prev_row ; // save for scroll, needed after update 
          prev_row = curr_row;        
          curr_row = next_row;        
          next_row = save_prev_row;
        
          if ((grid_row+2) < cgol_conf_p->height) 
             // next is not last row, copy from grid to window
             mem_copy(next_row, array_row_ptr(grid_p,grid_row+2), grid_p->byte_cols);
          else 
            // next is last row case, set to zero in window
             mem_set((byte*)next_row, 0, cgol_conf_p->act_bytes_per_row);
        }
    }
}

//---------------------------------------------------------------------------

int main() {

    cgol_conf_t cgol_conf ; // general configuration structure
    
    bit_array_t  grid ;  // grid descriptor defined in cgol_shared_lib/bit_array.h

    int thread_id =  bm_get_thread_id() ; // Just for printing thread ID , currently only thread 0 (t0) defined

    bm_printf("HELLO CGOL from thread:%d\n",thread_id); 
    
    initialize(&grid, &cgol_conf, 0,0); // loads initial pattern to grid and update grid and cgol_conf structures
            
    bm_printf("\nProcessing %d Generations\n",_NUM_ITR_);  
    
    mesure_init();   // Initialize measurements 
        
    for (int i = 0; i <  _NUM_ITR_; i++) {  // Run iterations
  
        display_grid(i,0); // // Always call, Will display (non-blocking) only in-case defined in invocation 

        update_grid(&grid, &cgol_conf); // Update grid per generation

        mesure_itr() ; // Measure  performance , will measure only in non-animated mod  
    }
       
    display_grid(_NUM_ITR_,1); // Always call, Will display (blocking) only in-case applied in invocation 

    animate_terminate() ;  // Always call, will terminate animation only in-case applied in invocation  

    report_mesure(0,0) ; // report measurements , is_mt8=0 , is_xlr=0  
                  
    bm_quit_app();
    return 0;
}

//---------------------------------------------------------------------------
