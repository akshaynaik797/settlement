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
    data_dict = get_data_dict(regex_dict, f)
    data_dict['unique_key'] = data_dict['ClaimNo']
    ins_upd_data(mail_id, hospital, data_dict)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
