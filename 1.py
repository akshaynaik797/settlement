import subprocess
import os

ins = 'Raksha'
mid = '1799f050168ee154'
filepath = '/home/akshay/temp/7169_9022122038283.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '12674'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])