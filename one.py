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
    insname, fpath = "fhpl", "/home/akshay/temp/66878081_.pdf"
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath, 'mail_id'])
    insname, fpath = "fhpl", "/home/akshay/temp/74967265_.pdf"
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath, 'mail_id'])
except:
    log_exceptions()
pass
