#include <k5_libs.h>
#include <bit_array.h>   // types and static inline functions
#include <cgol_shared_lib.h> // Shared among multiple cgol app versions

//---------------------------------------------------------------------------

void display_grid_terminal(int itr) {
         
    char pyshell_exec_str[80] ; 
    bm_sprintf(pyshell_exec_str,"pg.display_grid(%d)",itr) ;
    bm_pyshell_exec (pyshell_exec_str); 
    char done = (int)k5_get_char() ; // Should block till print is done 
}

//---------------------------------------------------------------------------

void display_grid_pyplot(int itr, char block) {
              
    char pyshell_exec_str[80] ; 

    char * block_str  = block  ? "True" : "False" ;
    if (block) bm_printf("\nTO PROCEED CLICK X AT THE DISPLAYED ANIMATION WINDOW\n");   
    bm_sprintf(pyshell_exec_str,"disp.display_grid(itr=%d,block=%s)",itr, block_str);
    bm_pyshell_exec (pyshell_exec_str);
}

//---------------------------------------------------------------------------

void display_grid_pygame(int itr, char block, char * ll_val_str) {
              
    char pyshell_exec_str[80] ; 

    char * block_str    = block  ? "True" : "False" ; 
    
    #if defined(ANIMATE)    
      char * animate_str  = "True" ; 
    #else
      char * animate_str  = "False" ;         
    #endif
    
    #if (!defined(ANIMATE)) || (ANIMATE==PYGAME)
      bm_sprintf(pyshell_exec_str,"disp.display_grid(itr=%d,block=%s,animate=%s,val_str=\'%s\')",itr, block_str,animate_str,ll_val_str);
    #else
      bm_sprintf(pyshell_exec_str,"disp.display_grid(itr=%d,block=%s,%s)",itr, block_str);  
    #endif
    bm_pyshell_exec (pyshell_exec_str);
}

//---------------------------------------------------------------------------


void display_grid(int itr, char post_last) {
    
    #if !defined(ANIMATE) 
      char * ll_val_str ;    
      if (post_last) {
         ll_val_str = report_mesure_elapse() ;          
         display_grid_pygame(itr,1,ll_val_str) ;
      }
    #elif ANIMATE==TERMINAL 
      display_grid_terminal(itr) ;
    #elif ANIMATE==PYPLOT
      display_grid_pyplot(itr,post_last);
    #elif ANIMATE==PYGAME
      display_grid_pygame(itr,post_last,(char *)0);  
    #endif               
}

//---------------------------------------------------------------------------

void animate_terminate() {
    
    #if ANIMATE==TERMINAL // Only Termoinal display mode require termination call
    bm_pyshell_exec ("pg.animate_terminate()");
    #endif
}

//----------------------------------------------------------------------------

void load_cgol_conf(int cgol_conf_f, cgol_conf_t *cgol_conf_p) { 
                        
 bm_printf("\nLoading CGOL Configuration file\n\n");
 bm_fscans(cgol_conf_f, cgol_conf_p->test_name) ;  

 char val_str[10] ;
 bm_fscans(cgol_conf_f, val_str) ;
 cgol_conf_p->height = dec_str_to_int(val_str) ;
 bm_fscans(cgol_conf_f, val_str) ;
 cgol_conf_p->width = dec_str_to_int(val_str) ; 
 cgol_conf_p->act_bytes_per_row = (cgol_conf_p->width%8)==0 ? cgol_conf_p->width/8 : (cgol_conf_p->width/8)+1 ; 
 
 bm_printf("test_name: %s , height=%d , width=%d\n",cgol_conf_p->test_name, cgol_conf_p->height, cgol_conf_p->width);
}
//-----------------------------------------------------------------------------------------------

void initialize(bit_array_t* grid_p, cgol_conf_t* cgol_conf_p, int thread_id, char is_xlr) {
    
    #ifndef _GP_VAL_
    #define _GP_VAL_ cgol_16x16_p1 // Default
    #endif

    //System call for generate loadable hex file.
    char cmd_str[80];
    char pat_name[80];  
    bm_sprintf(pat_name,"%s",EXPAND_AND_STRINGIFY(_GP_VAL_));
    bm_sprintf(cmd_str,"python3 app_src_dir/../cgol_shared_lib/cgol_p2h.py %s",pat_name);   
    bm_sys_call(cmd_str);

    int cgol_conf_f = bm_fopen_r("cgol_conf.txt") ;
    load_cgol_conf(cgol_conf_f, cgol_conf_p); // Load Configuration info
                  
    int byte_size = cgol_conf_p->height * cgol_conf_p->act_bytes_per_row  ;
 
    grid_p->rows = cgol_conf_p->height ;
    grid_p->byte_cols = cgol_conf_p->act_bytes_per_row ; 
    grid_p->bit_cols = cgol_conf_p->width ;     
    grid_p->data = (byte *)XSPACE_BASE_ADDR ;
    
    int pic_hex_f = bm_fopen_r("cgol_hex_in.txt") ; // Generated test source data     

    bm_printf("Loading input test data: to xmem address 0x%08x , byte length : %d\n", grid_p->data, byte_size);                 
    bm_start_soc_load_hex_file (pic_hex_f, byte_size, (unsigned char*)(grid_p->data)) ; 
    
    // Polling till transfer completed (SW may also do other stuff mean while)
    int num_loaded = 0 ;
    while (num_loaded==0) num_loaded = bm_check_soc_load_hex_file () ; // num_loaded!=0 indicates completion.
    
    bm_fclose(pic_hex_f);  
    bm_fclose(cgol_conf_f);    
    bm_printf("Loaded %d bytes\n",num_loaded) ;
    
    char class_str[80] ; 
    

    #if ANIMATE==TERMINAL // Default display for last generation
    bm_sprintf(class_str,"cgol_terminal_animate(%d,%d,0x%08x,%d, self.k5s)",grid_p->rows,grid_p->bit_cols, grid_p->data, thread_id);
    //                                                                rows,        cols,                   grid_soc_addr,thread_id     
    //                       path_str       module_name   class_str, obj_name
    bm_pyshell_get_class_obj("app_src_dir/../cgol_shared_lib","cgol_terminal_animate",class_str, "pg") ;   
    #endif

    
    #if ANIMATE==PYPLOT 
    bm_sprintf(class_str,"cgol_pyplot_animate(%d,%d,0x%08x,self.k5s)",grid_p->rows,grid_p->bit_cols, grid_p->data);    
    //                       path_str       module_name   class_str, obj_name,          grid_soc_addr
    bm_pyshell_get_class_obj("app_src_dir/../cgol_shared_lib","cgol_pyplot_animate",class_str, "disp") ;   
        
    #elif ANIMATE==PYGAME || !defined(ANIMATE) 
    bm_sprintf(class_str,"cgol_pygame_animate(%d,%d,0x%08x,self.k5s,%d)",grid_p->rows,grid_p->bit_cols, grid_p->data, bm_get_thread_id());  
    //bm_sprintf(class_str,"cgol_pygame_animate(%d,%d,0x%08x,self.k5s)",grid_p->rows,grid_p->bit_cols, grid_p->data);    
    //                       path_str       module_name   class_str, obj_name,          grid_soc_addr
    bm_pyshell_get_class_obj("app_src_dir/../cgol_shared_lib","cgol_pygame_animate",class_str, "disp") ;   
        
    // Provide pattern name   
    bm_sprintf(cmd_str,"disp.set_pat_name(\'%s\')",pat_name);
    //bm_printf("DBG cmd_str = %s\n" , cmd_str);
    bm_pyshell_exec (cmd_str);        
                
    #endif  
}

//==========================================================
// Performance Measurement


#ifdef MESURE
static int start_cycle,end_cycle ;     // For performance checking.  
static long long int ll_acc_diff;      // Need to accumulate in case exceeding 32 bits
#endif

void mesure_init() {
    #ifdef MESURE          
    ll_acc_diff = 0 ;                    // Need to accumulate in case exceeding 32 bits
    ENABLE_CYCLE_COUNT ;                 // Enable the cycle counter
    RESET_CYCLE_COUNT  ;                 // Reset counter to ensure 32 bit counter does not wrap in-between start and end.   
    GET_CYCLE_COUNT_START(start_cycle) ; // Capture the cycle count before the operation. 
    #endif    
}

//---------------------------------------------------------

void mesure_itr() {
  #ifdef MESURE     
  GET_CYCLE_COUNT_END(end_cycle);           // Capture after iteration.
  unsigned int uint_cyc_diff = end_cycle-start_cycle ; 
  ll_acc_diff += (long long int)(uint_cyc_diff); // Accumulate across iterations
  RESET_CYCLE_COUNT  ;                           // Avoid 32 bit wrap around
  GET_CYCLE_COUNT_START(start_cycle) ;           // Capture the cycle count before the operation.

  // 7segment DISPLAY - TODO check impact on measure


  #ifdef DISP7S
  unsigned int cyc_per_sec = 50000000 ; // Per 50 MHz
  unsigned int cyc_per_10ms = cyc_per_sec/100 ;  

  static unsigned int num_10ms = 0 ;  
  static unsigned int disp7s_cyc_diff = 0 ;
  
  disp7s_cyc_diff += uint_cyc_diff ;
  
  if (disp7s_cyc_diff >= cyc_per_10ms) {  
  
    num_10ms += disp7s_cyc_diff/cyc_per_10ms ;
    disp7s_cyc_diff = disp7s_cyc_diff % cyc_per_10ms ;
    display_6dig_7seg_sec_p2f(num_10ms) ;  
  }
  #endif // DISP7S
  
  #endif // MESURE 
}

//---------------------------------------------------------

void report_mesure(char is_mt8 , char is_xlr) {
       
  #ifdef MESURE   
  // TODO: Notice long long seems to have division issues, need to further debug.  
  // Time stamping report  
  char ll_val_str[40] ;// Long-Long-Int to string (long long not supported by bm_printf)

  if (is_xlr || is_mt8) {
      
    bm_format_with_commas(ll_acc_diff, ll_val_str);    
    bm_printf("\n\nMeasured %s K5 cycles for %d generations\n",ll_val_str,_NUM_ITR_); // Report

    #if (_NUM_ITR_ != 0) 
      int cyc_per_itr = (int)(ll_acc_diff)/_NUM_ITR_ ;
      bm_format_with_commas(cyc_per_itr, ll_val_str);
      bm_printf("%s K5 cycles per generations \n\n",ll_val_str);
    #endif
                        
  } else {
      
    long long int ll_val = ll_acc_diff/8 ;
    bm_format_with_commas(ll_val, ll_val_str);    
    bm_printf("\n\nMeasured %s K5 single-thread cycles for %d generations\n",ll_val_str,_NUM_ITR_); // Report

    #if (_NUM_ITR_ != 0) 
      int cyc_per_itr = (int)(ll_val)/_NUM_ITR_ ;
      bm_format_with_commas(cyc_per_itr, ll_val_str);
      bm_printf("%s K5 single-thread cycles per generations \n\n",ll_val_str);
    #endif
  }
  
  #endif
}

//----------------------------------------------------------

static char ll_val_str[20] ;// Long-Long-Int to string (long long not supported by bm_printf)
char * report_mesure_elapse() { 
       
  #ifdef MESURE   
         
    bm_format_with_commas(ll_acc_diff, ll_val_str);      
    char pyshell_exec_str[80] ; 
    bm_sprintf(pyshell_exec_str,"disp.report_mesure_elapse(\'%s\',%d)",ll_val_str,_NUM_ITR_) ; 
    bm_pyshell_exec (pyshell_exec_str);
   return ll_val_str ;
  #else
   return "0" ;  
  #endif
                    
}


//=========================================================