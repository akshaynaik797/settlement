import camelot
pdfpath = filepath = '/home/akshay/temp/4914_248021912_1.pdf'
tables = camelot.read_pdf(pdfpath, pages='all')
tables.export('temp_files/foo1.xls', f='excel')
