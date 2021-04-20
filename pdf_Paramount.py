import os
import subprocess
import re
import openpyxl
import sys
import camelot
import pdftotext
import xlrd
from make_log import log_exceptions
from backend import mark_flag
from movemaster import move_master_to_master_insurer

try:
    pdfpath = sys.argv[1]
    onlyfiles = [os.path.split(pdfpath)[1]]
    mypath = os.path.dirname(pdfpath)+'/'

    hosp_name = ''

    with open(pdfpath, "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('temp_files/output.txt', 'w', encoding='utf-8') as f:
        f.write(" ".join(pdf))
    with open('temp_files/output.txt', 'r',  encoding='utf-8') as myfile:
        f = myfile.read()
    with open('temp_files/output.txt', 'r',  encoding='utf-8') as myfile:
        text = myfile.read()
    if 'Balaji Medical' in f:
        op = 'Tpappg@maxhealthcare.com May@2020 outlook.office365.com Max PPT'
        hosp_name = 'Max'
    else:
        op = 'mediclaim@inamdarhospital.org Mediclaim@2019 imap.gmail.com inamdar hospital'
        hosp_name = 'inamdar'
    ###########################################################
    wbkName = 'temp_files/' + 'Paramount' + hosp_name + '.xlsx'
    po=[]
    repeat=[]
    fg=[]
    f=''
    wbk = openpyxl.Workbook()
    wbk.create_sheet('1')
    wbk.create_sheet('Sheet1')
    sh1 = ['Sr No', 'CCN', 'Member PHS ID', 'Name of the Patient', 'Name of Insurance co.', 'Policy No', 'Employee No', 'Group Name']
    sh2 = ['Sr No', 'CCN', 'Payment To', 'Insurer UTR No.', 'Date of Payment to Hospital']
    sh3 = ['Sr No', 'CCN', 'Date of Admission', 'Date of Discharge', 'Amount Claimed', 'Claim Amt Settled', 'Amt Paid to Hospital',
           'Amt Paid to Member']
    s1 = wbk.worksheets[0]
    s2 = wbk.worksheets[1]
    s3 = wbk.worksheets[2]

    ccn = ''
    temp = re.compile(r"(?<=CCN No.).*").search(text)
    if temp is not None:
        temp = temp.group()
        for i in [':']:
            temp = temp.replace(i, '')
        ccn = temp.strip()

    sh1_regex = [r"(?<=Member PHS ID) *:* *\w+", r"(?<=Name of the Patient) *:* *[\w ]+(?= \w+)",
                 r"(?<=Name of Insurance co.).*(?=Amount)", r"(?<=Policy No).*(?=Insurer)",
                 r"(?<=Employee No) *:* *\S+", r"(?<=Group Name).*(?= {3,})"]
    sh2_regex = [r"(?<=Payment To).*", r"(?<=Insurer UTR\n).*", r"\S+\s*(?=Sum Insured)"]
    sh3_regex = [r"(?<=Date of Admission).*", r"(?<=Date of Discharge).*", r"(?<=Amount Claimed).*",
                 r"(?<=Claim Amt Settled).*", r"(?<=Amt Paid to Hospital).*", r"(?<=Amt Paid to Member).*"]

    sh1_data = ['1', ccn]
    for regex in sh1_regex:
        clean = ''
        temp = re.compile(regex).search(text)
        if temp is not None:
            temp = temp.group()
            for i in [':']:
                temp = temp.replace(i, '')
            clean = temp.strip()
        sh1_data.append(clean)

    sh2_data = ['1', ccn]
    for regex in sh2_regex:
        clean = ''
        temp = re.compile(regex).search(text)
        if temp is not None:
            temp = temp.group()
            for i in [':', '$$']:
                temp = temp.replace(i, '')
            clean = temp.strip()
        sh2_data.append(clean)

    sh3_data = ['1', ccn]
    for regex in sh3_regex:
        clean = ''
        temp = re.compile(regex).search(text)
        if temp is not None:
            temp = temp.group()
            for i in [':', 'Rs.', '/-']:
                temp = temp.replace(i, '')
            clean = temp.strip()
        sh3_data.append(clean)

    for i in range(0, len(sh1)):
        s1.cell(row=1, column=i + 1).value = sh1[i]
    for i in range(len(sh1_data)):
        s1.cell(row=2, column=i+1).value = sh1_data[i]

    for i in range(0, len(sh2)):
        s2.cell(row=1, column=i+1).value = sh2[i]
    for i in range(len(sh2_data)):
        s2.cell(row=2, column=i + 1).value = sh2_data[i]

    for i in range(0, len(sh3)):
        s3.cell(row=1, column=i+1).value = sh3[i]
    for i in range(len(sh3_data)):
        s3.cell(row=2, column=i + 1).value = sh3_data[i]
    wbk.save(wbkName)
    wbk.close()
    subprocess.run(["python", "make_master.py", 'Paramount', op, '', wbkName])
    ###########################################################
    move_master_to_master_insurer(sys.argv[2], pdfpath=pdfpath)
    mark_flag('X', sys.argv[2])
    print(f'processed {wbkName}')
except SystemExit as e:
    v = e.code
    if 'exit' in v:
        a = 1
        os._exit(0)
except:
    log_exceptions()