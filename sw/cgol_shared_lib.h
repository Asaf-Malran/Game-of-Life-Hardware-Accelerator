#ifndef _CGOL_SHARED_LIB_H_
#define _CGOL_SHARED_LIB_H_

// Configuration Structure

typedef struct cgol_conf_s {
    char test_name[100] ;
    int height;
    int width;   
    int act_bytes_per_row; // actual bytes per row  
} cgol_conf_t;

//---------------------------------------------------------------------------------------------

#define MAX_WIDTH  256  // Max number of cells in a grid_row
#define MAX_HEIGHT 256  // Max number of rows
#define MAX_BYTES_PER_ROW (((MAX_WIDTH%8)==0)?(MAX_WIDTH/8):((MAX_WIDTH/8)+1))  // Number of bytes per grid_row (rounded up)

//==============================================================================

void load_cgol_conf(int cgol_conf_f, cgol_conf_t *cgol_conf_p);

void initialize(bit_array_t* grid_p, cgol_conf_t* cgol_conf_p, int thread_id, char is_xlr) ;

void display_grid(int itr, char post_last) ;
 
void animate_terminate() ; 
 
void load_cgol_conf(int cgol_conf_f, cgol_conf_t *cgol_conf_p);

//----------------------------------------------------------------------------

// Animate types used optionally in invocation
// Notice non-assigned defined ANIMATE macro naturally defaults to 1 which is TERMINAL
#define TERMINAL   1
#define PYPLOT     2
#define PYGAME     3 

//----------------------------------------------------------------------------

#ifndef _NUM_ITR_ 
 #define _NUM_ITR_ 1
#endif

//----------------------------------------------------------------------------

#if !defined(ANIMATE) 
#define MESURE
#endif

void mesure_init(); 
void mesure_itr(); 
void report_mesure(char is_mt8 , char is_xlr) ;
char * report_mesure_elapse() ;

//---------------------------------------------------------------------------

#endif // #ifndef _CGOL_SHARED_LIB_H_