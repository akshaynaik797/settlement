import subprocess
import os

ins = 'Medi_Assist'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEtAAA80npqDluGRIdxtgeTfSBNAALeh6nVAAA='
filepath = '/home/akshay/temp/8789_24088023.pdf'
sett_sno = '777'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])