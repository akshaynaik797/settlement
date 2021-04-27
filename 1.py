import subprocess
import os

ins = 'Max_Bupa'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/7398_ClaimSettlementVoucher#645626.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])