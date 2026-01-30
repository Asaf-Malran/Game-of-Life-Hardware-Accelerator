#ifndef _BIT_ARRAY_H_
#define _BIT_ARRAY_H_

typedef unsigned char byte;

typedef struct bit_array_s {
    int    rows ; // number of byte rows
    int    byte_cols ; // number of byte columns
    int    bit_cols ;// number of bit columns in the related bit array
    byte * data;    
} bit_array_t ;

//===========================================================================
// Static inline functions , required for dramatic compile optimization.
//===========================================================================

// Get the state of a cell (1 or 0)
static inline int get_cell_in_row(byte* bytes_vec, int grid_col) {
    return (bytes_vec[grid_col/8] >> (grid_col%8)) & 1;
}

//---------------------------------------------------------------------------

// Get the state of a cell (1 or 0)
static inline int vol_get_cell_in_row(volatile byte* bytes_vec, int grid_col) {
    return (bytes_vec[grid_col/8] >> (grid_col%8)) & 1;
}

//---------------------------------------------------------------------------


// Get the state of a cell (1 or 0)
static inline int get_cell(bit_array_t* bit_array, int grid_col, int grid_row) {
       
    if ((grid_col<0) || (grid_row<0) || (grid_col>=bit_array->bit_cols) || (grid_row>=bit_array->rows)) return 0;
     
    byte * row_vec = &(bit_array->data[grid_row*bit_array->byte_cols]) ;     
    return get_cell_in_row(row_vec,grid_col);
}

//---------------------------------------------------------------------------

static inline void set_cell_in_row(byte* bytes_vec, int grid_col, int state) {

    byte* byte_ptr = &(bytes_vec[grid_col/8]) ;
    byte  mask_val = 1<<(grid_col%8); 
    
    if (state) *byte_ptr |=  mask_val; // Set bit
    else       *byte_ptr &= ~mask_val; // Clear bit
}

//---------------------------------------------------------------------------

static inline void swap_cell_in_row(byte* bytes_vec, int grid_col) {

    byte* byte_ptr = &(bytes_vec[grid_col/8]) ;
    byte  mask_val = 1<<(grid_col%8); 
    
    *byte_ptr ^=  mask_val;
    // if (state) *byte_ptr |=  mask_val; // Set bit
    // else       *byte_ptr &= ~mask_val; // Clear bit
}

//---------------------------------------------------------------------------


// Set the state of a cell
static inline void set_cell(bit_array_t* bit_array, int grid_col, int grid_row, int state) {
    if ((grid_col<0) || (grid_row<0) || (grid_col>=bit_array->bit_cols) || (grid_row>=bit_array->rows)) return;
                
    byte* byte_ptr = &(bit_array->data[(grid_row*bit_array->byte_cols) + grid_col/8]) ;
    if (state)
        *byte_ptr |= (1<<(grid_col%8));  // Set bit
    else
        *byte_ptr &= ~(1<<(grid_col%8)); // Clear bit
}


//---------------------------------------------------------------------------------------------

static inline void mem_copy(byte * dst_addr, byte * src_addr, int num_bytes) {  
   int wi ; // word  index 
   for (wi=0 ; wi < num_bytes/4 ; wi++) ((unsigned int*)dst_addr)[wi] = ((unsigned int*)src_addr)[wi] ; // copy words
   for (int bi=wi*4 ; bi < num_bytes ; bi++) dst_addr[bi] = src_addr[bi] ; // copy  remaining bytes
}

//---------------------------------------------------------------------------

static inline void  mem_set(byte * dst_addr, byte set_val,  int num_bytes) {
   for (int i=0 ; i < num_bytes ; i++) dst_addr[i] = set_val ;   
 // TODO: word optimize like mem_copy   
}

//---------------------------------------------------------------------------

static inline byte * array_row_ptr(bit_array_t* bit_array_p, int byte_row_idx) {
    return &(bit_array_p->data[byte_row_idx*(bit_array_p->byte_cols)]) ;
}

//---------------------------------------------------------------------------


#endif