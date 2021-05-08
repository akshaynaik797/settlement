from common import date_formatting, conn_data, get_row, move_attachment
import mysql.connector

from make_log import log_exceptions

q = "select ALNO, ClaimNo, mail_id from stgSettlement where attachment is null"
# q = "select ALNO, ClaimNo, mail_id from stgSettlement where mail_id='17153a11c4f2d105'"
with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q)
    r = cur.fetchall()
    for alno, claimno, mail_id in r:
        try:
            if alno == '':
                alno = claimno
            attach_path = get_row(mail_id)['attach_path']
            move_attachment(alno, attach_path, 'noble')
        except:
            log_exceptions(mail_id=mail_id)