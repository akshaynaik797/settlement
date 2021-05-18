import random
import re
import sys

import camelot
import openpyxl
import tabula

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data, get_from_ins_big_utr_date
from make_log import log_exceptions

try:
    mail_id = sys.argv[2]
    tables = camelot.read_pdf(sys.argv[1], pages='all')
    flag = None
    data = []
    if tables.n > 0:
        tables.export('temp_files/foo1.xlsx', f='excel')
        flag = True
    if flag:
        wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
        sheet = wb.worksheets[0]
        for row in sheet.rows:
            tmp = [i.value for i in row]
            data.append(tmp)
        data = data[3:]
        data = [["" if j is None else j for j in i] for i in data]

    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=Intimation No).*(?=Bill)", r"(?<=Claim Intimation No.).*"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Claimant Name).*(?=Product)"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=DOA).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=DOD).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurance Company).*"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*(?=Payee)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Final Diagnosis).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=UTR/Cheque No).*(?=dated)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*(?=\.)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Beneficiary Acc No).*(?=UTR)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Total amount claimed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Total Claim Payable Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Total Claim Payable Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Total Co-pay Amt.).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount allowed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'UTRNo' not in datadict:
        datadict['UTRNo'], datadict['Transactiondate'] = get_from_ins_big_utr_date(mail_id)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['InsurerID'] = 'star'

    deductions = []

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    # x1 = ""
    # regex = r"(?<=REMARKS\n)[\s\S]+(?=\n *DISCOUNT DETAILS)"
    # if data := re.search(regex, f):
    #     data =
    #     [re.split(r" {3,}", i)[-2:] for i in data.group().split('\n')]

    try:
        for i in data:
            tmp = {}
            for j, k in zip(["Details", "BillAmount", "DeductedAmt", "PayableAmount", "DeductionReason"], [i[2], i[5], i[6], i[8] ,i[9]]):
                tmp[j] = k
            tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
            tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
            deductions.append(tmp)
    except:
        pass

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
