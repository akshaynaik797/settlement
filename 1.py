import subprocess
import os

ins = 'bajaj'
mid = '1794acff644b527d'
filepath = 'file:///home/akshay/Downloads/7924_IN00043Q9124544INBOM.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])