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
        'ClaimNo': [[r"(?<=Claim Number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy Number).*(?=Reference)"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer Co.).*(?=Policy No)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=ID Card Number).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Primary Diagnosis).*(?=ICD Code)"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Reference/UTR No).*", r"(?<=Payment Reference No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Date).*"], [':'], ""],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Bill Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Approved Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Approved Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[], [':'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[], [], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    # try:
    #     datadict['NetPayable'] = float(datadict['NetPayable']) - float(datadict['TDS'])
    # except:
    #     datadict['NetPayable'] = ""
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regex = r"(?<=Disallowed Reason\n)[\s\S]+(?=\nDiscount Deduction)"
    if data := re.search(regex, f):
        data = data.group().split('\n')
        for i, j in enumerate(data):
            data[i] = re.split(r" {3,}", j)
    else:
        data = []

    deductions = []
    try:
        for i in data:
            tmp = {}
            tmp["Details"], _, tmp["BillAmount"], tmp["DeductedAmt"], tmp["PayableAmount"], tmp["DeductionReason"] = i
            tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
            tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
            deductions.append(tmp)
    except:
        pass
    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
