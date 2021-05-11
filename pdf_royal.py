import random
import sys
import re

from backend import mark_flag
from common import get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    regex_dict = {
        'ClaimNo': [[r"(?<=Settlement of claim number:).*"], [':'], r"^\S+$"],
        'POLICYNO': [[r"(?<=Policy Number).*(?=Patient Name)"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=Transaction Refernce number:).*(?=towards)"], [':'], r"^\S+$"],
        'Transactiondate': [[r"\S*(?=vide\n*Transaction Refernce number)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Billed Amount).*"], [':', 'Rs', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount Paid).*(?=\()"], [':', 'Rs', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=Period of Hospitalization:).*(?=to)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"\S+(?=\n*We are pleased to inform)"], [':'], r"^\S+(?: \S+)*$"],
        'Discount': [[r"(?<=Discount).*"], [':', 'Rs', '/-'], r"^\d+(?:\.\d+)*$"],
        'TDS': [[r"(?<=TDS).*"], [':', 'Rs', '/-'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
    mark_flag('X', sys.argv[2])
except:
    log_exceptions()
    pass
