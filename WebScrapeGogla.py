#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 15:14:26 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import urllib.request
import datetime
import re



NEXT_TEXT = 'More'
URL = 'https://www.gogla.org/publications'
TAGS = [('div','view-content')]
LAST_SCRAPE_DATE = 'Dec 31, 2016'
SORTED_SITE = True
DATE_TAG = ('div','field field-name-post-date field-type-ds field-label-hidden')
DATE_FORM = '%b %d, %Y'


all_links = [URL]
links_visited = []
pdf_links = []
xlsx_links = []
URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
prefix_length = len(URL_PREFIX)


page_num = 1
while all_links:
    main_url = all_links[0]
    print (main_url)
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text = NEXT_TEXT)
    print ('PAGE: '+str(page_num))
    if len(pages)>0:
        pages = URL_PREFIX+pages[0]['href']
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
        links = []
        for tag_type,tag in TAGS:
            links_page = html_soup.find_all(tag_type, class_ = tag)     
            if len(links_page)==0:
                continue
            for each in links_page:
                articles = each.find_all('div',class_ = 'views-row')
                for site in articles:
                    date = site.find(DATE_TAG[0],class_ = DATE_TAG[1])
                    if date is not None and 'view' not in date.text:
                        date = date.text.strip()
                        date = datetime.datetime.strptime(date,DATE_FORM).date()
                        last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE,DATE_FORM).date()
                        if date>=last_date:
                            links.append(site)
                        elif SORTED_SITE:
                            pages=''
                            break
                    else:
                        links.append(site)
        for each in links:
            article_links= each.find_all('a',href=True)
            for url in article_links:
                pdf_url = url['href']
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
    if len(pages)>0:
        all_links.append(pages)
        page_num+=1

    
print ('all_links')
print (all_links)
print ('links_visited')
print (len(links_visited))
print (links_visited)
print ('pdf_links')
print (len(pdf_links))
for i in pdf_links:
    print (i)
print ('xlsx_links')
print (len(xlsx_links))
for i in (xlsx_links):
    print (i)