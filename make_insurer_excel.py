import shutil
import subprocess
import sys
import os
from make_log import log_exceptions
from backend import get_hospital, mark_utr_tables

try:
    hosp = get_hospital(sys.argv[2])
    if hosp != '':
        shutil.rmtree('temp_files', ignore_errors=True)
        os.mkdir('temp_files')
        insname, fpath, mid, sno = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
        subprocess.run(["python", 'pdf_' + insname + ".py", fpath, mid, sno])
        mark_utr_tables(fpath)
except:
    log_exceptions()
pass
