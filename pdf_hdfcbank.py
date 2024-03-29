import random
import re
import sys

import camelot
import openpyxl

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    ins_list = [('STAR HEALTH AND ALLIED ', 'star'),
                ('HDFC ERGO GENERAL INSURANCE', 'hdfc'),
                ('Aditya Birla', 'aditya'),
                ('RELIANCE GENERAL', 'reliance'),
                ('THE ORIENTAL INSURANCE', 'oriental'),
                ('FUTURE GENERALI INDIA', 'fgh')]
    insurer = ""
    for i, j in ins_list:
        if i in f:
            insurer = j

    regex_dict = {
        'ClaimNo': [[r"(?<=Client Ref No).*", r"(?<=Claim No).*"], [':', '.', '|'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Main)"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=policy number).*(?=,)"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=From :).*(?=To)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=To :).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Ailment).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Chq /DD/Ft No) *:? *\S+", r"(?<=Bank Reference No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Account No).*(?=with)", r"(?<=Account Number).*(?=with)", r"(?<=Account Number).*(?=for)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Beneficiary Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Total amount claimed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount).*", r"(?<=Payment Details 6).*", r"(?<=Payment Details 7).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Total Co-pay Amt.).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS Amount).*", r"(?<=Payment Details 4).*", r"(?<=Payment Details 5).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount allowed).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"]
    }

    if insurer == 'reliance':
        regex_dict['ClaimNo'][0] = [r"(?<=Payment Details 7).*(?=-)"]
    if insurer == 'fgh':
        regex_dict['ClaimNo'][0] = [r"(?<=Details 1).*"]

    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]
    datadict['InsurerID'] = insurer
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
    #     for j, k in zip(["Details", "BillAmount", "DeductedAmt", "Discount", "PayableAmount", "DeductionReason"], i[2:]):
    #         tmp[j] = k
    #     tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
    #     tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
    #     deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
