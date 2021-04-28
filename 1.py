import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/3903_FT104238864859.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])