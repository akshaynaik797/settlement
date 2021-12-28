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
    insname, fpath = "fgh", "/home/ubuntu/index/index/14_12_2021/noble/letters/fgh_10062021190521/6903_Claim_Payment_Hospital_NEFT_4809822.pdf"
    subprocess.run(["python", 'pdf_' + insname + ".py", fpath, '1780d0af0945709e'])
except:
    log_exceptions()
pass
