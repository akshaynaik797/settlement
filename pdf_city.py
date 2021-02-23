import mysql.connector
import sys
import re
import datetime

import pdftotext
from dateutil import parser as date_parser

from custom_parallel import conn_data, write


try:
    with open(sys.argv[1], "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('temp_files/output.txt', 'w', encoding='utf-8') as f:
        f.write(" ".join(pdf))
    with open('temp_files/output.txt', 'r', encoding='utf-8') as myfile:
        f = myfile.read()

    start = now = datetime.datetime.now()
    badchars = ('/',)
    if f != '':
        datadict = {}
        regexdict = {'transaction_reference': [r"(?<=Transaction Reference:).*"],
                     'payer_reference_no': [r"(?<=Reference No:).*"],
                     'payment_amount': [r"(?<=Payment Amount:).*"],
                     'payment_details': [r"(?<=Payment Details:)[\w\W]+(?=Kindly)"],
                     'nia_transaction_reference': [r"(?<=Payment Details: N)\d+"],
                     'claim_no': [r"(?<=CLAIM).*"],
                     'pname': [r".*(?=,ADMSN)"],
                     'adminssion_date': [r"(?<=ADMSN) ?\d+"],
                     'insurer_name': [r"(?<=behalf of).*"],
                     'tpa': [r"(?<=TPA-).*"],
                     'procesing_date': [r"(?<=Processing Date:).*"]}

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

        temp = re.compile(r"(?<=BCS_).*").search(sys.argv[5])
        if temp is None:
            datadict['advice_no'] = ""
        else:
            datadict['advice_no'] = temp.group()

        if datadict['adminssion_date'] != "":
            a = datadict['adminssion_date']
            a = date_parser.parse(a[0:2] + '/' + a[2:4] + '/' + a[4:])
            datadict['adminssion_date'] = a.strftime("%d-%b-%Y")

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
                sys.argv[7])
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            sql = "insert into City_Records (`Advice_No`,`Insurer_name`,`City_Transaction_Reference`,`Payer_Reference_No`,`Payment_Amount`,`Processing_Date`,`City_Claim_No`,`City_Patient_name`,`City_Admission_Date`,`City_TPA`,`Payment_Details`,`NIA_Transaction_Reference`, `hospital`) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, data)
            con.commit()
except:
    log_exceptions()
