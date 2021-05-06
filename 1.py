import subprocess
import os

ins = 'Raksha'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEtAAA80npqDluGRIdxtgeTfSBNAALeh6nVAAA='
filepath = 'file:///home/akshay/Downloads/24863392_.pdf'
# filepath = 'file:///home/akshay/Downloads/64976195_.pdf'
filepath = filepath.replace('file://', '')
sett_sno = '777'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])