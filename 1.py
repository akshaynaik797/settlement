import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/8042_114043AccountReport(Settle_Letter)_HELANKORABANDI_114043_0.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])