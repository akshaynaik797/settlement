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
    insname, fpath = "Paramount", "/home/akshay/temp/85480187_.pdf"
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath, '1780d0af0945709e'])
except:
    log_exceptions()
pass
