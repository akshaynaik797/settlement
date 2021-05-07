from common import date_formatting, conn_data, get_row, move_attachment
import mysql.connector

q = "select ALNO, mail_id from stgSettlement"
with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q)
    r = cur.fetchall()
    for alno, mail_id in r:
        attach_path = get_row(mail_id)['attach_path']
        move_attachment(alno, attach_path, 'noble')