import subprocess

import shutil
import subprocess
import sys
import os
from make_log import log_exceptions
from backend import mark_flag
try:
    shutil.rmtree('temp_files', ignore_errors=True)
    os.mkdir('temp_files')
    insname, fpath = "MDINDIA", "/home/akshay/temp/6366_MDI6072986_CPS_Cash Less_23_02_2021_02_01_00.pdf"
    # mark_flag('p', fpath)
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath])
except:
    log_exceptions()
pass
