import mysql.connector

from backend import conn_data


# INSERT INTO stgSettlement (unique_key, tpaid, alno)
# VALUES (1, "AS", "19")
# ON DUPLICATE KEY UPDATE
# tpaid="AS", alno="19";

q = "insert into stgSettlement (`InsurerID`, `TPAID`, `ALNO`, `ClaimNo`, `PatientName`, `AccountNo`, " \
            "`BeneficiaryBank_Name`, `UTRNo`, `BilledAmount`, `SettledAmount`, `TDS`, `NetPayable`," \
            " `Transactiondate`, `DateofAdmission`, `DateofDischarge`, `unique_key`, `mail_id`, `hospital`) "
q = q + ' values (' + ('%s, ' * q.count(',')) + '%s) '
q1 = "ON DUPLICATE KEY UPDATE `InsurerID`=%s, `TPAID`=%s, `ALNO`=%s, `ClaimNo`=%s, `PatientName`=%s, " \
     "`AccountNo`=%s, `BeneficiaryBank_Name`=%s, `UTRNo`=%s, `BilledAmount`=%s, `SettledAmount`=%s, `TDS`=%s, " \
     "`NetPayable`=%s, `Transactiondate`=%s, `DateofAdmission`=%s, `DateofDischarge`=%s, `cdate`=%s, " \
     "`processing_time`=%s, `mail_id`=%s, `hospital`=%s"
q = q + q1

with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    cur.execute(q)
    r = cur.fetchone()
    if r is not None:
        utr, date = r
pass