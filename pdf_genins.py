import random
import re
import sys


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
        'ClaimNo': [[r"(?<=Claim Control Number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Claim in respect of).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy Number).*(?=Reference)"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer Co.).*(?=Policy No)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=ID Card Number).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Primary Diagnosis).*(?=ICD Code)"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Cheque/DD No).*?(?=for)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?=dated).*?(?=towards)"], [':'], ""],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Amount claimed).*(?=ed)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Gross amount settled).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net amount paid).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[], [':'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS deducted).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[], [], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regex = r"(?<=DEDUCTION ::).*"
    data = re.findall(regex, f)
    data = [i.strip() for i in data]

    for j, i in enumerate(data):
        if tmp := re.search(r"(?P<deduction>\d+)(/-)(?P<reason>.*)", i):
            data[j] = tmp.groups()
    deductions = []
    for i in data:
        tmp = {}
        tmp["PayableAmount"], _, tmp["DeductionReason"] = i
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
