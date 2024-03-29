import datetime
import re
import sys

import mysql.connector
import pdftotext
import tabula

from common import conn_data, mark_flag, get_row, date_formatting, move_attachment
from make_log import log_exceptions


try:
    sno = sys.argv[3]
    row_data = get_row(sys.argv[2])
    mail_id = row_data['id']
    mail_date = row_data['date']
    fpath = sys.argv[1]
    hospital = row_data['hospital']
    start = now = datetime.datetime.now()

    with mysql.connector.connect(**conn_data) as conn:
        cur = conn.cursor()
        file = sys.argv[1]
        table = tabula.read_pdf(file, lattice=True, pages='all', pandas_options={'header': None})
        print(table[0])
        df = table[0]
        print(df.columns)
        tempDic = {}
        for i in range(len(df)):
            key = df.loc[i, 0]
            value = df.loc[i, 1]
            tempDic[key] = value

        refrenceNo = tempDic["Transaction Reference no"]

        with open(sys.argv[1], "rb") as f:
            pdf = pdftotext.PDF(f)
        with open('temp_files/output.txt', 'w', encoding='utf-8') as f:
            f.write(" ".join(pdf))
        with open('temp_files/output.txt', 'r', encoding='utf-8') as myfile:
            f = myfile.read()

        temp = re.compile(r"(?<=Amount).*").search(f)
        if temp is None:
            amount = ""
        else:
            amount = temp.group().replace(',', "").strip()

        w = f.find("on") + len('on')
        k = f[w:]
        u = k.find(".") + w
        g = f[w:u]
        g = g.strip()
        g = g.replace(',', '')
        date_time_obj = datetime.datetime.strptime(g, '%d %b %Y')
        mdate = str(date_time_obj.strftime("%d-%m-%Y"))
        print('Date:', mdate)

        # query = """insert into NIC(TPA_Name,Transaction_Reference_No,Amount,Date_on_attachment) values \
        # 	('%s','%s','%s','%s')""" %(tempDic['TPA Name'],tempDic['Transaction Reference no'],tempDic['Amount'],mdate)

        query = """insert into NIC(TPA_Name,Transaction_Reference_No,Amount,Date_on_attachment,MailId,Date_Of_Mail,Amount_In_Mail, hospital) values \
            ('%s','%s','%s','%s','%s','%s','%s','%s')""" % (
        tempDic['TPA Name'], tempDic['Transaction Reference no'], tempDic['Amount'], mdate, mail_id, mail_date,
        amount, hospital)

        print(query)
        cur.execute(query)
        conn.commit()

        table = tabula.read_pdf(file, lattice=True, pages='all')
        # print(table[1])
        df = table[1]
        newcoldic = {}
        colList = []
        for col in df.columns:
            col1 = col.replace('\r', ' ')
            newcoldic[col] = col1
            colList.append(col1)

        df = table[1]
        df1 = df.rename(columns=newcoldic, inplace=False)
        print(df1.columns)
        for i in range(len(df1)):
            policyNo = df1.loc[i, "Policy Number"]
            claimNo = df1.loc[i, "Claim Number"]
            tpa = claimNo[0:5]
            patientName = df1.loc[i, "Name of Patient"]
            grossAmount = df1.loc[i, "Gross Amount"]
            tdsAmount = df1.loc[i, "TDS Amount"]
            netAmount = df1.loc[i, "Net Amount"]
            query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No, hospital) values \
            ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
            refrenceNo, policyNo, claimNo, patientName, grossAmount, tdsAmount, netAmount, tpa, hospital)
            print(query)
            cur.execute(query)
            conn.commit()

    if len(table) > 2:
        df = table[2]
    if len(table[2].columns) == len(table[1].columns):
        tempDic = {}
        tempDic1 = {}
        i = 0
        for col in df.columns:
            tempDic[colList[i]] = col
            tempDic1[col] = colList[i]
            i = i + 1
        df2 = df.rename(columns=tempDic1, inplace=False)
        df1 = df2.append(tempDic, ignore_index=True)
        print(df1)

        with mysql.connector.connect(**conn_data) as conn:
            cur = conn.cursor()
            for i in range(len(df1)):
                policyNo = df1.loc[i, "Policy Number"]
                claimNo = df1.loc[i, "Claim Number"]
                tpa = claimNo[0:5]
                patientName = df1.loc[i, "Name of Patient"]
                grossAmount = df1.loc[i, "Gross Amount"]
                tdsAmount = df1.loc[i, "TDS Amount"]
                netAmount = df1.loc[i, "Net Amount"]
                query = """insert into NIC_Records(Transaction_Reference_No,Policy_Number,Claim_Number,Name_Of_Patient,Gross_Amounts,tds,Net_Amount,tpa_No,hospital) values \
                ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
                refrenceNo, policyNo, claimNo, patientName, grossAmount, tdsAmount, netAmount, tpa, hospital)
                print(query)
                cur.execute(query)
                conn.commit()


    utrno, tran_date = "", ""
    temp_q = "select City_Transaction_Reference,Processing_Date from City_Records " \
             "where NIA_Transaction_Reference =%s"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(temp_q, (refrenceNo,))
        r = cur.fetchone()
        if r:
            utrno, tran_date = r

    q = "insert into stgSettlement " \
        "(`unique_key`, `InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, `AccountNo`, " \
        "`BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`," \
        " `Transactiondate`, `DateofAdmission`, `DateofDischarge`, `mail_id`, `hospital`, " \
        "`file_name`, `sett_table_sno`) "
    q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '

    tran_date = date_formatting(tran_date)
    params = [refrenceNo + ',' + claimNo, 'newindia', tpa, '', claimNo, patientName, '', '', utrno, '', grossAmount,
              tdsAmount, netAmount, tran_date, '', '', sys.argv[2], hospital, sys.argv[0], sno]

    for i, j in enumerate(params):
        try:
            params[i] = str(j)
        except:
            pass


    q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
         "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, `TDS`=%s," \
         "`NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, `mail_id`=%s, " \
         "`hospital`=%s, `file_name`=%s, `sett_table_sno`=%s"
    q = q + q1

    params = params + params[1:]

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        con.commit()

    move_attachment(claimNo, sys.argv[1], hospital)
    mark_flag('X', sys.argv[2])
    print("processed ", hospital, ' ', mail_id)
except:
    log_exceptions()
    pass
