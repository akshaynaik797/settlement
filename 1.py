import subprocess
import os

ins = 'Paramount'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEtAAA80npqDluGRIdxtgeTfSBNAALeh6nVAAA='
filepath = '/home/akshay/temp/17057712_.pdf'
sett_sno = '777'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])