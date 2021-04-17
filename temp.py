import mysql.connector

from backend import conn_data
mid = 'AAMkAGMxMzcwMjVlLThjYjYtNGJlOC1iOWQzLTUzZjg5MTEwOTJiZABGAAAAAABg8S9egpbpQom_SYSQFJTABwA80npqDluGRIdxtgeTfSBNAAAAAAEMAAA80npqDluGRIdxtgeTfSBNAAKzTHxjAAA='
utr, date = "", ""
q = "select utr, `date` from ins_big_utr_date where id=%s limit 1"
with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q, (mid,))
    r = cur.fetchone()
    if r is not None:
        utr, date = r
pass