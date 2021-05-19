import random
import re
import sys

import camelot
import openpyxl
from tabula import read_pdf

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=CCN No).? *:? *\S+"], [':', '(', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Name of the Patient).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No.).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=Insurer UTR No).*", r"(?<=Insurer\n).*(?=\n.*UTR)"], [':', '.', 'UTR'], r"^\S+$"],
        'Transactiondate': [[r"\S+(?=\n *Hospital)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Amount Claimed).*", r"(?<=claimed for)[\s\S]+?(?=Towards)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Claim Amt Settled).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount Paid).*", r"(?<=settled for)[\s\S]+?(?=Against)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Name of Insurance co.).*(?=.)", r"(?<=issued by the).*(?=has been)"], [':'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Member PHS ID)(?: *:? *)\S+"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=treatment of).*(?=at)"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=TDS Deduction).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Copay).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)

    for i,j in [("Transactiondate", r"(?<=Payment to).*?(?=Hospital)"), ("UTRNo", r"(?<=Insurer).*?(?=No\.)")]:
        if i not in datadict:
            datadict[i] = ""
            if tmp := re.search(j, f, re.DOTALL):
                datadict[i] = tmp.group()
                for bad in [':', '.', '\n', 'UTR']:
                    datadict[i] = datadict[i].replace(bad, '').strip()

    if tmp := re.search(r"\d+(?:\/\d+){2}", datadict['Transactiondate']):
        datadict['Transactiondate'] = tmp.group().strip()
    if 'Employee No' in datadict['UTRNo']:
        if tmp := re.search(r"^\w+", datadict['UTRNo']):
            datadict['UTRNo'] = tmp.group().strip()
    if 'Policy No' in datadict['UTRNo']:
        if tmp := re.search(r"\w+$", datadict['UTRNo']):
            datadict['UTRNo'] = tmp.group().strip()
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]


    tables = camelot.read_pdf(sys.argv[1], pages='all')
    flag = None
    if tables.n > 0:
        tables.export('temp_files/foo1.xlsx', f='excel')
        flag = True
    if flag:
        wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
        sheet = wb.worksheets[1]
        data = []
        for row in sheet.rows:
            tmp = [i.value for i in row]
            data.append(tmp)
        data = [["" if j is None else j for j in i] for i in data]
        data = [[str(j).replace('\t', '') for j in i] for i in data]
        data = data[2:]
    deductions = []
    for row in data:
        tmp = {}
        tmp["Details"], tmp["BillAmount"], tmp["DeductedAmt"], tmp["DeductionReason"] = row[3:]
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)


    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
