import pdftotext
with open("84076041_.pdf", "rb") as f:
        pdf = pdftotext.PDF(f)
with open('temp_files/o21321utput.txt', 'w', encoding='utf-8') as f:
    f.write(" ".join(pdf))