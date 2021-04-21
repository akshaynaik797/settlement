import subprocess
import os

ins = 'city'
mid = '177f798f24e24b34'
filepath = '/home/akshay/temp/91666107_.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])