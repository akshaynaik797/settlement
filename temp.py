import mysql.connector
from common import update_date_utr_nic_city, conn_data

q = "select unique_key from stgSettlement where InsurerID='newindia' and UTRNo='';"

with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q)
    r = cur.fetchall()
    for i in r:
        update_date_utr_nic_city(i[0])