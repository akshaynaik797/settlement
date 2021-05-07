import subprocess
import os

ins = 'health_heritage'
mid = '172cbdd2859429c6'
filepath = 'file:///home/akshay/Downloads/40704421_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])