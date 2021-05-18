import random
import re
import sys

import camelot
from tabula import read_pdf

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=Settlement of claim number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*(?=Hospital)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy Number).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Period of Hospitalization).*(?=to)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=to).*(?=Patient’s Member UHID)"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer).*(?=Carporate)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Patient’s Member UHID).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Diagnosis).*(?=Policy)"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Neft/Cheque number).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Neft/Cheque Date).*(?=Neft)", r"(?<=Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Billed Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Approved Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount Paid).*(?=\(Rupees)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount).*"], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    deductions = []
    df = read_pdf(sys.argv[1], pages="all")[-1]
    tmp = list(df)
    if 'Reason' in tmp:
        for index, row in df.iterrows():
            try:
                tmp = {}
                record = row.tolist()
                tmp["Details"], tmp["BillAmount"], tmp["PayableAmount"], tmp["DeductedAmt"], tmp[
                    "DeductionReason"] = record[0], record[2].split(' ')[0], record[2].split(' ')[1], record[3], record[4]
                tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
                tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
                deductions.append(tmp)
            except:
                pass

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
