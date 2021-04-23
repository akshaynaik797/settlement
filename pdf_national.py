import re
import sys

import openpyxl
import pandas as pd

from backend import mark_flag
from common import get_row, ins_upd_data
from make_log import log_exceptions
from movemaster import move_master_to_master_insurer
try:
    _, file_path, mid = sys.argv
    row_data = get_row(mid)
    mail_id, hospital = row_data['id'], row_data['hospital']

    df = pd.read_html(file_path)[0]
    data = []

    for index, row in df.iterrows():
        temp = [cell for cell in row]
        data.append(temp)


    sh1_fields = [('ALNO', 'Remarks'), ('ClaimNo', 'Settlement No'), ('POLICYNO', 'Policy No'),
                  ('PatientName', 'Claimant Name'), ('InsurerID', 'Tpa Branch Name'),
                  ('AccountNo', 'Payee Bank Acc No'), ('UTRNo', 'Utr No'), ('SettledAmount', 'GrossPaidAmount'),
                  ('TDS', 'TDS'), ('NetPayable', 'Net Paid Amount'), ('Transactiondate', 'Payment Date')]

    temp = {}
    for j, i in enumerate(data[0]):
        for field in sh1_fields:
            if field[1] in i:
                t_list = []
                for k in range(1, len(data)):
                    t_list.append(data[k][j])
                temp[field[0]] = t_list

    table = []
    for i in range(len(temp['ALNO'])):
        table.append({})

    for i, j in enumerate(table):
        for k in temp:
            table[i][k] = temp[k][i]


    for datadict in table:
        datadict['ALNO'] = datadict['ALNO'].replace('-', '')
        datadict['unique_key'] = datadict['ALNO']
        datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
        deductions = []
        ins_upd_data(mail_id, hospital, datadict, deductions)
    mark_flag('X', sys.argv[2])
except:
    log_exceptions()
    pass