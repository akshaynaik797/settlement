import shutil
import subprocess
import sys
import os
from make_log import log_exceptions
from backend import mark_flag, get_hospital

try:
    hosp = get_hospital(sys.argv[2])
    if hosp != '':
        shutil.rmtree('temp_files', ignore_errors=True)
        os.mkdir('temp_files')
        insname, fpath = sys.argv[1], sys.argv[2]
        if os.path.exists('pdf_' + insname + ".py"):
            mark_flag('p', fpath)
            subprocess.run(["python", 'pdf_' + insname + ".py", fpath])
        else:
            mark_flag('NOFILE', fpath)
except:
    log_exceptions()
pass
