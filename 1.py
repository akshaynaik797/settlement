import subprocess
import os

tmp = 'icici_lombard'
mid = 'temp_id'
filepath = '/home/akshay/Downloads/91654494_.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])