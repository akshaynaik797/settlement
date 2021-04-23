import subprocess
import os

ins = 'national'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/2622_892411028018_mediclaim.noble_gmail.com.xls'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])