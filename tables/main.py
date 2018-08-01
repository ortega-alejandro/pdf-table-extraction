from text_csv_conversion import convert_all
from pdf_extraction import detect_tables
from pdf_processing import convert_pdf, clean
import time
import os


def pdf_table_extraction(pdf):
    t1 = time.time()
    convert_pdf(pdf)  # Converts pdf to JPEG
    file_name = pdf.split('/')[-1][:4]
    print("Total tables:"+str(detect_tables(pdf,file_name))) # Extracts the tables
    convert_all(name = file_name)  # Converts text output to CSV
    t2 = time.time()
    t = t2 - t1
    print(t)


if __name__ == "__main__":
    i=0
    files = os.listdir('/users/brookeerickson/desktop/OneDrive_2018-05-27/ml/')
    if '.DS_Store' in files:
        files.remove('.DS_Store')
    print (files[:10])
    while i<10:
        file = '/users/brookeerickson/desktop/OneDrive_2018-05-27/ml/'+files[i]
        pdf_table_extraction(file)
        i+=1
