from common import update_date_utr_nic_city, conn_data
import mysql.connector

q = "select unique_key from stgSettlement where UTRNo = '' and unique_key like '%,%'"
with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q)
    r = cur.fetchall()
    for unique_key in r:
        update_date_utr_nic_city(unique_key[0])