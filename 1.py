import subprocess
import os

ins = 'Medsave'
mid = '1'
filepath = '/home/akshay/temp/1482_20200905B008CH04617.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '1'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])