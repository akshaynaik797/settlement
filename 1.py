import subprocess
import os

ins = 'MDINDIA'
mid = '1794acff644b527d'
filepath = '/home/akshay/temp/2525_MDI6203679_CPS_CashLess_16_04_2021_04_54_44.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])