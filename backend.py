from distutils.dir_util import copy_tree, remove_tree
import zipfile
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from shutil import copyfile

from movemaster import move_master_to_master_insurer

directory = 'backups'

inslist = ('all', 'aditya', 'apollo', 'bajaj', 'big', 'east_west', 'fgh', 'fhpl', 'Good_health', 'hdfc',
           'health_heritage', 'health_india', 'health_insurance', 'icici_lombard', 'MDINDIA', 'Medi_Assist',
           'Medsave', 'Paramount', 'Raksha', 'reliance', 'religare', 'small', 'united', 'Universal_Sompo',
           'vidal', 'vipul')

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
    dst = 'excels/'
    remove_tree(dst)
    Path(dst).mkdir(parents=True, exist_ok=True)
    master_excel = 'master_insurer.xlsx'
    letters_location = "../index/"
    today = datetime.now()
    fromtime = today.replace(hour=0, minute=0, second=1)
    totime = today.replace(hour=23, minute=59, second=59)
    today = datetime.now().strftime("%d_%m_%Y")
    hospital_list = ['Max PPT', 'ils', 'ils_dumdum', 'noble', 'inamdar', 'ils_agartala', 'ils_howrah']
    for hospital in hospital_list:
        if os.path.exists(master_excel):
            os.remove(master_excel)
        remove_tree(directory)
        folder = os.path.join(letters_location, today, hospital, "letters/")
        Path(folder).mkdir(parents=True, exist_ok=True)
        Path(directory).mkdir(parents=True, exist_ok=True)
        copy_tree(folder, directory)
        for ins in inslist:
            if collect_folder_data(fromtime, totime, ins):
                print(f'{ins} completed')
            else:
                print(f'{ins} incomplete')
        if os.path.exists(master_excel):
            copyfile(master_excel, os.path.join(dst, hospital + '.xlsx'))
    zipf = zipfile.ZipFile('letters.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(dst, zipf)
    zipf.close()
    #code to send zip to emails
    return True

if __name__ == '__main__':
    automate_processing()
