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
    insname, fpath = "Raksha", "/home/akshay/temp/3944_90192021625239.pdf"
    # mark_flag('p', fpath)
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath, 'mail_id'])
except:
    log_exceptions()
pass
