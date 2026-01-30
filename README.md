# Game of Life Hardware Accelerator

## Overview
This project implements a high-performance Hardware/Software Co-design for Conway's Game of Life simulation on an Intel FPGA. The system leverages massive parallelism in hardware to verify cellular automaton rules, achieving significant acceleration compared to standard software implementations.

## Key Features
* **Performance:** Achieves up to x6000 speedup over software-only implementations.
* **Architecture:** Custom SystemVerilog accelerator core with Torus topology for seamless boundary handling.
* **HW/SW Co-Design:**
    * **Hardware (RTL):** Custom accelerator and memory interfaces.
    * **Software (C):** Driver layer for configuration, control, and host communication.
    * **Visualization (Python):** Real-time pattern generation and verification scripts.
* **Verification:** Includes a suite of test patterns and automated checking environments.

## Repository Structure

* **rtl/**: SystemVerilog source code for the accelerator core, memory interfaces (xmemcpy), and Torus logic.
* **sw/**: C drivers and host application code for interfacing with the hardware.
* **scripts/**: Python scripts for simulation visualization (PyGame), animation, and data processing.
* **quartus_prj/**: Intel Quartus Prime project files (.qpf, .qsf) and pin assignments.
* **patterns/**: Library of initial configuration files (e.g., gliders, spaceships) for system testing.

## System Description
The host CPU offloads the compute-intensive grid calculation to the hardware accelerator.
1.  **Host:** Loads the initial pattern from the `patterns/` directory and configures the accelerator via the C driver layer located in `sw/`.
2.  **Accelerator:** Computes the next generation in parallel using custom logic cells defined in `rtl/`.
3.  **Display:** The results are read back and visualized using the Python interface in `scripts/`.

## Prerequisites
* Intel Quartus Prime (for FPGA synthesis and fitting).
* GCC / Nios II software tools (for compiling the C host code).
* Python 3.x (for running the visualization scripts).

## License
This project is open-source and available under the MIT License.
