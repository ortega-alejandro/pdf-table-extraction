import text_csv_conversion as tcc
import pdf_processing as pdfp
import pdf_extraction as pdfe
import ontologies
import time


def main():
    '''t1 = time.time()
    pdfp.convert_pdf("22B6352E6BECE47FADD61B6B9DFFCAB91468236.pdf")  # Converts pdf to JPEG
    pdfe.function_calls()  # Extracts the tables
    tcc.convert_all()  # Converts text output to CSV
    t2 = time.time()
    t = t2 - t1
    print(t)'''
    my_pdf = "sample.pdf"
    ontology_path = "file:///users/brookeerickson/downloads/root-ontology-v9.owl"
    ontologies.run(my_pdf, ontology_path)
    # If you want to clean the directory with pictures, call pdfp.clean('images')


if __name__ == "__main__":
    main()
