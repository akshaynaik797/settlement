import subprocess
import os

ins = 'Paramount'
mid = '1794acff644b527d'
filepath = '/home/akshay/temp/87476394_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])