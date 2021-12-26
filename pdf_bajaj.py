import re
import sys
import random

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data, get_row
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    row_data = get_row(sys.argv[2])
    f = f.replace('***', '')

    insurer = re.compile(r"(?<=as instructed by).*").search(f)
    if insurer is not None:
        insurer = insurer.group().strip()
    else:
        insurer = "bajaj"
    ins_list = (
        ('chola', 'CHOLAMANDALAM'),
        ('bajaj', 'BAJAJ'),
        ('Max_Bupa', 'MAX BUPA')
    )
    for i, j in ins_list:
        if j in insurer:
            insurer = i
            break

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim Number).*", r"(?<=Claim No).*", r"(?<=Customer Ref).*(?=_)", r"(?<=Customer Ref).*"], [':', 'Claim No'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No :).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=UTR No).*", r"(?<=UTR Reference).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Approval Date).*", r"(?<=We have on).*(?=made)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Bill Amount).*(?=\nPaid Amount)", r"(?<=Bill Amount).*", r"(?<=GROSS AMOUNT)\s*\S+", r"(?<=Billed Amount)\s*\w+"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Bill Amount).*(?=\nPaid Amount)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Paid Amount).*", r".*(?=as instructed by)", r"(?<=NET Amount Paid).*"], [':', 'Rs.', 'INR', '/-', ','], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date Of Admission).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date Of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Name of Insurance co.).*(?=.)"], [':'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=ID Card No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r".*(?=\s*Diagnosis)", r"(?<=Diagnosis :).*"], [':'], r"^.*$"],
        'Discount': [[r"(?<=Discount).*"], [], r"^.*$"],
        'TDS': [[r"(?<=TDS Amount).*", r"(?<=TDS Amount).*", r"(?<=TDS)\s*\w+", r"(?<=TDS).*(?=\/)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        try:
            regex = r"(?<=No\.\n).*?(?=\n *Page 1)"
            if tmp := re.search(regex, f, re.DOTALL):
                tmp = [re.split(r" {2,}", i) for i in tmp.group().split('\n')]
                datadict['ClaimNo'] = tmp[0][3] + tmp[1][-1]
                datadict['SettledAmount'], datadict['TDS'], datadict['NetPayable'] = tmp[0][4], tmp[0][6], tmp[0][7]
        except:
            pass

    for k, v in regex_dict.items():
        if k in datadict:
            for i in v[1]:
                datadict[k] = datadict[k].replace(i, '')

    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]
    datadict['InsurerID'] = insurer

    x1 = ""
    regexe = r"\w+(?: ?\w+) +\d+ + \d+ +\d+.*"
    data = re.findall(regexe, f)
    for i, j in enumerate(data):
        j = re.compile(r" {5,}").split(j)
        data[i] = j

    for i, j in enumerate(data):
        while len(j) < 5:
            j.append("")
        data[i] = j

    deductions = []
    for i in data:
        tmp = {}
        for j, k in zip(["Details", "BillAmount", "DeductedAmt", "PayableAmount", "DeductionReason"], i):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)
    if 'PAYEE ADVICE' in f:
        utrno = ""
        if 'UTRNo' in datadict:
            utrno = datadict['UTRNo']
        if tmp := re.search(r"(?<=AMOUNT\(INR\)\nNo.\n).*(?=\n *Page 1)", f, re.DOTALL):
            tmp = [re.split(r" +", i) for i in tmp.group().split('\n')]
            for j, i in enumerate(tmp):
                if len(i) == 8:
                    datadict = {}
                    datadict['ALNO'], datadict['PatientName'], datadict['ClaimNo'], datadict['BilledAmount'], \
                    datadict['TDS'], datadict['NetPayable'], datadict['Transactiondate'] = i[0], i[2], i[3], \
                                                                                           i[4], i[6], i[7], i[1]
                    datadict['NetPayable'] = datadict['NetPayable'].replace(',', '')
                    datadict['TPAID'], datadict['InsurerID'] = 'sc', insurer
                    row = tmp[j+1]
                    if len(row) == 3:
                        datadict['ALNO'] += row[0]
                        datadict['Transactiondate'] += row[1]
                        datadict['ClaimNo'] += row[2]
                    if len(row) == 4:
                        datadict['ALNO'] += row[0]
                        datadict['Transactiondate'] += row[1]
                        datadict['PatientName'] += row[2]
                        datadict['ClaimNo'] += row[3]
                    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
                    datadict['UTRNo'] = utrno
                    datadict['file_name'] = sys.argv[0]
                    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
                if len(i) == 5:
                    z = datadict['Transactiondate']
                    datadict = {}
                    datadict['ALNO'], datadict['PatientName'], datadict['ClaimNo'], datadict['BilledAmount'], \
                    datadict['TDS'], datadict['NetPayable'], datadict['Transactiondate'] = i[0], i[4], i[0], \
                                                                                           i[1], i[2], i[3], z
                    datadict['NetPayable'] = datadict['NetPayable'].replace(',', '')
                    datadict['TPAID'], datadict['InsurerID'] = 'sc', insurer
                    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
                    datadict['UTRNo'] = utrno
                    datadict['file_name'] = sys.argv[0]
                    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
                if len(i) == 6:
                    z = datadict['Transactiondate']
                    datadict = {}
                    datadict['ALNO'], datadict['PatientName'], datadict['ClaimNo'], datadict['BilledAmount'], \
                    datadict['TDS'], datadict['NetPayable'], datadict['Transactiondate'] = i[2], '', i[2], \
                                                                                           i[3], i[4], i[5], z
                    datadict['NetPayable'] = datadict['NetPayable'].replace(',', '')
                    datadict['TPAID'], datadict['InsurerID'] = 'sc', insurer
                    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
                    datadict['UTRNo'] = utrno
                    datadict['file_name'] = sys.argv[0]
                    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
    else:
        ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
