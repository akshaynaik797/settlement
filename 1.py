import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/6022_Settlement.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])