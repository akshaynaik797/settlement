import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/7930_rptSettlementLetterIndivisual_RC-HS20-12245469_202_20210311162927821.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])