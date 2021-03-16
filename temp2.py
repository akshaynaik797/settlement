import os

import mysql.connector

from backend import conn_data

with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    q = "select sno, attach_path from settlement_mails"
    cur.execute(q)
    r = cur.fetchall()
    for sno, attach_path in r:
        if not os.path.exists(attach_path):
            q = "update settlement_mails set completed='NF' where sno=%s"
            cur.execute(q, (sno,))
    con.commit()
