import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=Claim ID).*", r"(?<=Claim Number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Claim Of).*(?=Insured)", r"(?<=Patient Name).*", r"(?<=Claim Of).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*(?=Card)", r"(?<=Policy Number).*", r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=NEFT)[\s\S]*?(?=dated)"], [':', 'transaction', 'number', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*?(?=towards)", r"(?<=dated\n)\S+", r"(?<=dated).*", r"(?<=dated).*(?=\.)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Billed).*(?=Dis)", r"(?<=Billed).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Settled).*(?=Less)", r"(?<=settled for).*(?=\/-)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Paid Amount).*", r"(?<=Net Settled Amount after TDS).*", r"(?<=Net Paid Amount).*", r"(?<=settled for).*(?=\()", r"(?<=Net Paid Amount).*(?=For)"], [':', 'Rs.', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=issued by).*(?=has)"], [], r"^.*$"],
        'CorporateName': [[], [], r"^.*$"],
        'MemberID': [[r"(?<=Card No).*", r"(?<=Member ID Number).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Diagnosis).*"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=Less TDS).*", r"(?<=Less TDS).*(?=Co-Payment)"], [':', 'Rs.', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-Payment Amount).*"], [], []]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    x1 = ""
    regexes = r'(?<=Disallowance Reasons:)[\s\S]*(?=Claimed)', r"(?<=Deduction Reason\n)[\s\S]+(?=This)"
    for regex in regexes:
        x = re.search(regex, f)
        if x:
            x1 = x.group().strip()
            break

    regex = '(?<=Rs.)\d+'
    amounts = re.findall(regex, x1, re.MULTILINE)

    reasons, details = [], []
    for i in x1.split('\n'):
        regex = re.compile(r"Rs.\S+")
        if regex.search(i):
            tmp = [i.strip() for i in regex.split(i)]
            reasons.append(tmp[-1])
            if len(tmp) > 1:
                details.append(tmp[0])
            else:
                details.append("")


    deductions = []
    for i, j, k in zip(amounts, reasons, details):
        tmp = {}
        tmp["DeductedAmt"], tmp["DeductionReason"], tmp["Details"] = i, j, k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)


    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
