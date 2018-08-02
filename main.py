from text_csv_conversion import convert_all
from pdf_extraction import detect_tables
from pdf_processing import convert_pdf, clean
import time


def main():
    t1 = time.time()
    pdf = "../input/1807.10399.pdf"
    convert_pdf(pdf)  # Converts pdf to JPEG
    print(detect_tables(pdf))  # Extracts the tables
    convert_all()  # Converts text output to CSV
    t2 = time.time()
    t = t2 - t1
    print(t)


if __name__ == "__main__":
    main()
