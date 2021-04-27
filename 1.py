import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/3929_20210328B008CH18474.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])