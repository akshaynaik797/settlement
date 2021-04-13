import subprocess
import os

tmp = 'religare'
mid = 'temp_id'
filepath = '/home/akshay/Downloads/1078_Settlement.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])