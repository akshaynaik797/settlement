import subprocess
import os

ins = 'vidal'
mid = '1794acff644b527d'
filepath = 'file:///home/akshay/Downloads/8967_BLR-0320-CH-0003303.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])