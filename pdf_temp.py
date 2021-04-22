import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ALNO': [[r"(?<=Claim ID).*"], [':'], r"^\S+$"],
        'ClaimNo': [[r"(?<=Claim ID).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Claim Of).*(?=Insured)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*(?=Card)"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=NEFT transaction number\n).*(?=dated)"], [':'], r"^\S+$"],
        'Transactiondate': [[r"(?<=dated).*"], [':'], ""],
        'BilledAmount': [[r"(?<=Billed).*(?=Dis)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Settled).*(?=Less)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Paid Amount).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ClaimNo']
    datadict['InsurerID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    ins_upd_data(mail_id, hospital, datadict)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
