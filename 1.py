import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/6786_GAL_BillSummaryOtherProducts_CLMG_2021_110000_0643168_1615267200776.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])