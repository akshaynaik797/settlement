import subprocess
import os

ins = 'icici_lombard'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEtAAA80npqDluGRIdxtgeTfSBNAALeh6nVAAA='
filepath = 'file:///home/akshay/Downloads/12786147_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '777'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])