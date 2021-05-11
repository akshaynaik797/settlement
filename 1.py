import subprocess
import os

ins = 'MDINDIA'
mid = '177fbb57d153d200'
filepath = '/home/akshay/temp/4078_Payment_Rec_(150023291)_Report_Mar_2021.xls'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])