import subprocess
import os

ins = 'city'
mid = '1794acff644b527d'
filepath = '/home/akshay/temp/35046471_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])