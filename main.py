from text_csv_conversion import convert_all
import subprocess
import time


def simple_convert(pdf_file):
    output = 'output/txt/sample.txt'
    subprocess.call(["pdftotext", "-layout", pdf_file, output])


def main():
    t1 = time.time()
    pdf = "input/AP_rural_page1.pdf"
    simple_convert(pdf)
    # convert_pdf(pdf)  # Converts pdf to JPEG
    # print(detect_tables(pdf))  # Extracts the tables
    convert_all(src='output/txt/', dst='output/csv/', name='sample')  # Converts text output to CSV
    t2 = time.time()
    t = t2 - t1
    print(t)


if __name__ == "__main__":
    main()
