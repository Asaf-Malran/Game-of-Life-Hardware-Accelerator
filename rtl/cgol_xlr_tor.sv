import xbox_def_pkg::*;


//-----------------------------------------------------------------------

module cgol_xlr_tor (

  // DO NOT TOUCH INTERFACE

  input        clk,
  input        rst_n,  
 
  // Command Status Register Interface
  input        [XBOX_NUM_REGS-1:0][31:0] host_regs,               // regs accelerator write data, reflecting logicisters content as most recently written by SW over APB
  input  logic [XBOX_NUM_REGS-1:0]       host_regs_valid_pulse,   // logic written by host (APB) (one per register)   
  output logic [XBOX_NUM_REGS-1:0][31:0] host_regs_data_out,      // regs accelerator write data,  this is what SW will read when accessing the register  
                                                                  // provided that the register specific host_regs_valid_out is asserted
  output logic [XBOX_NUM_REGS-1:0]       host_regs_valid_out,     // logic accelerator (one per register)   
  input  logic [XBOX_NUM_REGS-1:0]       host_regs_read_pulse,    // Indicate register actual read by host to allow clear on read if desired.

  mem_intf_read.client_read   mem_intf_read,
  mem_intf_write.client_write mem_intf_write 
 );
 
 //-----------------------------------------------------------------------

  // Max possible dimenssions avtual confifured dimenssions might be less.

  localparam MAX_HEIGHT = 64;  // MAX Height of cgol grid (max number of rows)
  localparam MAX_WIDTH  = 64;  // Max number cells in a cgol grid row , must be an integer multiple of 8
  localparam MAX_WIDTH_BYTES = MAX_WIDTH/8 ;
  
   
 //======================================================================================================== 

  enum {
    GRID_BASE_ADDR_REG_IDX,
    GRID_WIDTH_REG_IDX, 
    GRID_HEIGHT_REG_IDX,
    START_REG_IDX, 
    DONE_REG_IDX 
  } regs_idx;

  enum {
    IDLE,
    READ,
    CALC,
    WRITE,
    DONE
  } next_state, state;

    //======================================================================================================== |

  logic [31:0] grid_base_addr;
  logic [$clog2(MAX_WIDTH):0]  width; 
  logic [$clog2(MAX_HEIGHT):0]  height; 
  logic        start_pulse;
  logic        cgol_done;


  // set the three row (prev,curr and next)
  logic [7:0] prev_row [0:MAX_WIDTH_BYTES-1];
  logic [7:0] curr_row [0:MAX_WIDTH_BYTES-1];
  logic [7:0] next_row [0:MAX_WIDTH_BYTES-1];
  logic [7:0] new_row  [0:MAX_WIDTH_BYTES-1];
  logic [7:0] first_row [0:MAX_WIDTH_BYTES-1];


  logic [7:0] new_row_updated  [0:MAX_WIDTH_BYTES-1];
  logic [7:0] new_row_ps  [0:MAX_WIDTH_BYTES-1];

  //real size of the row
  logic [$clog2(MAX_WIDTH_BYTES):0] row_size_bytes;
  assign row_size_bytes = width[$clog2(MAX_WIDTH):3];


  //index of row 
  logic [$clog2(MAX_HEIGHT):0] row_index;
  //stop condition 
  logic is_last_row;
  assign is_last_row = (row_index == height - 1);

  logic [31:0] curr_rd_addr;
  logic [31:0] curr_wr_addr;
  logic clear_done_on_read;

  logic first_iter;
  logic is_read_last_row;
  logic row_changed;

  //======================================================================================================== |
  assign grid_base_addr = host_regs[GRID_BASE_ADDR_REG_IDX];
  assign width          = host_regs[GRID_WIDTH_REG_IDX];
  assign height         = host_regs[GRID_HEIGHT_REG_IDX];
  assign start_pulse = host_regs[START_REG_IDX] && host_regs_valid_pulse[START_REG_IDX];
  assign clear_done_on_read = host_regs_read_pulse[DONE_REG_IDX];

  //======================================================================================================== |

  // Host Regs Interface 
  logic [XBOX_NUM_REGS-1:0][31:0] host_regs_data_out_ps;


  always_comb begin
    host_regs_data_out_ps = host_regs_data_out;
    if (cgol_done)
      host_regs_data_out_ps[DONE_REG_IDX][0] = 1;
    else if (host_regs_read_pulse[DONE_REG_IDX])
      host_regs_data_out_ps[DONE_REG_IDX][0] = 0;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      host_regs_data_out <= '0;
    else
      host_regs_data_out <= host_regs_data_out_ps;
  end


  always_comb begin
    host_regs_valid_out = '0;
    host_regs_valid_out[DONE_REG_IDX] = host_regs_data_out[DONE_REG_IDX][0];
  end


  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      state <= IDLE;
    else
      state <= next_state;
  end

  //======================================================================================================== |

  // Sequential block
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      row_index    <= 0;
      curr_rd_addr <= 0;
      curr_wr_addr <= 0;
      first_iter    <= 1;
      is_read_last_row <= 0;
      prev_row      <= '{default:0};
      curr_row      <= '{default:0};
      next_row      <= '{default:0};
      new_row       <= '{default:0};
      first_row     <= '{default:0};
    end 
    else begin
      if (start_pulse && state == IDLE) begin
        row_index    <= 0;
        curr_rd_addr <= grid_base_addr;
        curr_wr_addr <= grid_base_addr;
        first_iter <= 1;
        is_read_last_row <= 0;
      end 
      else if (state == READ && mem_intf_read.mem_valid) begin
        curr_rd_addr <= curr_rd_addr + row_size_bytes;
        if (first_iter) begin
          if (!is_read_last_row) begin
            for (int i = 0; i < MAX_WIDTH_BYTES; i++) begin
              curr_row[i] <= mem_intf_read.mem_data[i];
            end

            first_iter <= 1;
            curr_rd_addr <= grid_base_addr + (height - 1) * row_size_bytes ;
            is_read_last_row <= 1;
          end
          else begin
          // copy the last row to prev row
            for (int i = 0; i < MAX_WIDTH_BYTES; i++) begin
              prev_row[i] <= mem_intf_read.mem_data[i];
            end
            curr_rd_addr <= grid_base_addr + row_size_bytes;
            first_iter <= 0;
            first_row <= curr_row;
          end
        end
        else begin
          if ((row_index +1) < height) begin
            for (int i = 0; i < MAX_WIDTH_BYTES; i++) begin
              next_row[i] <= mem_intf_read.mem_data[i];
            end
            curr_rd_addr <= curr_rd_addr + row_size_bytes;
          end else begin 
            next_row      <= first_row;
            curr_rd_addr <= curr_rd_addr + row_size_bytes;
          end
        end
      end 
      else if (state == CALC) begin
        new_row <= new_row_ps;
        if (!row_changed) begin
          curr_wr_addr <= curr_wr_addr + row_size_bytes;
          row_index <= row_index  + {{($clog2(MAX_HEIGHT)){1'b0}}, 1'b1};
          prev_row <= curr_row;
          curr_row <= next_row;
          first_iter <= 1'b0;
        end
      end
      else if (state == WRITE && mem_intf_write.mem_ack) begin 
        curr_wr_addr <= curr_wr_addr + row_size_bytes;
        row_index <= row_index  + {{($clog2(MAX_HEIGHT)){1'b0}}, 1'b1};
        prev_row <= curr_row;
        curr_row <= next_row;
        first_iter <= 1'b0;
      end
    end
  end

  assign new_row_ps = new_row_updated;


  //======================================================================================================== |

  //state machine 
  always_comb begin

    next_state = state;

    mem_intf_read.mem_req  = 0;
    mem_intf_write.mem_req = 0;

    mem_intf_read.mem_start_addr  = curr_rd_addr;
    mem_intf_write.mem_start_addr = curr_wr_addr;

    mem_intf_read.mem_size_bytes  = row_size_bytes;
    mem_intf_write.mem_size_bytes = row_size_bytes;

    mem_intf_write.mem_data = 0;
    for (int i = 0; i < MAX_WIDTH_BYTES; i++) begin
        mem_intf_write.mem_data[i] = new_row[i];
    end

    cgol_done = 0;

    new_row_updated = '{default:0};
    row_changed = 0;
    case(state)

      IDLE: begin
        //$display(">>> STATE = IDLE, start_pulse = %b", start_pulse);
        //$display("[IDLE] width = %0d, height = %0d, base_addr = %h", width, height, grid_base_addr);
        if (start_pulse) begin
          //$display(">>> Transitioning: IDLE --> READ");
          next_state = READ;
        end else begin
          //$display(">>> Staying in IDLE");
        end
      end

      READ: begin
        //$display(">>> STATE = READ, mem_valid = %b, first_iter = %b", mem_intf_read.mem_valid, first_iter);
        //$display("[READ] curr_rd_addr = %h", curr_rd_addr);
        mem_intf_read.mem_req = 1; 
        if (mem_intf_read.mem_valid) begin
          mem_intf_read.mem_req = 0; 
          next_state = first_iter ? READ : CALC;
        end    
      end

      CALC: begin : calc_logic
        for (int col_bit = 0; col_bit < MAX_WIDTH; col_bit++) begin
          int neighbors;
          int alive;
          int bit_num;
          int byte_num;
          int left_bit;
          int right_bit;
          int lb_byte;
          int lb_bit;
          int rb_byte;
          int rb_bit;
          neighbors = 0;
          if (col_bit < width) begin
            byte_num = col_bit >> 3;
            bit_num  = col_bit & 3'b111;
            alive = (curr_row[byte_num] >> bit_num) & 1;

            left_bit = (col_bit == 0) ? width - 1 : col_bit - 1;
            right_bit = (col_bit == width - 1) ? 0 : col_bit + 1;

            rb_byte = right_bit >> 3;
            rb_bit  = right_bit & 3'b111;

            lb_byte = left_bit >> 3;
            lb_bit  = left_bit & 3'b111;

            neighbors = 
                  ((prev_row[lb_byte]  >> $unsigned(lb_bit)) & 1) +
                  ((prev_row[byte_num] >> bit_num) & 1) +
                  ((prev_row[rb_byte]  >> $unsigned(rb_bit)) & 1) +

                  ((curr_row[lb_byte]  >> $unsigned(lb_bit)) & 1) +
                  ((curr_row[rb_byte]  >> $unsigned(rb_bit)) & 1) +

                  ((next_row[lb_byte]  >> $unsigned(lb_bit)) & 1) +
                  ((next_row[byte_num] >> bit_num) & 1) +
                  ((next_row[rb_byte]  >> $unsigned(rb_bit)) & 1);
                 
            if ((!alive && neighbors == 3) || (alive && (neighbors == 2 || neighbors == 3)))
              new_row_updated[byte_num][bit_num] = 1;
            else
              new_row_updated[byte_num][bit_num] = 0;

            // $display("line: %0d col: %0d alive: %0d neighbors: %0d", row_index, col_bit, alive, neighbors);
          end         
          else begin
           break;
          end;
        end    
        
        for (int i = 0; i < MAX_WIDTH_BYTES; i++) begin
          if (new_row_updated[i] !== curr_row[i]) begin
            row_changed = 1;
            break;
          end
        end
        if (row_changed) begin
          next_state = WRITE;
        end
        else begin
          next_state = is_last_row ? DONE : READ;
        end
      end

      WRITE: begin
        //$display(">>> STATE = WRITE, mem_ack = %b", mem_intf_write.mem_ack);
        //$display("[WRITE] row_index = %0d, is_last_row = %b", row_index, is_last_row);
        mem_intf_write.mem_req = 1;
        if (mem_intf_write.mem_ack) begin
          next_state = is_last_row ? DONE : READ;
        end
      end

      DONE: begin
        //$display(">>> STATE = DONE, clear_done_on_read = %b", clear_done_on_read);
        cgol_done = 1;
        if (clear_done_on_read) next_state = IDLE;
      end
    endcase
  end

endmodule