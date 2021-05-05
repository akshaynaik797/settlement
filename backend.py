from distutils.dir_util import copy_tree, remove_tree
import zipfile
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from shutil import copyfile
import smtplib
from datetime import datetime, timedelta
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import re
import mysql.connector
import openpyxl

from common import conn_data, mark_flag
from movemaster import move_master_to_master_insurer
from make_log import log_exceptions


directory = 'backups'

inslist = ('all', 'aditya', 'apollo', 'bajaj', 'big', 'east_west', 'fgh', 'fhpl', 'Good_health', 'hdfc',
           'health_heritage', 'health_india', 'health_insurance', 'icici_lombard', 'MDINDIA', 'Medi_Assist',
           'Medsave', 'Paramount', 'Raksha', 'reliance', 'religare', 'small', 'united', 'Universal_Sompo',
           'vidal', 'vipul', 'newindia', 'city')


def send_email(file, subject):
    emailfrom = "iClaim.vnusoftware@gmail.com"
    emailto = ["sachin@vnusoftware.com", 'ceo@vnusoftware.com', 'maneesh@vnusoftware.com', 'akshaynaik797@gmail.com']
    fileToSend = file
    username = emailfrom
    password = "44308000"

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = ", ".join(emailto)
    msg["Subject"] = subject
    msg.preamble = subject

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

def get_hospital(filepath):
    hospital = ""
    if filepath != "":
        filepath = os.path.split(filepath)[-1]
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            q = "select hospital from settlement_mails where attach_path like %s limit 1"
            cur.execute(q, ('%' + filepath + '%',))
            r = cur.fetchone()
            if r is not None:
                hospital = r[0]
    return hospital

def check_mid_in_master(mid):
    filepath = 'master_insurer.xlsx'
    if os.path.exists(filepath):
        wb = openpyxl.open(filepath)
        ws = wb.active
        for row in ws.iter_rows(max_col=1, values_only=True):
            if mid in row:
                return True
    return False


def mark_utr_tables(filepath):
    filepath = os.path.split(filepath)[-1]
    flag = ''
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        q = "select completed from settlement_mails where attach_path like %s limit 1"
        cur.execute(q, ('%' + filepath + '%',))
        result = cur.fetchone()
        if result is not None:
            flag = result[0]
            #make fun for moving from utr_mails to utr_copy and delete
            #make utr_mails entry -> flag
            q = "update utr_mails set completed=%s where attach_path like %s limit 1"
            cur.execute(q, (flag, '%' + filepath + '%',))
            con.commit()
            q = "select sno from utr_mails where completed='X' and attach_path like %s limit 1"
            cur.execute(q, ('%' + filepath + '%',))
            r = cur.fetchone()
            if r is not None:
                sno = r[0]
                set_utr_mails_flag(sno)

def set_utr_mails_flag(sno):
    q = "BEGIN ; INSERT INTO utr_mails_copy SELECT * FROM utr_mails WHERE sno=%s; DELETE FROM utr_mails WHERE  sno=%s; COMMIT;"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (sno,))
        con.commit()

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

def accept_values(fromtime, totime, insname):
    fromtime = datetime.strptime(fromtime, '%d/%m/%Y %H:%M:%S')
    totime = datetime.strptime(totime, '%d/%m/%Y %H:%M:%S')
    if insname == 'all':
        for i in inslist:
            if collect_folder_data(fromtime, totime, i):
                print(f'{i} completed')
            else:
                print(f'{i} incomplete')
        return True
    elif collect_folder_data(fromtime, totime, insname):
        return True
    return False


def collect_folder_data(fromtime, totime, insname):
    regex = r'(?P<name>.*(?=_\d+))_(?P<date>\d+)'
    for x in os.walk(directory):
        for y in x[1]:
            if insname in y:
                result = re.compile(regex).search(y)
                if result is not None:
                    tempdict = result.groupdict()
                    folder_insname, foldertime = tempdict['name'], datetime.strptime(tempdict['date'], '%m%d%Y%H%M%S')
                    if fromtime < foldertime < totime and folder_insname == insname:
                        print(f'processing {y}')
                        process_insurer_excel(y, insname, foldertime)
            elif 'star' in y:
                result = re.compile(regex).search(y)
                if result is not None:
                    tempdict = result.groupdict()
                    folder_insname, foldertime = tempdict['name'], datetime.strptime(tempdict['date'], '%m%d%Y%H%M%S')
                    if fromtime < foldertime < totime and folder_insname == 'star':
                        if insname == 'big' or insname == 'small':
                            print(f'processing {y}')
                            process_insurer_excel(y, insname, foldertime)

        break
    return True


def process_insurer_excel(folder_name, insname, foldertime):
    for root, dirs, files in os.walk(directory + '/' + folder_name):
        flag = 0
        for file in files:
            path = (os.path.join(root, file))
            if 'smallinamdar.xlsx' in file:
                op = 'mediclaim@inamdarhospital.org Mediclaim@2019 imap.gmail.com inamdar hospital'
                subprocess.run(["python", "make_master.py", 'small_star', op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
            elif 'smallMax.xlsx' in file:
                op = 'Tpappg@maxhealthcare.com May@2020 outlook.office365.com Max PPT'
                subprocess.run(["python", "make_master.py", 'small_star', op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
            elif 'starinamdar.xlsx' in file:
                op = 'mediclaim@inamdarhospital.org Mediclaim@2019 imap.gmail.com inamdar hospital'
                subprocess.run(["python", "make_master.py", 'star', op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
            elif 'starMax.xlsx' in file:
                op = 'Tpappg@maxhealthcare.com May@2020 outlook.office365.com Max PPT'
                subprocess.run(["python", "make_master.py", 'star', op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
            elif 'Max.xlsx' in file:
                op = 'Tpappg@maxhealthcare.com May@2020 outlook.office365.com Max PPT'
                subprocess.run(["python", "make_master.py", insname, op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
            elif 'inamdar.xlsx' in file:
                op = 'mediclaim@inamdarhospital.org Mediclaim@2019 imap.gmail.com inamdar hospital'
                subprocess.run(["python", "make_master.py", insname, op, '', path])
                move_master_to_master_insurer('')
                print(f'processed {path}')
                flag = 1
                break
        if flag == 0:
            # code for 2nd condtion
            process_insurer_pdfs(folder_name, insname, files)
            pass
    pass


def process_insurer_pdfs(folder_name, insname, files):
    for f in files:
        if '.pdf' in f:
            fpath = directory + '/' + folder_name + '/' + f
            subprocess.run(["python", "make_insurer_excel.py", insname, fpath])
        pass
    pass


def automate_processing():
    try:
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            format = '%d/%m/%Y %H:%i:%s'
            q = "SELECT sno, attach_path, id FROM settlement_mails where hospital='noble'"
            # q = "SELECT sno, attach_path, id FROM settlement_mails INNER JOIN stgSettlement ON settlement_mails.sno = stgSettlement.sett_table_sno where TPAID = 'big' and UTRNo ='';"
            cur.execute(q)
            result = cur.fetchall()
        for sno, filepath, mid in result:
            try:
                sno = str(sno)
                if os.path.exists(filepath):
                    mark_flag('p', mid)
                    tmp = re.compile(r"(?<=letters\/)[a-zA-Z_]+(?=_)").search(filepath)
                    if tmp is not None:
                        tmp = tmp.group()
                        if os.path.exists('pdf_' + tmp + ".py"):
                            subprocess.run(["python", "make_insurer_excel.py", tmp, filepath, mid, sno])
                        else:
                            mark_flag('NO_INS_FILE', mid)
                    else:
                        mark_flag('NO_INS_EXIST', mid)
                else:
                    mark_flag('NO_ATTACH', mid)
            except:
                log_exceptions(filepath=filepath)
    except:
        log_exceptions()

if __name__ == '__main__':
    automate_processing()
