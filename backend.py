import os
import re
from datetime import datetime

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
                        process_folder(y, insname, foldertime)
        break
    return True


def process_folder(folder_name, insname, foldertime):
    for root, dirs, files in os.walk(directory+'/'+folder_name):
        for file in files:
            path = (os.path.join(root, file))
            if 'Max.xlsx' in file:
                print(path)
                pass
            elif 'inamdar.xlsx' in file:
                print(path)
                pass
            else:
                pass
        pass
    pass



if __name__ == '__main__':
    # collect_folder_data()
    pass
