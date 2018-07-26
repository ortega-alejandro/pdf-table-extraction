#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:09:33 2018

@author: jadewu
"""
import nltk
import pandas as pd
import numpy as np
import re
import codecs
import pickle
from nltk.tokenize import RegexpTokenizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os
import re
import pickle
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTLine, LTFigure, LTImage, LTRect, LTTextLine
from pdfminer.converter import PDFPageAggregator, TextConverter
import urllib.request
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from bs4 import BeautifulSoup
from requests import get
import datetime


#####################ARRAY OF PDF URL LINKS####################
pdf_files = pdf_links
    
#loaded machine learning model
model = 'finalized_model.sav'
cv_model = 'count_vectorizer.sav'
tfidfv_model = 'tfidf_vectorizer.sav'
loaded_model = pickle.load(open(model, 'rb'))
loaded_cv = pickle.load(open(cv_model, 'rb'))
loaded_tfidfv = pickle.load(open(tfidfv_model, 'rb'))
#bound for number of words to initially include in the ML model
BOUND = 600
WORD_LIMIT = 700
#MAXIMUM PERCENTAGE OF TOTAL WORDS THAT WILL BE PARSED THROUGH
PERC_LIMIT = 0.9
#how many words to increment by if probability value is too low
INCREMENT = 300
#probability threshold value 
RELEVANCY_THRESHOLD = 0.4
original_prob = []
new_prob = []
relevant = []


def process_and_tokenize(pdf_text): 
    pdf_text = re.sub(r"\\n", " " , pdf_text) 
    pdf_text_tok = pdf_text.split()
    num_of_words = len(pdf_text_tok)
    return pdf_text_tok, num_of_words

#convert pdf url to text
def pdf_from_url_to_txt(url):
    try:
        rsrcmgr = PDFResourceManager()
        retstr = BytesIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        f = urllib.request.urlopen(url).read()
        fp = BytesIO(f)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        for page in PDFPage.get_pages(fp,
                                      pagenos,
                                      maxpages=maxpages,
                                      password=password,
                                      caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)
            text = str(retstr.getvalue())
            #text = re.sub(r"\\n", " " , text) 
            pdf_text_tok, num_of_words = process_and_tokenize(text)
            if (num_of_words > WORD_LIMIT):
                break
        retstr.close()
        fp.close()
        device.close()
    except PDFTextExtractionNotAllowed:
        print("PDFTextExtractionNotAllowed")
        pdf_text_tok = []
        num_of_words = -1
    except urllib.error.HTTPError as err:
        if err.code == 404:
            print("HTTPError 404")
            pdf_text_tok = []
            num_of_words = -2
    return pdf_text_tok, num_of_words

#return value between 0-1, probability of whether a pdf is relevant or not
def predict(pdf_text_arr):
    pdf_text_cv = loaded_cv.transform(pdf_text_arr)
    pdf_text_tfidf = loaded_tfidfv.transform(pdf_text_arr)
    probability = round(loaded_model.predict_proba(pdf_text_tfidf)[:,1][0], 3)
    return probability


for pdf in pdf_files:
    pdf_text_tok, num_of_words = pdf_from_url_to_txt(pdf)
    pdf_text_arr = pdf_text_tok[0:BOUND]
    pdf_text_arr = [" ".join(pdf_text_arr)]
    original_probability = predict(pdf_text_arr)
    new_probability = original_probability 
    if (original_probability < RELEVANCY_THRESHOLD and num_of_words > 1):
        while (BOUND < WORD_LIMIT):
            BOUND += INCREMENT
            pdf_text_arr = pdf_text_tok[0:BOUND]
            pdf_text_arr = [" ".join(pdf_text_arr)]
            new_probability = predict(pdf_text_arr)
            #print("word count = " + str(BOUND) + ", probability = " + str(new_probability))
    if (num_of_words <= 1):
            new_probability = 'NA'
    if (num_of_words == -1):
        original_probability = -1
        new_probability = -1
        relevant = 'PDFTextExtractionNotAllowed'
    if (num_of_words == -2):
        original_probability = -2
        new_probability = -2
        relevant = 'HTTPError 404'
    original_prob.append(original_probability) 
    new_prob.append(new_probability)

#determining relevancy as "yes" or "no" in a list (relevant) based on new probability value    
for i in new_prob:
    if (i == "NA"):
        relevant.append("scanned document (total number of words = 0)")
    elif (i < RELEVANCY_THRESHOLD):
        relevant.append("no")
    else:
        relevant.append("yes")

#prints out a dictionary, (key, value) = (pdf url, yes/no)
def display_relevancy(pdf_files, relevant):
    relevancy = {}
    for i in range(len(pdf_files)):
        relevancy[pdf_files[i]] = relevant[i]
    return relevancy

#prints out a table with the pdf_ url, the original probability, the new probability 
#(will be same as original probability if original probability > RELEVANCY_THRESHOLD, and whether it's relevant or not)
def display_full_df(pdf_files, original_prob, new_prob, relevant):   
    table = pd.DataFrame()
    table[0] = pdf_files
    table[1] = original_prob
    table[2] = new_prob
    table[3] = relevant
    table.columns = ['pdf-files', 'original probabilities', 'new probabilities', 'relevant?']
    return full_df
    

#relevancy = display_relevancy(pdf_files, relevant)
full_df = display_full_df(pdf_files, original_prob, new_prob, relevant)

