import mysql.connector
import sys
import re
import datetime

import pdftotext
from dateutil import parser as date_parser

from common import conn_data, mark_flag, get_row, date_formatting, move_attachment
from make_log import log_exceptions

try:
    row_data, sno = get_row(sys.argv[2]), sys.argv[3]
    mail_id = row_data['id']
    hospital = row_data['hospital']
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
            if i == 'payment_details':
                data = re.compile(j, re.DOTALL).search(f)
            else:
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
        try:
            datadict['adminssion_date'] = ad_date[0:2] + '-' + ad_date[2:4] + '-' + ad_date[4:]
        except:
            datadict['adminssion_date'] = ""
        datadict['ALNO'] = temp_l[2]
        datadict['tpa'] = temp_l[3]
    else:
        temp_l = ' '.join(temp_l)
        datadict['claim_no'] = temp_l.split(' ')[0].strip('CLAIM')
        datadict['ALNO'] = ""
        # if tmp := re.search(r"(?:^\W*)\d+ |(?: +)\d+", temp_l):
        #     ad_date = tmp.group().strip()
        #     try:
        #         datadict['adminssion_date'] = ad_date[0:2] + '-' + ad_date[2:4] + '-' + ad_date[4:]
        #     except:
        #         datadict['adminssion_date'] = ""
    if 'FAMILY' in datadict['tpa']:
        datadict['pname'] = datadict['pname'][1:-1]

    datadict['procesing_date'] = date_formatting(datadict['procesing_date'])
    datadict['adminssion_date'] = date_formatting(datadict['adminssion_date'])

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

    if 'UIIC' in datadict['insurer_name']:
        q = "insert into stgSettlement " \
            "(`unique_key`, `InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, `AccountNo`, " \
            "`BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`," \
            " `Transactiondate`, `DateofAdmission`, `DateofDischarge`, `mail_id`, `hospital`, `sett_table_sno`) "
        q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '

        params = [datadict['advice_no'], 'UIIC', 'City_TPA', datadict['ALNO'], datadict['claim_no'], '', '', '',
                  datadict['transaction_reference'], '', datadict['payment_amount'], '', datadict['payment_amount'],
                  datadict['procesing_date'], datadict['adminssion_date'], '', sys.argv[2], hospital, sno]

        q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
             "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, `TDS`=%s," \
             "`NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, `mail_id`=%s, " \
             "`hospital`=%s, `sett_table_sno`=%s"
        q = q + q1

        params = params + params[1:]

        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            cur.execute(q, params)
            con.commit()

    if 'india' in datadict['insurer_name'] or 'INDIA' in datadict['insurer_name']:
        # Date_on_attachment, Transaction_Reference_No, Claim_Number datadict['transaction_reference'] NIC_Records
        q = "select Date_on_attachment from NIC where Transaction_Reference_No=%s limit 1"
        q1 = "select Transaction_Reference_No, Claim_Number from NIC_Records where Transaction_Reference_No=%s limit 1"
        trandate, utrno, claimno = "", "", ""
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()

            cur.execute(q, [datadict['nia_transaction_reference']])
            if r := cur.fetchone():
                trandate = r[0]
                trandate = date_formatting(trandate)

            cur.execute(q1, [datadict['nia_transaction_reference']])
            if r := cur.fetchone():
                utrno, claimno = r

            q = "update stgSettlement set Transactiondate=%s, UTRNo=%s where unique_key=%s"
            cur.execute(q, [trandate,utrno, utrno + ',' + claimno])
            con.commit()

    move_attachment(datadict['claim_no'], sys.argv[1], hospital)
    mark_flag('X', sys.argv[2])
    print("processed ", hospital, ' ', mail_id)
except:
    log_exceptions()
