import subprocess
import os

ins = 'health_heritage'
mid = '17260d504508d4c2'
filepath = '/home/akshay/temp/43565900_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3842'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])