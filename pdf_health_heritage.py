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
        'ClaimNo': [[r"(?<=CCN).*(?=\))"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Age)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=DOA).*(?=DOD)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=DOD).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer Co.).*(?=Policy No)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=I-Card No).*(?=Relation)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Primary Diagnosis).*(?=ICD Code)"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=NEFT No).*(?=Date)", r"(?<=NEFT No).*?(?=Â)", r"(?<=NEFT No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Date of Transfer).*(?=Settled)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Amount Claimed).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Settled Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Amount).*", r"(?<=Amount:Â).*(?=In Favour)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[], [':'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS Deducted).*(?=Deducted)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[], [], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regex = r"(?<=Details of deductions:\n)[\s\S]*(?=\n.*MOU Discount)"
    if data := re.search(regex, f):
        data = data.group().strip().split('\n')
    else:
        data = []


    for j, i in enumerate(data):
        if tmp := re.search(r"((?<=Rs.) *\d+(?:.?\d+) )(.*)", i):
            data[j] = tmp.groups()
    deductions = []
    for i in data:
        tmp = {}
        tmp["DeductedAmt"], tmp["DeductionReason"] = i
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
