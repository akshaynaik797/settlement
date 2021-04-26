import re
import sys


from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    f = f.replace('***', '')
    regex_dict = {
        'ClaimNo': [[r"(?<=Claim Number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No :).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=UTR No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Approval Date).*"], [':'], ""],
        'BilledAmount': [[r"(?<=Bill Amount).*(?=\nPaid Amount)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Bill Amount).*(?=\nPaid Amount)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Paid Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date Of Admission).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date Of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Name of Insurance co.).*(?=.)"], [':'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=ID Card No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r".*(?=\s*Diagnosis)", r"(?<=Diagnosis :).*"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    x1 = ""
    regexe = r"\w+(?: ?\w+) +\d+ + \d+ +\d+.*"
    data = re.findall(regexe, f)
    for i, j in enumerate(data):
        j = re.compile(r" {5,}").split(j)
        data[i] = j

    for i, j in enumerate(data):
        while len(j) < 5:
            j.append("")
        data[i] = j

    deductions = []
    for i in data:
        tmp = {}
        for j, k in zip(["Details", "BillAmount", "DeductedAmt", "PayableAmount", "DeductionReason"], i):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
