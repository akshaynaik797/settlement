import re

import mysql.connector
import pdftotext

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'python'}

stg_sett_fields = (
    "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")

stg_sett_deduct_fields = (
"TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
"Discount", "DeductionCategory", "MailID", "HospitalID")

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


def ins_upd_data(mail_id, hospital, datadict, deductions):
    datadict["mail_id"], datadict["hospital"] = mail_id, hospital
    for i in stg_sett_fields:
        if i not in datadict:
            datadict[i] = ""

    q = "insert into stgSettlement (`unique_key`, `InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, " \
        "`AccountNo`, `BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`, " \
        "`Transactiondate`, `DateofAdmission`, `DateofDischarge`, `mail_id`, `hospital`, `POLICYNO`, " \
        "`CorporateName`, `MemberID`, `Diagnosis`, `Discount`, `Copay`)"
    q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '

    params = [datadict['unique_key'], datadict['InsurerID'], datadict['TPAID'], datadict['ALNO'], datadict['ClaimNo'],
              datadict['PatientName'], datadict['AccountNo'], datadict['BeneficiaryBank_Name'], datadict['UTRNo'],
              datadict['BilledAmount'], datadict['SettledAmount'], datadict['TDS'], datadict['NetPayable'],
              datadict['Transactiondate'], datadict['DateofAdmission'], datadict['DateofDischarge'],
              datadict['mail_id'], datadict['hospital'], datadict['POLICYNO'], datadict['CorporateName'],
              datadict['MemberID'], datadict['Diagnosis'], datadict['Discount'], datadict['Copay']]

    q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
         "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, " \
         "`TDS`=%s, `NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, " \
         "`mail_id`=%s, `hospital`=%s, `POLICYNO`=%s, `CorporateName`=%s, `MemberID`=%s, `Diagnosis`=%s, " \
         "`Discount`=%s, `Copay`=%s"
    q = q + q1

    params = params + params[1:]

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        con.commit()

    for num, row in enumerate(deductions):
        for i in stg_sett_deduct_fields:
            if i not in row:
                row[i] = ""
        row["DeductionCategory"] = get_deduction_category(row["Details"], row["DeductionReason"])
        deductions[num] = row

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        for row in deductions:
            p = "insert into stgSettlementDeduction (`TPAID`,`ClaimID`,`Details`,`BillAmount`,`PayableAmount`," \
                "`DeductedAmt`, `DeductionReason`,`Discount`,`DeductionCategory`,`MailID`,`HospitalID`)"
            p = p + ' values (' + ('%s, ' * p.count(',')) + '%s) '
            p_params = [row['TPAID'], row['ClaimID'], row['Details'], row['BillAmount'], row['PayableAmount'],
                        row['DeductedAmt'], row['DeductionReason'], row['Discount'], row['DeductionCategory'],
                        row['MailID'], row['HospitalID']]
            cur.execute(p, p_params)
        con.commit()
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
            print(reasons, details)
        else:
            category = '5'
    return category
