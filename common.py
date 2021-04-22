import re

import mysql.connector
import pdftotext

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'python'}

table_fields = (
    "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")

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
        pass
    finally:
        return data_dict


def ins_upd_data(mail_id, hospital, datadict):
    datadict["mail_id"], datadict["hospital"] = mail_id, hospital
    datadict["mail_id"], datadict["hospital"] = "ak", "ak"
    for i in table_fields:
        if i not in datadict:
            datadict[i] = ""
    q = "insert into stgSettlement (`unique_key`, `InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, " \
        "`AccountNo`, `BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`, " \
        "`Transactiondate`, `DateofAdmission`, `DateofDischarge`, `mail_id`, `hospital`, `POLICYNO`)"
    q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '

    params = [datadict['unique_key'], datadict['InsurerID'], datadict['TPAID'], datadict['ALNO'], datadict['ClaimNo'],
              datadict['PatientName'], datadict['AccountNo'], datadict['BeneficiaryBank_Name'], datadict['UTRNo'],
              datadict['BilledAmount'], datadict['SettledAmount'], datadict['TDS'], datadict['NetPayable'],
              datadict['Transactiondate'], datadict['DateofAdmission'], datadict['DateofDischarge'],
              datadict['mail_id'], datadict['hospital'], datadict['POLICYNO']]

    q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
         "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, " \
         "`TDS`=%s, `NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, " \
         "`mail_id`=%s, `hospital`=%s, `POLICYNO`=%s"
    q = q + q1

    params = params + params[1:]

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        con.commit()
