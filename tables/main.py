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
    my_pdf = "desktop/OneDrive_2018-05-27/ml/3AC1DACD68A35562618B2A9D7B92DE841964B.pdf"
    ontology_path = "file:///users/brookeerickson/downloads/root-ontology-v9.owl"
    onto = get_ontology(ontology_path).load()
    ontologies.run(my_pdf, ontology_path, page_threshold=0.005, threshold=0.03, number_of_levels=3, print_output=True, print_debug=False)

if __name__ == "__main__":
    main()
