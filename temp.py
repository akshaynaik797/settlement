from distutils.dir_util import copy_tree
import os
from pathlib import Path
from shutil import copyfile

dst = '/home/akshay/Videos/teasdmp.txt'
a = os.path.split(dst)[0]
Path(a).mkdir(parents=True, exist_ok=True)
copyfile('/home/akshay/temp.txt', dst)