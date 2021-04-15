import subprocess
import os

tmp = 'temp'
mid = 'temp_id'
filepath = '/home/akshay/temp/IN00043Q0343055INBOM.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])