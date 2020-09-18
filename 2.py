import sqlite3

my_conn = sqlite3.connect('database1.db')
###### end of connection ####
r_set = my_conn.execute("SELECT count(*) as no from updation_detail_log")
data_row = r_set.fetchone()
no_rec = data_row[0]  # Total number of rows in table
limit = 8;  # No of records to be shown per page.
##### tkinter window ######
import tkinter  as tk
from tkinter import *

my_w = tk.Tk()
my_w.geometry("350x200")


def my_display(offset):
    q = "SELECT * from updation_detail_log LIMIT " + str(offset) + "," + str(limit)
    r_set = my_conn.execute(q);
    i = 0  # row value inside the loop
    for student in r_set:
        for j in range(len(student)):
            e = Entry(my_w, width=10, fg='blue')
            e.grid(row=i, column=j)
            e.insert(END, student[j])
        i = i + 1
    while (i < limit):  # required to blank the balance rows if they are less
        for j in range(len(student)):
            e = Entry(my_w, width=10, fg='blue')
            e.grid(row=i, column=j)
            e.insert(END, "")
        i = i + 1
    # Show buttons
    back = offset - limit  # This value is used by Previous button
    next = offset + limit  # This value is used by Next button
    b1 = tk.Button(my_w, text='Next >', command=lambda: my_display(next))
    b1.grid(row=12, column=4)
    b2 = tk.Button(my_w, text='< Prev', command=lambda: my_display(back))
    b2.grid(row=12, column=1)
    if (no_rec <= next):
        b1["state"] = "disabled"  # disable next button
    else:
        b1["state"] = "active"  # enable next button

    if (back >= 0):
        b2["state"] = "active"  # enable Prev button
    else:
        b2["state"] = "disabled"  # disable Prev button


my_display(0)
my_w.mainloop()