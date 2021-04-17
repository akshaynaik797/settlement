import subprocess
import os

tmp = 'big'
mid = 'temp_id'
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEMAAA80npqDluGRIdxtgeTfSBNAAKzTHxjAAA='
filepath = '/home/akshay/temp/3269_GAL_BillSummaryOtherProducts_CLMG_13_03_2021_1614791138986.pdf'

subprocess.run(["python", 'pdf_' + tmp + ".py", filepath, mid])