import subprocess
import os

ins = 'newindia'
mid = 'as='
filepath = '/home/akshay/temp/6359_PAYMENT_DETAIL_1000002122046680264.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])