import subprocess
import os

ins = 'temp'
mid = '177fbf009add6841'
filepath = '/home/akshay/temp/3282_MDI6143564_CPS_CashLess_09_03_2021_12_15_29.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])