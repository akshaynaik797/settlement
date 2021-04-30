import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=CCN No).? *:? *\S+"], [':', '(', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Name of the Patient).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No.).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=Insurer UTR No).*", r"(?<=Insurer\n).*(?=\n.*UTR)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"\S+(?=\n *Hospital)"], [':'], r"^\w+(?:[\/ -]?\w+){0,2}$"],
        'BilledAmount': [[r"(?<=Amount Claimed).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Claim Amt Settled).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount Paid).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Name of Insurance co.).*(?=.)"], [':'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Member PHS ID)(?: *:? *)\S+"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=treatment of).*(?=at)"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=TDS Deduction).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Copay).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    x1 = ""
    regexes = r"(?<=Reason for Deduction\n)[\s\S]*(?=\n *Total *\d)", r""
    for regex in regexes:
        x = re.search(regex, f)
        if x:
            x1 = x.group().strip()
            break

    table = []
    for i in x1.split('\n'):
        regex = re.compile(r" {3,}")
        t1 = [i.strip() for i in regex.split(i)]
        while len(t1) < 6:
            t1.append("")
        table.append(t1)



    deductions = []
    for row in table:
        tmp = {}
        tmp["Details"], tmp["BillAmount"], tmp["DeductedAmt"], tmp["DeductionReason"] = row[2:]
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)


    ins_upd_data(mail_id, hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
