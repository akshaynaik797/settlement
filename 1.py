import subprocess

tmp = 'fhpl'
mid = 'temp_id'
filepath = '/home/akshay/temp/69576360_.pdf'
subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])