from tkinter import Tk, Label, Entry, StringVar, Button, ttk, messagebox, Scrollbar, BOTH, Listbox, RIGHT, END
from backend import accept_values
from from_delete import accept_data
import tkinter

my_date = ''
mygui = Tk(className='Process Failed Settlements')
mygui.geometry("900x200")

format_label = Label(mygui, text='dd/mm/yyyy hh:mm:ss').grid(row=2, column=1)
format_label2 = Label(mygui, text='dd/mm/yyyy hh:mm:ss').grid(row=2, column=4)

fromtime = StringVar()
fromtime_label = Label(mygui, text="From", width=10).grid(row=1, column=0)
fromtime_entry = Entry(mygui, textvariable=fromtime).grid(row=1, column=1, pady=15)
fromtime.set("01/08/2020 00:00:01")

totime = StringVar()
totime_label = Label(mygui, text="To", width=10).grid(row=1, column=3)
totime_entry = Entry(mygui, textvariable=totime).grid(row=1, column=4)
totime.set("01/09/2020 00:00:01")

insname = StringVar()
ttk.Label(mygui, text="Insurer Name", width=10).grid(column=0, row=4, pady=15, padx=15)
inslist = ttk.Combobox(mygui, width=12, textvariable=insname)
inslist['values'] = ('all', 'aditya', 'apollo', 'bajaj', 'big', 'east_west', 'fgh', 'fhpl', 'Good_health', 'hdfc',
                     'health_heritage', 'health_india', 'health_insurance', 'icici_lombard', 'MDINDIA', 'Medi_Assist',
                     'Medsave', 'Paramount', 'Raksha', 'reliance', 'religare', 'small', 'united', 'Universal_Sompo',
                     'vidal', 'vipul')
inslist.grid(row=4, column=1)
inslist.current(0)


def send_values():
    if fromtime.get() != '' and totime.get() != '' and insname.get() != '':
        result = accept_values(fromtime.get(), totime.get(), insname.get())
        if result is True:
            print('Job finished')
            messagebox.showinfo(title='Success', message='Job finished')
        else:
            messagebox.showerror(title='Error', message='Job failed, see logs')
    else:
        messagebox.showerror(title="Error", message='Enter values in all fields')

def check_in_db():
    global my_date
    win = tkinter.Toplevel()
    win.wm_title("Check db")
    win.geometry("600x200")
    format_label = Label(win, text='dd/mm/yyyy hh:mm:ss').grid(row=2, column=1)
    # format_label2 = Label(win, text='dd/mm/yyyy hh:mm:ss').grid(row=2, column=4)

    fromtime1 = StringVar()
    fromtime_label1 = Label(win, text="From", width=10).grid(row=1, column=0)
    fromtime_entry1 = Entry(win, textvariable=fromtime).grid(row=1, column=1, pady=15)
    fromtime1.set("01/08/2020 00:00:01")
    my_date = fromtime1.get()



    # totime = StringVar()
    # totime_label = Label(win, text="To", width=10).grid(row=1, column=3)
    # totime_entry = Entry(win, textvariable=totime).grid(row=1, column=4)
    # totime.set("01/09/2020 00:00:01")
    checkButton1 = Button(win, text="Check Deleted", command=check_deleted).grid(row=5, column=1)
    closeButton1 = Button(win, text="Close", command=win.destroy).grid(row=5, column=2)

def check_deleted():
    root = tkinter.Toplevel()
    root.wm_title("Check1")
    root.geometry("600x300")

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=BOTH)
    listbox = Listbox(root)
    listbox.pack()
    temp = accept_data(my_date)
    for j in temp:
        print(j)
        listbox.insert(END, j)

    # bind listbox to scrollbar
    listbox.config(yscrollcommand=scrollbar.set, width=100)
    scrollbar.config(command=listbox.yview)
    # checkButton1 = Button(root, text="Process pdfs", command=check_in_db).pack()
    closeButton1 = Button(root, text="Close", command=root.destroy).pack()


loginButton = Button(mygui, text="Submit", command=send_values).grid(row=5, column=0)
checkButton = Button(mygui, text="Check Deleted", command=check_in_db).grid(row=5, column=1)
closeButton = Button(mygui, text="Close", command=mygui.destroy).grid(row=5, column=2)
mygui.mainloop()
