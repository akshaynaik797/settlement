import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim No).*(?=AL)"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Name of the Patient :).*(?=Policy)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No :).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=ref. no.).*(?=dated)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*(?=towards)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Requested Amount i! n Rs).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Final Amount Settled in Rs.).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=an amount of Rs.) *\d+(?=.)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date Of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date Of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Name of Insurance co.).*(?=.)"], [':'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=UHID NO :).*(?=Relationship)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r".*(?=\s*Diagnosis)", r"(?<=Diagnosis :).*"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=TDS is) *\d+(?=.)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    ins_upd_data(mail_id, hospital, datadict, [])
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
