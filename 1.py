import subprocess
import os

ins = 'temp'
mid = '177fcf4b4c7f4602'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEMAAA80npqDluGRIdxtgeTfSBNAALeh3rnAAA='
filepath = '/home/akshay/temp/86952040_.pdf'

subprocess.run(["python", 'pdf_' + ins + ".py", filepath, mid])