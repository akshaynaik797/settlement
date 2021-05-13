import datetime
import re
from pathlib import Path
from os import path
from shutil import copyfile

import mysql.connector
import pdftotext

from make_log import log_exceptions

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'python'}

stg_sett_fields = (
    "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay", "sett_table_sno")

stg_sett_deduct_fields = (
"TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
"Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

regex_dict = {'InsurerID': [[], [], r"^.*$"],
              'ALNO': [[], [], r"^.*$"],
              'ClaimNo': [[], [], r"^.*$"],
              'PatientName': [[], [], r"^.*$"],
              'AccountNo': [[], [], r"^.*$"],
              'BeneficiaryBank_Name': [[], [], r"^.*$"],
              'UTRNo': [[], [], r"^.*$"],
              'BilledAmount': [[], [], r"^.*$"],
              'SettledAmount': [[], [], r"^.*$"],
              'TDS': [[], [], r"^.*$"],
              'NetPayable': [[], [], r"^.*$"],
              'Transactiondate': [[], [], r"^.*$"],
              'DateofAdmission': [[], [], r"^.*$"],
              'DateofDischarge': [[], [], r"^.*$"],
              'POLICYNO': [[], [], r"^.*$"],
              'CorporateName': [[], [], r"^.*$"],
              'MemberID': [[], [], r"^.*$"],
              'Diagnosis': [[], [], r"^.*$"],
              'Discount': [[], [], r"^.*$"],
              'Copay': [[], [], []]
              }

def update_date_utr_nic_city(unique_key):
    tranref = unique_key.split(',')[0]
    q1 = "select `Date_Of_Mail` from `NIC` where `Transaction_Reference_No`=%s limit 1"
    q2 = "select `City_Transaction_Reference` from `City_Records` where `NIA_Transaction_Reference`=%s limit 1"
    trandate, utrno = "", ""
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q1, [tranref])
        if r := cur.fetchone():
            trandate = r[0]
            trandate = trandate.split(' ')[0]

        cur.execute(q2, [tranref])
        if r := cur.fetchone():
            utrno = r[0]

        q = "update stgSettlement set Transactiondate=%s, UTRNo=%s where unique_key like %s"
        cur.execute(q, [trandate, utrno, '%' + tranref + '%'])
        con.commit()


def get_from_db_and_pdf(mail_id, file):
    row_data = get_row(mail_id)
    mail_id, hospital = row_data['id'], row_data['hospital']
    with open(file, "rb") as f:
        pdf = pdftotext.PDF(f)
    with open('temp_files/output.txt', 'w', encoding='utf-8') as f:
        f.write(" ".join(pdf))
    with open('temp_files/output.txt', 'r', encoding='utf-8') as myfile:
        f = myfile.read()
    return mail_id, hospital, f


def get_row(mid):
    fields = (
        "id", "subject", "date", "sys_time", "attach_path", "completed", "sender", "sno", "folder", "process",
        "hospital")
    temp = {}
    for i in fields:
        temp[i] = ""
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select * from settlement_mails where id=%s order by sno desc limit 1"
        cur.execute(q, (mid,))
        r = cur.fetchone()
        if r is not None:
            for k, v in zip(fields, r):
                temp[k] = v
    return temp


def mark_flag(flag, mid):
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "update settlement_mails set completed=%s where id=%s;"
        cur.execute(q, (flag, mid))
        q = "update utr_mails set completed='' where id=%s;"
        cur.execute(q, (mid,))
        con.commit()


def get_data_dict(regex_dict, text):
    data_dict = {}
    try:
        for key, value in regex_dict.items():
            for regex in value[0]:
                if tmp := re.compile(regex).search(text):
                    data = tmp.group().strip()
                    for badchar in value[1]:
                        data = data.replace(badchar, '').strip()
                    if re.compile(value[2]).match(data):
                        data_dict[key] = data
                        break
    except:
        log_exceptions()
    finally:
        return data_dict


def ins_upd_data(mail_id, sett_sno, hospital, datadict, deductions):
    datadict["mail_id"], datadict["hospital"], datadict['sett_table_sno'] = mail_id, hospital, sett_sno
    for i in stg_sett_fields:
        if i not in datadict:
            datadict[i] = ""

    if datadict['Transactiondate'] == '':
        datadict['Transactiondate'] = get_row(mail_id)['date'].split(' ')[0]

    datadict['Transactiondate'] = date_formatting(datadict['Transactiondate'])
    datadict['DateofAdmission'] = date_formatting(datadict['DateofAdmission'])
    datadict['DateofDischarge'] = date_formatting(datadict['DateofDischarge'])

    q = "insert into stgSettlement (`unique_key`, `InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, " \
        "`AccountNo`, `BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`, " \
        "`Transactiondate`, `DateofAdmission`, `DateofDischarge`, `mail_id`, `hospital`, `POLICYNO`, " \
        "`CorporateName`, `MemberID`, `Diagnosis`, `Discount`, `Copay`, `sett_table_sno`)"
    q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '

    params = [datadict['unique_key'], datadict['InsurerID'], datadict['TPAID'], datadict['ALNO'], datadict['ClaimNo'],
              datadict['PatientName'], datadict['AccountNo'], datadict['BeneficiaryBank_Name'], datadict['UTRNo'],
              datadict['BilledAmount'], datadict['SettledAmount'], datadict['TDS'], datadict['NetPayable'],
              datadict['Transactiondate'], datadict['DateofAdmission'], datadict['DateofDischarge'],
              datadict['mail_id'], datadict['hospital'], datadict['POLICYNO'], datadict['CorporateName'],
              datadict['MemberID'], datadict['Diagnosis'], datadict['Discount'], datadict['Copay'], datadict['sett_table_sno']]

    q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
         "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, " \
         "`TDS`=%s, `NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, " \
         "`mail_id`=%s, `hospital`=%s, `POLICYNO`=%s, `CorporateName`=%s, `MemberID`=%s, `Diagnosis`=%s, " \
         "`Discount`=%s, `Copay`=%s, `sett_table_sno`=%s"
    q = q + q1

    params = params + params[1:]

    q2 = "select srno from stgSettlement where unique_key=%s limit 1"
    q2_params = (datadict['unique_key'],)
    last_id = -1
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        con.commit()
        cur.execute(q2, q2_params)
        r = cur.fetchone()
        if r:
            last_id = r[0]

    for num, row in enumerate(deductions):
        for i in stg_sett_deduct_fields:
            if i not in row:
                row[i] = ""
        row["DeductionCategory"] = get_deduction_category(row["Details"], row["DeductionReason"])
        row["stgsettlement_sno"] = last_id
        deductions[num] = row

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "delete from stgSettlementDeduction where stgsettlement_sno=%s"
        cur.execute(q, (last_id,))
        for row in deductions:
            p = "insert into stgSettlementDeduction (`stgsettlement_sno`, `TPAID`,`ClaimID`,`Details`,`BillAmount`,`PayableAmount`," \
                "`DeductedAmt`, `DeductionReason`,`Discount`,`DeductionCategory`,`MailID`,`HospitalID`)"
            p = p + ' values (' + ('%s, ' * p.count(',')) + '%s) '
            p_params = [last_id, row['TPAID'], row['ClaimID'], row['Details'], row['BillAmount'], row['PayableAmount'],
                        row['DeductedAmt'], row['DeductionReason'], row['Discount'], row['DeductionCategory'],
                        row['MailID'], row['HospitalID']]
            cur.execute(p, p_params)
        con.commit()
    attach_path = get_row(mail_id)['attach_path']
    if not path.exists('sftp_folder'):
        move_attachment(datadict['ALNO'], attach_path, hospital)
    print("processed ", hospital, ' ', mail_id)


def get_deduction_category(details, reasons):
    category = ''
    if details == None and reasons == None:
        pass
    elif details.lower().find('co-pay') != -1 or details.lower().find('copay') != -1 or details.lower().find(
            'co pay') != -1 or details.lower().find('co-payment') != -1:
        category = '1'

    elif details.lower().find('nme') != -1 or details.lower().find('non-consumable') != -1 or details.lower().find(
            'non payable') != -1 or details.lower().find('not payable') != -1:
        category = '5'

    elif details.lower().find('disc') != -1 and details.lower().find('discharge') == -1:
        category = '6'

    elif details.lower().find('per soc') != -1 or details.lower().find('tariff') != -1 or details.lower().find(
            'do not collect') != -1 or details.lower().find('not to be collect') != -1 or details.lower().find(
        'not to collect') != -1 or details.lower().find('as per mou') != -1 or details.lower().find(
        'as per ppn') != -1 or details.lower().find('as per mini soc') != -1 or details.lower().find(
        'as per hospital') != -1:
        category = '7'


    elif details.lower().find('as per patient') != -1 or details.lower().find(
            'as per policy') != -1 or details.lower().find(
            'as per authorization') != -1 or details.lower().find('excess room') != -1:
        category = '2'

    elif details.lower().find('paid by patient') != -1 or details.lower().find('room') != -1:
        if reasons != None:
            if reasons.lower().find('package') != -1 or reasons.lower().find('pkg') != -1 or reasons.lower().find(
                    'icu') != -1 or reasons.lower().find('hospital') != -1 or reasons.lower().find(
                'consultant') != -1 or reasons.lower().find('room') != -1:
                category = '2'
            else:
                category = '5'
        else:
            category = '5'


    elif details.lower().find('member paid') != -1 or details.lower().find('admin') != -1 or details.lower().find(
            'micro') != -1 or details.lower().find('casu') != -1 or details.lower().find(
        'TPA') != -1 or details.lower().find(
        'payable') != -1 and details.lower().find('not') != -1 or details.lower().find('non') != -1:
        category = '5'

    elif details.lower().find('non') != -1 and details.lower().find('med') != -1 or details.lower().find('adm') != -1:
        category = '5'

    elif details.lower().find('exhausted') != -1 or details.lower().find('gipsa') != -1 or details.lower().find(
            'ppn') != -1 or details.lower().find('pkg') != -1 or details.lower().find(
        'over') != -1 or details.lower().find(
        'excess') != -1 or details.lower().find('room') != -1 or details.lower().find(
        'limit') != -1 or details.lower().find(
        'exceed') != -1:
        category = '3'


    elif details.lower().find('tax') != -1 or details.lower().find('tds') != -1 or details.lower().find('gst') != -1:
        category = '8'

    elif details.lower().find('mou ') != -1:
        category = '6'


    else:
        if reasons != None and reasons.lower().find('other') != -1:
            category = '4'
        else:
            category = '5'
    return category


def get_from_ins_big_utr_date(mail_id):
    q = "select utr, date from ins_big_utr_date where `id`=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (mail_id,))
        if r := cur.fetchone():
            return r
        return ("", "")


def date_formatting(date):
    # d b m Y
    #30/12/2121
    # 30-12-3202
    # 30-Feb-1232
    # 12 Feb 2021
    # 12 Feb 21
    formats = ['%d/%m/%Y', '%d-%m-%Y', '%d-%b-%Y', '%d-%b-%y', '%d %b %Y', '%d %b %y']
    date = date.strip()
    for i in formats:
        try:
            date = datetime.datetime.strptime(date, i)
            date = date.strftime('%d/%m/%Y')
            break
        except:
            pass
    return date


def move_attachment(alno, pdfpath, hospital):
    f_dst = f"../index/Attachments/{hospital}/"
    if alno == '':
        copyfile(pdfpath, path.join(f_dst, path.split(pdfpath)[-1]))
        return True
    Path(f_dst).mkdir(parents=True, exist_ok=True)
    ext = path.splitext(pdfpath)
    f_dst = path.join(f_dst, alno.replace('/', '-') + ext[-1])
    copyfile(pdfpath, f_dst)
    q = "update stgSettlement set attachment='X' where ALNO=%s"
    q1 = "update stgSettlement set attachment='X' where ClaimNo=%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (alno,))
        cur.execute(q1, (alno,))
        con.commit()
