#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 15:16:14 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import urllib.request
import re

NEXT_TEXT = '»'
url = 'https://africaopendata.org/dataset'
URL_PREFIX = 'https://africaopendata.org/'


all_links = [url]
pdf_links = []

page_num = 1
while all_links:
    main_url = all_links.pop()
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    print (page_num)
    links = html_soup.find_all('div', class_ = 'dataset-resource-list')
    for doc in links:
        pdf_ = doc.find_all('a',href=True)
        for link in pdf_:
            pdf_url= link['href']
            data_form = link['data-format']
            if data_form == 'pdf':
                pdf_links.append(pdf_url)
                print (pdf_url)
    pages = html_soup.find_all('a', text = NEXT_TEXT)
    if len(pages)>0:
        pages = URL_PREFIX+pages[0]['href']
        all_links.append(pages)
        print (all_links)
        page_num+=1

    
print ('all_links')
print (all_links)
print ('pdf_links')
print (len(pdf_links))
for i in pdf_links:
    print (i)