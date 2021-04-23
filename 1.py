import subprocess
import os

ins = 'royal'
mid = '177fbf009add6841'
filepath = '/home/akshay/Downloads/8758_CashlessClaimSettlementLetter_IH19020272CSL00.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])