import os
import re
import shutil
import sys

import camelot
import openpyxl
import pandas as pd
import mysql.connector
import xlrd

from common import mark_flag, get_from_db_and_pdf, get_data_dict, ins_upd_data, get_row, conn_data
from make_log import log_exceptions

try:
    if '.xls' in sys.argv[1]:
        row_data = get_row(sys.argv[2])
        mail_id, hospital = row_data['id'], row_data['hospital']
        fields = ['SRNO', 'CCN', 'TOTALSETTLED', 'CHEQUEDATE', 'DOA', 'DOD', 'IPNAME', 'HOSPNAME', 'HOSP_CITY', 'LODGEAMT', 'DED_AMT', 'PROVIDER_CODE', 'TDS_AMT', 'STAMT', 'CHEQUENO', 'ded', 'ICCLAIMNUMBER']
        book = xlrd.open_workbook(sys.argv[1])
        sh = book.sheet_by_index(0)
        data = []
        for j, i in enumerate(sh):
            if j != 0:
                tmp = {i: j for i, j in zip(fields, [str(j.value) for j in i])}
                with mysql.connector.connect(**conn_data) as con:
                    cur = con.cursor()
                    q = "select ClaimNo from stgSettlement where ClaimNo=%s limit 1"
                    cur.execute(q, (tmp['CCN'],))
                    r = cur.fetchone()
                    if r is None:
                        datadict = {}
                        for k, v in [("UTRNo", 'CHEQUENO'), ("Transactiondate", 'CHEQUEDATE'), ("NetPayable", 'TOTALSETTLED'), ("TDS", 'TDS_AMT')]:
                            datadict[k] = tmp[v]
                        datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo'] = tmp['CCN']
                        datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
                        ins_upd_data(mail_id, sys.argv[3], hospital, datadict, [])
        mark_flag('X', sys.argv[2])
        exit()
    mail_id, hospital, f = get_from_db_and_pdf(sys.argv[2], sys.argv[1])

    # stg_sett_fields = (
    #     "srno", "InsurerID", "TPAID", "ALNO", "ClaimNo", "PatientName", "AccountNo", "BeneficiaryBank_Name", "UTRNo",
    #     "BilledAmount", "SettledAmount", "TDS", "NetPayable", "Transactiondate", "DateofAdmission",
    #     "DateofDischarge", "cdate", "processing_time", "unique_key", "mail_id", "hospital", "POLICYNO",
    #     "CorporateName", "MemberID", "Diagnosis", "Discount", "Copay")


    regex_dict = {
        'ClaimNo': [[r"(?<=CCN).*(?=MD ID No)"], [':'], r"^\S+$"],
        'PatientName': [[r"(?<=Patient Name).*"], [':'], r"^\S+(?: \S+)*$"],
        'POLICYNO': [[r"(?<=Policy No).*"], [':', '.'], r"^\S+$"],
        'DateofAdmission': [[r"(?<=Date of Admission).*(?=Date)"], [':'], r"^\S+(?: \S+)*$"],
        'DateofDischarge': [[r"(?<=Date of Discharge).*"], [':'], r"^\S+(?: \S+)*$"],
        'InsurerID': [[r"(?<=Insurance Co).*"], [':', '.'], r"^.*$"],
        'CorporateName': [[r"(?<=Corporate Name).*"], [':'], r"^.*$"],
        'MemberID': [[r"(?<=MD ID No.).*"], ['.', ':'], r"^.*$"],
        'Diagnosis': [[r"(?<=Diagnosis).*"], [':'], r"^.*$"],

        'UTRNo': [[r"(?<=ECS Tran No).*", r"(?<=Cheque No).*"], [':', '.'], r"^\S+$"],
        'Transactiondate': [[r"(?<=ECS Tran Date).*"], [':'], r"^\d+(?:[\/ -]{1}\w+){2}$"],
        'AccountNo': [[r"(?<=Beneficiary A/C Number).*"], [':'], r"^\S+(?: \S+)*$"],
        'BeneficiaryBank_Name': [[r"(?<=Beneficiary Bank Name).*"], [':'], r"^\S+(?: \S+)*$"],

        'BilledAmount': [[r"(?<=Lodge Amt).*(?=Deduction)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'SettledAmount': [[r"(?<=NetPayable).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'NetPayable': [[r"(?<=NetPayable).*"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Copay': [[r"(?<=Co-payment).*"], [':', 'Rs'], r"^\S+(?: \S+)*$"],
        'TDS': [[r"(?<=TDS Amt).*(?=Final)"], [':', 'Rs.', 'INR', '/-', 'Rs'], r"^\d+(?:\.\d+)*$"],
        'Discount': [[r"(?<=Discount Amt).*"], ['Rs', ':'], r"^.*$"]
    }
    datadict = get_data_dict(regex_dict, f)
    datadict['unique_key'] = datadict['ALNO'] = datadict['ClaimNo']
    datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()

    # stg_sett_deduct_fields = (
    #     "TPAID", "ClaimID", "Details", "BillAmount", "PayableAmount", "DeductedAmt", "DeductionReason",
    #     "Discount", "DeductionCategory", "MailID", "HospitalID", "stgsettlement_sno")

    x1 = ""
    deductions = []
    regex = r"(?<=REMARKS\n)[\s\S]+(?=\n *DISCOUNT DETAILS)"
    if data := re.search(regex, f):
        data = [re.split(r" {3,}", i)[-2:] for i in data.group().split('\n')]
        for i in data:
            tmp = {}
            for j, k in zip(["DeductedAmt", "DeductionReason"], i):
                tmp[j] = k
            tmp["MailID"], tmp["HospitalID"] = mail_id, hospital
            tmp["TPAID"], tmp["ClaimID"] = datadict["TPAID"], datadict["ClaimNo"]
            deductions.append(tmp)
    ins_upd_data(mail_id, sys.argv[3], hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except Exception:
    log_exceptions()
