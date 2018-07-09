from PyPDF2 import PdfFileReader
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import re
import warnings

table_count=0
regex = "^(?!\s)(Table|Annex|TABLE)\s+([1-9]+[A-Z]?|[A-Z]?)\.?:?\s?"
fp = open(my_pdf, 'rb')
doc = PDFDocument(parser)
parser = PDFParser(fp)
rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
pdf = PdfFileReader(open(my_pdf, 'rb'))
num = pdf.getNumPages()


path = 'btest2.txt'
text = open(path,'r')
final = open('csvfile3.csv','w')
regex = '(\s\s)+[0-9]+'
regex_space = '([ ]{2,})+'