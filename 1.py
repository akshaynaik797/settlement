import subprocess
import os

ins = 'hdfcbank'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/FT010220724013.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])