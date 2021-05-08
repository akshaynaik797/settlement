import subprocess
import os

ins = 'health_india'
mid = '172cbdd2859429c6'
filepath = 'file:///home/akshay/Downloads/3381_HI-NIA-001178249_0_DV.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])