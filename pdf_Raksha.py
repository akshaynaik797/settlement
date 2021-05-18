import random
import re
import sys

import camelot
import openpyxl

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data
from make_log import log_exceptions

try:
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])
    if 'details of Electronic Fund transfer processed' in f:
        # tables = camelot.read_pdf(sys.argv[1], pages='all')
        # flag = None
        # if tables.n > 0:
        #     tables.export('temp_files/foo1.xlsx', f='excel')
        #     flag = True
        # if flag:
        #     wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
        #     sheet = wb.worksheets[-1]
        #     data = []
        #     for row in sheet.rows:
        #         tmp = [i.value for i in row]
        #         data.append(tmp)
        #     data = data[3:]
        #     data = [["" if j is None else j for j in i] for i in data]
        #     data = [[str(j).replace('\n', ' ').replace('\t', ' ') for j in i[2:]] for i in data]
        #     for i in data:
        #         datadict = {}
        #         datadict['ClaimNo'], datadict['NetPayable'] = i[2].split(' ')
        #         datadict['UTRNo'] = i[-2].split(' ')[0]
        #         if 'ClaimNo' not in datadict:
        #             datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
        #         datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
        #         datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
        #         ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
        #         mark_flag('X', sys.argv[2])
        if tmp := re.search(r"(?<=Date\n).*(?=\nRegards)", f, re.DOTALL):
            data = [re.split(r" +", i) for i in tmp.group().split('\n')]
            for j, i in enumerate(data):
                if len(i) > 10:
                    alpha_num, nums = [], []
                    for k in i:
                        if re.match(r"^(?!(?:[0-9]*|[a-zA-Z]*)$)[a-zA-Z0-9]+$", k):
                            alpha_num.append(k)
                        if re.match(r"^\d+(?:\.\d+)*$", k):
                            nums.append(k)
                    datadict = {}
                    _, datadict['ClaimNo'], datadict['NetPayable'], datadict['TDS'] = nums
                    datadict['UTRNo'] = alpha_num[-1]
                    if 'ClaimNo' not in datadict:
                        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
                    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
                    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
                    datadict['file_name'] = sys.argv[0]
                    pass
                    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
        mark_flag('X', sys.argv[2])
        exit()
    tables = camelot.read_pdf(sys.argv[1], pages='all')
    flag = None
    if tables.n > 0:
        tables.export('temp_files/foo1.xlsx', f='excel')
        flag = True
    if flag:
        wb = openpyxl.load_workbook('temp_files/foo1.xlsx')
        sheet = wb.worksheets[-1]
        data = []
        for row in sheet.rows:
            tmp = [i.value for i in row]
            data.append(tmp)
        data = data[2:]
        data = [["" if j is None else j for j in i] for i in data]


    # stg_sett_fields = (
    #     "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    #     "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    #     "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    #     "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")

    regex_dict = {
        'ClaimNo': [[r"(?<=Claim No).*(?=Insurance)", r"(?<=Claim No).*(?=Member)"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Claimant/Patient).*(?=Corporate)"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy Number).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=DOA).*(?=DOD)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=DOD).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=policy issued by).*(?=has been)"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Proposer Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=Member Id).*(?=Policy)"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Diagnosis of).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=Neft-Ref/Cheque No).*(?=Payment)", r"(?<=Neft-Ref/Cheque No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=Neft-Ref/Cheque Date).*(?=Diagnosis)", r"(?<=Neft-Ref/Cheque Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Bank Account No).*(?=on)"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Beneficiary Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Claim Amount).*(?=Deduction)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=Net Payable Amount).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=Net Payable Amount).*", r"(?<=Net Payable Amount).*(?=Neft)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS Amt).*(?=Final)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount Amt).*"], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    if 'ClaimNo' not in datadict:
        datadict['ClaimNo'] = 'not_found_' + str(random.randint(9999999, 999999999))
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
    datadict['file_name'] = sys.argv[0]

    deductions = []

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    # x1 = ""
    # regex = r"(?<=REMARKS\n)[\s\S]+(?=\n *DISCOUNT DETAILS)"
    # if data := re.search(regex, f):
    #     data = [re.split(r" {3,}", i)[-2:] for i in data.group().split('\n')]

    for i in data:
        tmp = {}
        for j, k in zip(["Details", "BillAmount", "DeductedAmt", "PayableAmount", "DeductionReason"], i[1:]):
            tmp[j] = k
        tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
        tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
        deductions.append(tmp)

    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
