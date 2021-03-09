import mysql.connector
import sys
import re
import datetime

import pdftotext
from dateutil import parser as date_parser

from backend import conn_data, mark_flag, get_hospital, get_row
from make_log import log_exceptions

try:
    hospital = get_hospital(sys.argv[1])
    row_data = get_row(sys.argv[1])
    mail_id = row_data['id']
    with open(sys.argv[1], "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('temp_files/output.txt', 'w', encoding='utf-8') as f:
        f.write(" ".join(pdf).replace('\n', ''))
    with open('temp_files/output.txt', 'r', encoding='utf-8') as myfile:
        f = myfile.read()

    start = now = datetime.datetime.now()
    badchars = ('/',)
    datadict = {}
    regexdict = {'transaction_reference': [r"(?<=Transaction Reference:).*(?=Payer)"],
                 'payer_reference_no': [r"(?<=Reference No:).*(?=Beneficiary)"],
                 'payment_amount': [r"(?<=Payment Amount:).*(?=Currency)"],
                 'payment_details': [r"(?<=Payment Details:).*(?=Kindly)"],
                 'nia_transaction_reference': [r"(?<=Details:N).*(?=Kindly)", r"(?<=Details: N).*(?=Kindly)", r"(?<=Details :N).*(?=Kindly)"],
                 'claim_no': [r"(?<=CLAIM).*"],
                 'pname': [r".*(?=,ADMSN)"],
                 'adminssion_date': [r"(?<=ADMSN) ?\d+"],
                 'insurer_name': [r"(?<=behalf of).*(?=Transaction Reference:)"],
                 'tpa': [r"(?<=TPA-).*"],
                 'procesing_date': [r"(?<=Processing Date:).*(?=Payment Details)"]}

    for i in regexdict:
        for j in regexdict[i]:
            data = re.compile(j).search(f)
            if data is not None:
                temp = data.group().strip()
                for k in badchars:
                    temp = temp.replace(k, "")
                datadict[i] = temp
                break
            datadict[i] = ""

    temp = re.compile(r"(?<=BCS_).*").search(row_data['subject'])
    if temp is None:
        datadict['advice_no'] = ""
    else:
        datadict['advice_no'] = temp.group()

    if datadict['adminssion_date'] != "":
        a = datadict['adminssion_date']
        a = date_parser.parse(a[0:2] + '/' + a[2:4] + '/' + a[4:])
        datadict['adminssion_date'] = a.strftime("%d-%b-%Y")
    temp_l = datadict['payment_details'].split(',')
    if len(temp_l) == 4:
        datadict['claim_no'] = temp_l[0]
        ad_date = ""
        temp = re.compile(r'\d+').search(temp_l[1])
        if temp is not None:
            ad_date = temp.group()
        datadict['adminssion_date'] = ad_date
        datadict['pname'] = temp_l[2]
        datadict['tpa'] = temp_l[3]



    data = (datadict['advice_no'],
            datadict['insurer_name'],
            datadict['transaction_reference'],
            datadict['payer_reference_no'],
            datadict['payment_amount'],
            datadict['procesing_date'],
            datadict['claim_no'],
            datadict['pname'],
            datadict['adminssion_date'],
            datadict['tpa'],
            datadict['payment_details'],
            datadict['nia_transaction_reference'],
            hospital, mail_id)
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        sql = "insert into City_Records (`Advice_No`,`Insurer_name`,`City_Transaction_Reference`,`Payer_Reference_No`,`Payment_Amount`,`Processing_Date`,`City_Claim_No`,`City_Patient_name`,`City_Admission_Date`,`City_TPA`,`Payment_Details`,`NIA_Transaction_Reference`, `hospital`, mail_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(sql, data)
        con.commit()
    mark_flag('X', sys.argv[1])
except:
    log_exceptions()
