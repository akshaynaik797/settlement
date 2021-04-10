tables = camelot.read_pdf(pdfpath, pages='all')
tables.export('temp_files/foo1.xls', f='excel')