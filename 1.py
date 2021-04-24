import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/Downloads/83200912_.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])