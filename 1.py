import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/6650_Claim_Payment_Hospital_NEFT_3812099.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])