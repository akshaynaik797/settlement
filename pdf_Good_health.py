import random
import re
import sys

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=CCN).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Patient)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*(?=Agent)"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=NEFT is).*?(?=from)"], [':', 'transaction', 'number', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=DATE).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Billed).*(?=Dis)", r"(?<=Billed).*"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Settled).*(?=Less)", r"(?<=settled for).*(?=\/-)"], [':', 'Rs.', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Settled Amount).*"], [':', 'Rs.', '/-', ','], r"^\d+(?:\.\d+)*$"],
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
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    deductions = []
    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
