import random
import re
import sys

import camelot
from tabula import read_pdf

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    # stg_sett_fields = (
    #     "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    #     "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    #     "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    #     "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")

    regex_dict = {
        'ClaimNo': [[r"(?<=Ref No).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=for the period from).*(?=to)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=to) *\d+(?:/\d+)+"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=policy issued by).*(?=has been)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Proposer Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Card No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=treatment of).*(?=at)"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=ECS/ NEFT).*(?=in your)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=on).*(?=against)", r"(?<=Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Bank Account No).*(?=on)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Beneficiary Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Amount claimed for).*(?=towards)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=has been settled for).*(?=\(RUPEES)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=has been settled for).*(?=\(RUPEES)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS Amt).*(?=Final)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount Amt).*"], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    deductions = []
    df = read_pdf(sys.argv[1], pages="all")[-1]
    tmp = list(df)
    if 'Reason' in tmp:
        for index, row in df.iterrows():
            tmp = {}
            row = row.tolist()
            tmp["Details"], tmp["DeductedAmt"], tmp["DeductionReason"], _ = row
            tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
            tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
            deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
