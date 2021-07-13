import random
import re
import sys

import camelot

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    # stg_sett_fields = (
    #     "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    #     "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    #     "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    #     "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim Number).*"], [':'], r"^\S+$"],
        'ALNO': [[r"(?<=Preauthorization Approval Number).*"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy Number).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharege).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer).*(?=Carporate)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Patient’s Member UHID).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Treatment).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Neft/Cheque number).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Neft/Cheque Date).*(?=Neft)"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Billed Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Approved Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Amount Paid).*(?=\(Rupees)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    r1 = r"(?<=Discount Amount\n) *\w+ *(?P<Transactiondate>\S+) *(?P<BilledAmount>\S+) *(?P<Discount>\S+) *(?P<SettledAmount>\S+)"
    if tmp := re.search(r1, f):
        tmp = tmp.groupdict()
    r2 = r"(?<=Payment Acct. No.\n) *(?P<NetPayable>\S+) *(?P<TDS>\S+) *(?P<UTRNo>\S+(?=;))\S+ *(?P<AccountNo>\w+)"
    if tmp1 := re.search(r2, f):
        tmp1 = tmp1.groupdict()
    tmp = {**tmp, **tmp1}
    tmp = {i: j.replace(',', '') for i, j in tmp.items()}
    datadict = {**tmp, **datadict}
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]
    datadict['InsurerID'] = datadict['TPAID']

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regex = r"(?<=Disallowance Reason\n)[\s\S]+(?=\n *Total)"
    if data := re.search(regex, f):
        data = [re.split(r" {3,}", i) for i in data.group().split('\n')]

    deductions = []
    for i in data:
        tmp = {}
        if len(i) == 5:
            for j, k in zip(["Details", "BillAmount", "DeductedAmt", "PayableAmount", "DeductionReason"], i):
                tmp[j] = k
        if len(i) == 3:
            for j, k in zip(["Details", "DeductedAmt", "DeductionReason"], i):
                tmp[j] = k

        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
