import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/58322751_.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])