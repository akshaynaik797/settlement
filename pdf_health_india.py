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
        'POLICYNO': [[r"(?<=Policy Number).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission -\n).*(?=-)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=-).*(?=\n *Discharge)"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurance Company).*"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate/Retail).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=I-Card No).*(?=Relation)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Ailment).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=UTR No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=UTR Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Claim Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Approved Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=NEFT/Paid Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[], [':'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[], [], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regex = r"\d+ {4,}\d+(?:\/\d+)+ *(\d+) *(\d+) *(\d+) *(.*)"
    data = re.findall(regex, f)

    deductions = []
    for i in data:
        tmp = {}
        for j, k in zip(["BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason"], i):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
