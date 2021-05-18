import random
import re
import sys

import mysql.connector
import pandas as pd

from backend import mark_flag
from common import get_row, ins_upd_data, conn_data, ins_upd_data_excel
from make_log import log_exceptions
try:
    _, file_path, mid, _ = sys.argv
    row_data = get_row(mid)
    mail_id, hospital = row_data['id'], row_data['hospital']

    df = pd.read_html(file_path)[0]
    data = []

    for index, row in df.iterrows():
        temp = [cell for cell in row]
        data.append(temp)


    sh1_fields = [('ALNO', ['Remarks']), ('ClaimNo', ['Settlement No']), ('POLICYNO', ['Policy No']),
                  ('PatientName', ['Claimant Name']), ('InsurerID', ['Tpa Branch Name']),
                  ('AccountNo', ['Payee Bank Acc No']), ('UTRNo', ['Utr No', 'UTR Number']), ('SettledAmount', ['GrossPaidAmount']),
                  ('TDS', ['TDS']), ('NetPayable', ['Net Paid Amount', 'Net Amount']), ('Transactiondate', ['Payment Date', 'Settlement Date'])]

    temp = {}
    for j, i in enumerate(data[0]):
        for k, v in sh1_fields:
            for m in v:
                if m in i:
                    t_list = []
                    for n in range(1, len(data)):
                        t_list.append(str(data[n][j]))
                    temp[k] = t_list
                    break

    table = []
    for i in temp:
        for j in temp[i]:
            table.append({})
        break

    for i, j in enumerate(table):
        for k in temp:
            table[i][k] = temp[k][i]


    for datadict in table:
        if 'ALNO' in datadict:
            datadict['ALNO'] = datadict['ALNO'].strip('-')
            for i in ['MD', 'Medi', 'United']:
                if i in datadict['InsurerID']:
                    datadict['ALNO'] = datadict['ALNO'].split("-")[0]
            if 'Heritage' in datadict['InsurerID']:
                datadict['ALNO'] = datadict['ALNO'].strip('CL').strip('00')
            if 'Family' in datadict['InsurerID']:
                datadict['ALNO'] = datadict['ALNO'][1:].split('/')[0]
            if 'Ericson' in datadict['InsurerID']:
                tmp = re.findall(r"\d+", datadict['ALNO'])
                if len(tmp) > 0:
                    datadict['ALNO'] = tmp[0]
            if datadict['ALNO'] == '':
                datadict['ALNO'] = 'not_found_' + str(random.randint(9999999, 999999999))

        else:
            datadict['ALNO'] = 'not_found_' + str(random.randint(9999999, 999999999))
        if 'Paramount' in datadict['InsurerID']:
            tmp = re.findall(r"\d+", datadict['ALNO'])
            if len(tmp) > 0:
                datadict['MemberID'] = tmp[0]
                datadict['ALNO'] = 'not_found_' + str(random.randint(9999999, 999999999))
        datadict['unique_key'] = datadict['ALNO']
        datadict['TPAID'] = re.compile(r"(?<=pdf_).*(?=.py)").search(sys.argv[0]).group()
        datadict['file_name'] = sys.argv[0]
        datadict['UTRNo'] = '' if datadict['UTRNo'] == 'nan' else datadict['UTRNo']
        deductions = []
        q = "select * from stgSettlement where ALNO=%s and UTRNo=%s limit 1"
        params = [datadict['ALNO'], datadict['UTRNo']]
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            cur.execute(q, params)
            r = cur.fetchone()
            if r is None:
                ins_upd_data_excel(mail_id, sys.argv[3], hospital, datadict)
    mark_flag('X', sys.argv[2])
except:
    log_exceptions()
    pass