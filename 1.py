import subprocess
import os

ins = 'newindia'
mid = '177fcf4b4c7f4602'
filepath = '/home/akshay/temp/8422_PAYMENT_DETAIL_1000002023186414691.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])