import subprocess
import os

tmp = 'royal'
mid = 'temp_id'
filepath = '/home/akshay/temp/7930_CashlessClaimSettlementLetter_IH19018731CSL00.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])