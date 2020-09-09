import subprocess

import openpyxl
import pdftotext
import re
import sys
from make_log import log_exceptions
from movemaster import move_master_to_master_insurer

try:
    pdfpath = sys.argv[1]
    with open(pdfpath, "rb") as f:
        pdf = pdftotext.PDF(f)
        data = "\n\n".join(pdf)
    with open('temp_files/temppdf.txt', "w") as f:
        f.write(data)
    with open('temp_files/temppdf.txt', "r") as f:
        f = f.read()

    if 'CIMETS INAMDAR MULTISPECIALITY HOSPITAL' in f:
        hosp_name = 'inamdar'
    else:
        hosp_name = 'Max'

    regex = r'(?<=UTR Reference).*'
    x = re.search(regex, f)
    if x:
        utr = x.group().strip()
    else:
        utr = ''

    regex = r'\d+ +\d{2}/\d{2}/.+'
    list1 = re.findall(regex, f)
    list1 = [re.split(r' {2,}', i) for i in list1]
    regex = r'\d{4} +\d{4}.*'
    list2 = re.findall(regex, f)
    list2 = [re.split(r' {2,}', i) for i in list2]

    table = []
    if len(list1) == len(list2):
        for i, j in zip(list1, list2):
            datadict = {}
            datadict['appr_no'] = i[0] + j[0]
            datadict['date'] = i[1] + j[1]
            if j[2].isdigit() is True:
                datadict['name'] = i[2]
            else:
                datadict['patientname'] = i[2] + ' ' + j[2]
            if len(j) > 3:
                datadict['claimno'] = i[3] + j[3]
            else:
                datadict['claimno'] = i[3] + j[2]
            datadict['amt'] = i[-1].replace(',', '')
            datadict['tds'] = i[-2]
            datadict['utr_ref'] = utr

    wbk = openpyxl.Workbook()
    s1 = wbk.worksheets[0]
    mydata = [datadict['appr_no'], datadict['claimno'], datadict['patientname'], hosp_name, datadict['amt'],
              datadict['tds'], datadict['date'], datadict['utr_ref']]
    mylist = ['appr_no', 'claimno', 'patientname', 'hospital_name', 'Approved Amount', 'TDS', 'Payment Date', 'UTR reference']

    rowno = s1.max_row + 1
    for i, j in enumerate(mylist):
        s1.cell(row=1, column=i + 1).value = j
        s1.cell(row=rowno, column=i + 1).value = mydata[i]
    wbname = 'temp_files/'+'bajaj' + hosp_name + '.xlsx'
    wbk.save(wbname)
    wbk.close()
    if hosp_name == 'Max':
        op = 'Tpappg@maxhealthcare.com May@2020 outlook.office365.com Max PPT'
        subprocess.run(["python", "make_master.py", 'bajaj', op, '', wbname])
        move_master_to_master_insurer('')
        print(f'processed {wbname}')
    else:
        op = 'mediclaim@inamdarhospital.org Mediclaim@2019 imap.gmail.com inamdar hospital'
        subprocess.run(["python", "make_master.py", 'bajaj', op, '', wbname])
        move_master_to_master_insurer('')
        print(f'processed {wbname}')

except:
    log_exceptions()
