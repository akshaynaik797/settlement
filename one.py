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
    insname, fpath = "Medi_Assist", "/home/ubuntu/index/index/13_03_2021/noble/letters/Medi_Assist_03132021155259/9517_23960887.pdf"
    # mark_flag('p', fpath)
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath])
except:
    log_exceptions()
pass
