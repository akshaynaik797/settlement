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
        'ClaimNo': [[r"(?<=claim number).*(?=towards)"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Claimant/Patient).*"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=DOA).*(?=-)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=DOD).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=policy issued by).*(?=has been)", r"(?<=policyholder of the)[\s\S]*?(?=\.)"], [':', '.', '\n'], r"^.*$"],
        'CorporateName': [[], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Disease).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=transaction number).*(?=dated)"], [':', '.', 'Â'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*(?=towards)", r"(?<=Cheque No\/Date).*?(?=-)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Bank Account No).*(?=on)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Claim Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Amt).*(?=\[TDS)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Pay Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co pay).*(?=Deductible)"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS).*(?=\])"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount Amt).*"], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]

    try:
        regex = r"(?<=NEFT Transaction No.\n).*(?=\n.*Bill)"
        if tmp := re.search(regex, f, re.DOTALL):
            tmp = [re.split(r" {2,}", i) for i in tmp.group().split('\n')]
            datadict['Transactiondate'], datadict['UTRNo'] = tmp[1][-2], tmp[1][-1]
    except:
        pass
    deductions = []
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
        data = data[2:]
        data = [["" if j is None else j for j in i] for i in data]

        for row in data:
            tmp = {}
            _, tmp["Details"], tmp["BillAmount"], tmp["PayableAmount"], tmp["DeductedAmt"], tmp[
                "DeductionReason"] = row
            tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
            tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
            deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
