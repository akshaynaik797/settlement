import subprocess
import os

ins = 'Good_health'
mid = '172cbdd2859429c6'
filepath = '/home/akshay/temp/5754_940262_CashLess_Claim_Settlement_Letter.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '3574'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])