import os
storedeductions = True
file_name = "storedeductions"
with open(file_name, "a") as fp:
    fp.write("")
if os.path.isfile(file_name):
    os.remove(file_name)