import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/5936_BLR-0321-CH-0001010.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])