import shutil
import subprocess
import sys
import os
from make_log import log_exceptions
from backend import mark_flag, get_hospital, mark_utr_tables

try:
    hosp = get_hospital(sys.argv[2])
    if hosp != '':
        shutil.rmtree('temp_files', ignore_errors=True)
        os.mkdir('temp_files')
        insname, fpath, mid = sys.argv[1], sys.argv[2], sys.argv[3]
        if os.path.exists('pdf_' + insname + ".py"):
            mark_flag('p', fpath)
            subprocess.run(["python", 'pdf_' + insname + ".py", fpath, mid])
            mark_utr_tables(fpath)
        else:
            mark_flag('NOFILE', fpath)
except:
    log_exceptions()
pass
