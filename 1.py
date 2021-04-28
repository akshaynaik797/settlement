import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/3103_246784_ClaimSettelmentCashlessLetter.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])