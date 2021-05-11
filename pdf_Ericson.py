import random
import re
import sys


from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    regex_dict = {
        'ClaimNo': [[r"(?<=Claim ID).*(?=InstNo)"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'UTRNo': [[r"(?<=UTR No).*(?=Dated)"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Dated:).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'BilledAmount': [[r"(?<=Cheque Amount).*(?=UTR No)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Cheque Amount).*(?=UTR No)"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Bill).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"],
        'DateofAdmission': [[r"(?<=D. O. A.).*"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*(?=D. O. A.)"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurer Co.).*(?=Policy No)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Group Name).*(?=Date)"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Card No).*(?=Patient)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Primary Diagnosis).*(?=ICD Code)"], [':'], r"^.*$"],
        'Discount': [[], [], r"^.*$"],
        'TDS': [[r"(?<=TDS Amount).*"], [':', 'Rs.', 'INR', '/-'], r"^\d+(?:\.\d+)*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    try:
        datadict['NetPayable'] = float(datadict['NetPayable']) - float(datadict['TDS'])
    except:
        datadict['NetPayable'] = ""
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    regexe = r".*\n +\d \w+.*"
    data = re.findall(regexe, f)
    for i, j in enumerate(data):
        j = re.compile(r" {9,}").split(j)
        data[i] = j

    for i, j in enumerate(data):
        while len(j) < 4:
            j.append("")
        data[i] = j

    deductions = []
    for i in data:
        tmp = {}
        for j, k in zip(["Details", "BillAmount", "PayableAmount", "DeductedAmt"], i):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
