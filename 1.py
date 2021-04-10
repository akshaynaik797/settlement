import subprocess
import os

tmp = 'Medsave'
mid = 'temp_id'
filepath = '/home/akshay/Downloads/4115_20201219B011CH06589.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])