import os
import subprocess
from wand.image import Image
from PyPDF2 import PdfFileReader
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

def process_pdf(path):
    table_count=0
    regex = "^(?!\s)(Table|Annex|TABLE)\s+([1-9]+[A-Z]?|[A-Z]?)\.?:?\s?"
    fp = open(my_pdf, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pdf = PdfFileReader(open(my_pdf, 'rb'))
    num = pdf.getNumPages()
    try:
        with Image(filename=path, resolution=200) as img:
            img.save(filename='image.jpg')
    except:
        subprocess.call(["convert", "-density","200",path,"-quality","100","-sharpen","0x1.0","image.jpg"])
    return table_count, regex, fp, doc, laparams, interpreter, pdf, num
