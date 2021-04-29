import re
import sys

import camelot
import openpyxl

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    tables = camelot.read_pdf(sys.argv[1], pages='all')
    flag = None
    if tables.n > 0:
        tables.export('temp_files/foo1.xlsx', f='excel')
        flag = True
    if flag:
        wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
        sheet = wb.worksheets[0]
        data = []
        for row in sheet.rows:
            tmp = [i.value for i in row]
            data.append(tmp)
        data = data[2:]
        data = [["" if j is None else j for j in i] for i in data]

    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=with CCN).*(?=, under)"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Main)"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=policy number).*(?=,)"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=From :).*(?=To)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=To :).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Ailment).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=UTR)[\s\S]*?(?=and)"], [':', '.', 'No'], r"^\S+$"],
        'Transactiondate': [[r"(?<=and Transaction Date).*"], [':'], ""],
        'AccountNo': [[r"(?<=Account No).*(?=with)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=with).*(?=and IFSC Code)"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Total amount claimed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Total Co-pay Amt.).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount allowed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    deductions = []

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    # x1 = ""
    # regex = r"(?<=REMARKS\n)[\s\S]+(?=\n *DISCOUNT DETAILS)"
    # if data := re.search(regex, f):
    #     data = [re.split(r" {3,}", i)[-2:] for i in data.group().split('\n')]

    for i in data:
        tmp = {}
        for j, k in zip(["Details", "BillAmount", "DeductedAmt", "Discount", "PayableAmount", "DeductionReason"], i[2:]):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
