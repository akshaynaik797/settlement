import os
import re
import subprocess
from datetime import datetime
from movemaster import move_master_to_master_insurer

directory = 'backups'


def accept_values(fromtime, totime, insname):
    fromtime = datetime.strptime(fromtime, '%d/%m/%Y %H:%M:%S')
    totime = datetime.strptime(totime, '%d/%m/%Y %H:%M:%S')
    if collect_folder_data(fromtime, totime, insname):
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
            fpath = directory+'/'+folder_name+'/'+f
            subprocess.run(["python", "make_insurer_excel.py", insname, fpath])
        pass
    pass


if __name__ == '__main__':
    # collect_folder_data()
    pass
