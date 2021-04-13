import camelot
pdfpath = filepath = '/home/akshay/Downloads/54982420_.pdf'
tables = camelot.read_pdf(pdfpath, pages='all')
tables.export('temp_files/foo1.xls', f='excel')
