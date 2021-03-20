from pathlib import Path
import os
from shutil import copyfile

import mysql.connector

from backend import conn_data

#'/home/ubuntu/index/index/13_03_2021/noble/letters/vidal_03052021162015/1628_PUN-0221-CH-0000024.pdf'

def get_ins_process(subject, email):
    ins, process = "", ""
    q1 = "select IC from email_ids where email_ids=%s limit 1"
    q2 = "select subject, table_name from email_master where ic_id=%s"
    q3 = "select IC_name from IC_name where IC=%s limit 1"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor(buffered=True)
        cur.execute(q1, (email,))
        result = cur.fetchone()
        if result is not None:
            ic_id = result[0]
            cur.execute(q2, (ic_id,))
            result = cur.fetchall()
            for sub, pro in result:
                if 'Intimation No' in subject:
                    return ('big', 'settlement')
                if 'STAR HEALTH AND ALLIED INSUR04239' in subject:
                    return ('small', 'settlement')
                if sub in subject:
                    cur.execute(q3, (ic_id,))
                    result1 = cur.fetchone()
                    if result1 is not None:
                        return (result1[0], pro)
    return ins, process

result = []

with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = "select * from python.settlement_mails where hospital='noble' and completed != 'NF' and attach_path not like '%letters%';"
    cur.execute(q)
    result = cur.fetchall()

for i in result:
    subject, email = i[1], i[6]
    path, sno = i[4], i[7]
    fname = os.path.split(path)[-1]
    ins, pro = get_ins_process(subject, email)
    if pro == 'settlement':
        folder = f'../index/19_03_2021/noble/letters/{ins}_03052021162015/'
        Path(folder).mkdir(parents=True, exist_ok=True)
        dst = os.path.join(folder, fname)
        copyfile(path, dst)
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            q = "update settlement_mails set attach_path=%s, completed='FIXED' where sno=%s;"
            cur.execute(q, (dst, sno))
            con.commit()
