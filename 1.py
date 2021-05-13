import subprocess
import os

ins = 'national'
mid = '1794acff644b527d'
filepath = '/home/akshay/temp/7441_892411028018_mediclaim.noble_gmail.com.xls'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])