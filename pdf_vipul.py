import random
import re
import sys

import camelot
import openpyxl

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    # tables = camelot.read_pdf(sys.argv[1], pages='all')
    # flag = None
    # if tables.n > 0:
    #     tables.export('temp_files/foo1.xlsx', f='excel')
    #     flag = True
    # if flag:
    #     wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
    #     sheet = wb.worksheets[-1]
    #     data = []
    #     for row in sheet.rows:
    #         tmp = [i.value for i in row]
    #         data.append(tmp)
    #     data = data[3:]
    #     data = [["" if j is None else j for j in i] for i in data]

    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=File No).*"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Admin)"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Admin Date).*(?=Emp)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Dis Date).*(?=File)"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurance Company).*"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*(?=Payee)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Final Diagnosis).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=UTR/Cheque No).*(?=dated)"], [':', '.', 'NEFT-'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*(?=\.)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Beneficiary Acc No).*(?=UTR)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Approval Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Total Approved).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=payment of).*(?=vide EFT No)"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Total Co-pay Amt.).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount allowed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    regex = r"(\d+) +(?P<BilledAmount>\d+) +(\d+) +(?P<Copay>\d+) +(\d+) +(\d+) +(?P<Discount>\d+) +(?P<SettledAmount>\d+) +(?P<TDS>\d+) +(?P<NetPayable>\d+)"
    if tmp := re.search(regex, f):
        tmp = tmp.groupdict()
        datadict = {**tmp, **datadict}
    if 'UTRNo' not in datadict:
        regex = r"(?<=Cheque No:).*?(?=dated)"
        if tmp := re.search(regex, f, re.DOTALL):
            datadict['UTRNo'] = tmp.group().strip()
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]

    deductions = []

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    # x1 = ""
    # regex = r"(?<=REMARKS\n)[\s\S]+(?=\n *DISCOUNT DETAILS)"
    # if data := re.search(regex, f):
    #     data = [re.split(r" {3,}", i)[-2:] for i in data.group().split('\n')]

    # for i in data:
    #     tmp = {}
    #     for j, k in zip(["Details", "DeductedAmt", "DeductionReason"], i[1:]):
    #         tmp[j] = k
    #     tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
    #     tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
    #     deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
