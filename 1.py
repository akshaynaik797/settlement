import subprocess
import os

ins = 'Medsave'
mid = '1'
filepath = '/home/akshay/temp/6224_20200309B008CH10232.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '1'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])