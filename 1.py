import subprocess
import os

ins = 'bajaj'
mid = '1794acff644b527d'
filepath = '/home/akshay/temp/5381_IN00043Q0343075INBOM.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])