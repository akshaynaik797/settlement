import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=Cashless Claim Reference Number).*(?=\))"], [':', '('], r"^\S+$"],
        'PatientName': [[r"(?<=Claim Of).*(?=Insured)", r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No.).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=UTR Number).*"], [':'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Settlement Date).*(?=00)"], [':'], ""],
        'BilledAmount': [[r"(?<=Total) *\d+"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Settled Amount \(INR\)).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Settled Amount \(INR\)).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=issued by).*(?=has)"], [], r"^.*$"],
        'CorporateName': [[r"(?<=Policy Holder).*"], [], r"^.*$"],
        'MemberID': [[r"(?<=Insurer Member ID).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Diagnosis).*"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=Tax Deducted at Source).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Copay).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    x1 = ""
    regexes = r"(?<=Non-Payment\n)[\s\S]*(?=\n *Total)", r""
    for regex in regexes:
        x = re.search(regex, f)
        if x:
            x1 = x.group().strip()
            break

    stg_sett_deduct_fields = (
        "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
        "Discount", "DeductionCategory", "MailID", "HospitalID")

    table = []
    for i in x1.split('\n'):
        regex = re.compile(r" {3,}")
        t1 = [i.strip() for i in regex.split(i)]
        while len(t1) < 5:
            t1.append("")
        table.append(t1)



    deductions = []
    for row in table:
        tmp = {}
        tmp["Details"], tmp["BillAmount"], tmp["PayableAmount"], tmp["DeductedAmt"], tmp["DeductionReason"] = row
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)


    ins_upd_data(mail_id, hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
