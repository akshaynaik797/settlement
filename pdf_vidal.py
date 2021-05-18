import random
import re
import sys
import math

import camelot
import openpyxl
import tabula

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim No).*(?=Claim)"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Claimant Name).*"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=DOA) *:? *\w+(?:/\w+)+"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=DOD) *:? *\w+(?:/\w+)+"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurance Company).*"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*(?=Payee)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Enrollment No).*(?=Relationship)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Final Diagnosis).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=EFT No).*(?=dated)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*(?=to the provided)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
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
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    deductions = []
    # df = tabula.read_pdf(sys.argv[1], pages="all")[0]
    # df = df[2:]
    # tmp = list(df)
    # if 'Amt Claimed' in tmp:
    #     for index, row in df.iterrows():
    #         tmp = {}
    #         row = row.tolist()
    #         tmp_flag = True
    #         for i in row:
    #             if isinstance(i, float):
    #                 if math.isnan(i):
    #                     tmp_flag = False
    #                     break
    #         if tmp_flag:
                # tmp["Details"], tmp["BillAmount"], tmp["DeductedAmt"], tmp["PayableAmount"], tmp[
                #     "DeductionReason"] = row
                # tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
                # tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
                # deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
