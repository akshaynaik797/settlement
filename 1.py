import subprocess
import os

ins = 'Ericson'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEtAAA80npqDluGRIdxtgeTfSBNAALeh6nVAAA='
filepath = '/home/akshay/Downloads/3890_107004AccountReport(Settle_Letter)_HELANKORABANDI_107004_0.pdf'
sett_sno = '777'
subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid, sett_sno])