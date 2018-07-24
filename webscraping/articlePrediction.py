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

def get_url_attributes(file):
    lines = [line.rstrip('\n') for line in open(file)]
    url = lines[1]
    html_tags = get_tags(lines[2])
    date_tags = get_tags(lines[4])[0]
    if len(date_tags) == 1:
        date_tags = []
    sort = False
    if lines[3] == '1':
        sort = True
    date_form = lines[5]
    next_text = lines[1]
    date = lines[6]
    # last_scraped = datetime.datetime.strptime(date, date_form).date()

    return url, html_tags, sort, date_tags, date_form, next_text, date

def get_tags(line):
    tags = line.split('|')
    final_tags = []
    for tag in tags:
        final_tags.append(tag.split(','))
    return final_tags

def get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX):
    main_url = all_links[0]
    print (main_url)
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text = NEXT_TEXT)
    print ('PAGE: '+str(page_num))
    if len(pages)>0:
        pages = URL_PREFIX+pages[0]['href']
    print (pages)
    return pages

def tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, links, html_soup, pages):
    for tag_type,tag in TAGS:
        links_page = html_soup.find_all(tag_type, class_ = tag) 
        if len(links_page)==0:
            continue
        for each in links_page:
            if len(DATE_TAG)>0:
                date = each.find(DATE_TAG[0],class_ = DATE_TAG[1])
                print ("DATE")
                print (date)
                if date is not None:
                    date = date.text.strip()
                    date = datetime.datetime.strptime(date,DATE_FORM).date()
                    last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE,DATE_FORM).date()
                    if date>=last_date:
                        links.append(each)
                    elif SORTED_SITE:
                        pages=''
                        break
                else:
                    links.append(each)
            else:
                links.append(each)
    return links, pages

def scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            pdf_url= link['href']
            if pdf_url[:prefix_length] != URL_PREFIX:
                pdf_url = URL_PREFIX+str(pdf_url)
            if pdf_url not in links_visited:
                links_visited.append(pdf_url)
                if 'pdf' in pdf_url:
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
                else:
                    all_links.append(pdf_url)
    if 'pdf' in current:
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links

def one_page(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited):
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
    
        links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, [], html_soup, '')
    
        pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
     
    #to debug
    '''
    print ('all_links')
    print (all_links)
    print ('links_visited')
    print (len(links_visited))
    print (links_visited)
    '''
    print ('pdf_links')
    print (len(pdf_links))
    for i in pdf_links:
        print (i)
    print ('xlsx_links')
    print (len(xlsx_links))
    for i in (xlsx_links):
        print (i)
    return pdf_links
        
def multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited):
    page_num = 1
    while all_links:
        pages = get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX)
        
        while all_links:
            current = all_links[0]
            response = get(current)
            html_soup = BeautifulSoup(response.text, 'lxml')
            
            links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, [], html_soup, pages)
            print (links)
            
            pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
    
        if len(pages)>0:
            all_links.append(pages)
            page_num+=1
    
    #to debug
    '''print ('all_links')
    print (all_links)
    print ('links_visited')
    print (len(links_visited))
    print (links_visited)
    '''
    print ('pdf_links')
    print (len(pdf_links))
    for i in pdf_links:
        print (i)
    print ('xlsx_links')
    print (len(xlsx_links))
    for i in (xlsx_links):
        print (i)
    return pdf_links
        
#################################################################################
'''NEXT_TEXT = 'More'
URL = 'https://www.gogla.org/publications'
TAGS = [('div','ds-1col node node-resource node-teaser view-mode-teaser clearfix')]
LAST_SCRAPE_DATE = 'Dec 31, 2017'
SORTED_SITE = False
DATE_TAG = ('div','field field-name-post-date field-type-ds field-label-hidden')
DATE_FORM = '%b %d, %Y'''

NEXT_TEXT = 'Next »'
URL = 'http://www.undp.org/content/undp/en/home/library.html?start=0&sort=date&view=cards&tag=topics:energy/energy-access'
TAGS = [('div','library-card-image'),('div','small-12 medium-8 columns'),('div','docDownloads')]
LAST_SCRAPE_DATE = 'January 1, 2017'
SORTED_SITE = True
DATE_TAG = ('div','library-card-date')
DATE_FORM = '%B %d, %Y'

'''NEXT_TEXT = ''
URL = 'http://www.cleanenergyministerial.org/publication-cem'
TAGS = [('div','publication-latest-cem')]
LAST_SCRAPE_DATE = '2018-05-30'
SORTED_SITE = True
DATE_TAG = ('div','views-field views-field-field-publication-date')
DATE_FORM = '%Y-%m-%d'''

'''NEXT_TEXT = ''
URL = 'https://www.ruralelec.org/publications'
TAGS = [('div','col-xs-6 col-sm-3'),('span', 'file')]
DATE_TAG = []
DATE_FORM = ''
SORTED_SITE = True
LAST_SCRAPE_DATE = '''''


'''NEXT_TEXT = ''
URL = 'http://www.gnesd.org/PUBLICATIONS/Energy-Access-Theme'
TAGS = [('div','contentmain')]
DATE_TAG = []
DATE_FORM = ''
SORTED_SITE = True
LAST_SCRAPE_DATE = '''

'''NEXT_TEXT = 'More'
URL = 'https://www.reeep.org/publications/'
TAGS = [('div','view-content ui-accordion ui-widget ui-helper-reset ui-accordion-icons'),('h4','field-content list-view-heading'),('span','file')]
LAST_SCRAPE_DATE = ''
SORTED_SITE = True
DATE_TAG = []
DATE_FORM = '''

'''NEXT_TEXT = 'More'
URL = 'http://energyaccess.org/resources/publications/'
TAGS = [('div', 'list-content items-list')]
LAST_SCRAPE_DATE = ''
SORTED_SITE = True
DATE_TAG = []
DATE_FORM = '''

'''NEXT_TEXT = ' Next '
URL = 'https://www.sun-connect-news.org/databases/documents/all/'
TAGS = [('div','article articletype-2 topnews')]
DATE_TAG = []
DATE_FORM = ''
SORTED_SITE = True
LAST_SCRAPE_DATE = '''''

#FORBIDDEN??
#NEXT_TEXT = 'More'
#URL = 'https://united4efficiency.org/resources/publications/'
#TAGS = [('div', 'featured-img'), ('div', 'entry-content')]
#LAST_SCRAPE_DATE = ''
#SORTED_SITE = True
#DATE_TAG = []
#DATE_FORM = ''

#TEXT_FILE = 'ruralelec.txt'

#URL, TAGS, SORTED_SITE, DATE_TAG, DATE_FORM, NEXT_TEXT, LAST_SCRAPE_DATE = get_url_attributes(TEXT_FILE)

print(DATE_TAG)

URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
prefix_length = len(URL_PREFIX)
    
if NEXT_TEXT == '':
    print ("ONE PAGE")
    pdf_links = one_page(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])
else:
    print ("MULTIPLE PAGES")
    pdf_links = multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])


#####################ARRAY OF PDF URL LINKS####################
pdf_files = pdf_links
'''for pdf in pdf_links:
    pdf_str = "'" + pdf + "'"
    pdf_files.append(pdf_str)'''
    
#loaded machine learning model
model = 'finalized_model.sav'
cv_model = 'count_vectorizer.sav'
tfidfv_model = 'tfidf_vectorizer.sav'
loaded_model = pickle.load(open(model, 'rb'))
loaded_cv = pickle.load(open(cv_model, 'rb'))
loaded_tfidfv = pickle.load(open(tfidfv_model, 'rb'))
#bound for number of words to initially include in the ML model
BOUND = 600
#MAXIMUM PERCENTAGE OF TOTAL WORDS THAT WILL BE PARSED THROUGH
PERC_LIMIT = 0.9
#how many words to increment by if probability value is too low
INCREMENT = 300
#probability threshold value 
RELEVANCY_THRESHOLD = 0.4
original_prob = []
new_prob = []
relevant = []

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
        fp.close()
        device.close()
        text = str(retstr.getvalue())
        retstr.close()
    except PDFTextExtractionNotAllowed:
        text = []
    return str(text)

def tokenize(pdf_text): 
    pdf_text_tok = pdf_text.split()
    num_of_words = len(pdf_text_tok)
    return pdf_text_tok, num_of_words

#return value between 0-1, probability of whether a pdf is relevant or not
def predict(pdf_text_arr):
    pdf_text_cv = loaded_cv.transform(pdf_text_arr)
    pdf_text_tfidf = loaded_tfidfv.transform(pdf_text_arr)
    probability = round(loaded_model.predict_proba(pdf_text_tfidf)[:,1][0], 3)
    return probability


for pdf in pdf_files:
    print("PDF FILE: " + pdf)
    pdf_text = pdf_from_url_to_txt(pdf)
    pdf_text = re.sub(r"\\n", " " , pdf_text) 
    pdf_text_tok, num_of_words = tokenize(pdf_text)
    pdf_text_arr = pdf_text_tok[0:BOUND]
    pdf_text_arr = [" ".join(pdf_text_arr)]
    original_probability = predict(pdf_text_arr)
    original_prob.append(original_probability) 
    new_probability = original_probability 
    while (new_probability < RELEVANCY_THRESHOLD):
        if (num_of_words < 5):
            new_probability = 'NA'
            break
        BOUND += INCREMENT
        pdf_text_arr = pdf_text_tok[0:BOUND]
        pdf_text_arr = [" ".join(pdf_text_arr)]
        new_probability = predict(pdf_text_arr)
        #to debug
        print("word count = " + str(BOUND) + ", probability = " + str(new_probability))
        if ((BOUND/num_of_words) > PERC_LIMIT):
            break
    print('new probability: ' + str(new_probability))
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

