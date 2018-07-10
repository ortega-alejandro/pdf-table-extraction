import text_csv_conversion as tcc
import pdf_processing as pdfp
import pdf_extraction as pdfe


def main():
    pdfp.convert_pdf("sample.pdf")  # Converts pdf to JPEG
    pdfe.function_calls()  # Extracts the tables
    tcc.convert_all()  # Converts text output to CSV
    # If you want to clean the directory with pictures, call pdfp.clean('images')


if __name__ == "__main__":
    main()
