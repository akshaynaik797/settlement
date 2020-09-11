import pdftotext

fpath = '/home/akshay/PycharmProjects/settelement/backups/health_insurance_08172020211241/191300311111.pdf'
with open(fpath, "rb") as f:
    pdf = pdftotext.PDF(f)

with open('temp_files/output.txt', 'w') as f:
    f.write(" ".join(pdf))
with open('temp_files/output.txt', 'r') as myfile:
    f = myfile.read()