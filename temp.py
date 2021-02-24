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
    insname, fpath = "bajaj", "/home/akshay/temp/bajaj_02222021143359/5769_IN00043Q0073099INBOM.pdf"
    # mark_flag('p', fpath)
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath])
except:
    log_exceptions()
pass
