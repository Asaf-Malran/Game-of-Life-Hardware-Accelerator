# Partly working ...
import sys
from colorama import init,deinit,Fore, Cursor        
init()
sys.stderr.write("\x1b[2J\x1b[H")
deinit()
