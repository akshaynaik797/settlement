import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/98455637_.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])