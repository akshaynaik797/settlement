from pathlib import Path
from shutil import copyfile
import os
import openpyxl

wb = openpyxl.open('master.xlsx')
worksheet = wb.active
x1 = worksheet.cell(row=2, column=5).value
x2 = worksheet.cell(row=2, column=4).value
wb.close()
b = '/home/akshay/temp/19429253_.pdf'
dst = "../index/Attachments/"
Path(dst).mkdir(parents=True, exist_ok=True)
copyfile(f_src, f_dst)