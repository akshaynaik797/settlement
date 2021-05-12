import random
import re
import sys

import camelot
import openpyxl

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim ID).*(?=Safeway)"], [':', '.'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient).*"], [':', '"'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Loc No).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Ailment).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=NEFT No).*(?=Payment)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Payment Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Account No).*(?=with)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=with).*(?=and IFSC Code)"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Claimed Amount).*(?=Cashless)"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Approved Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-Payment).*(?=Bank)"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS Amount).*(?=Net)"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Deduction).*(?=Co)"], [':', 'Rs.', 'INR', '/-', 'Rs', ',', '(', ')'], r"^\d+(?:\.\d+)*$"]
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
