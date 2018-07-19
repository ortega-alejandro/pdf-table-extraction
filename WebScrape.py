#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:20:47 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import urllib.request
import datetime
import re

NEXT_TEXT = 'next ›'
URL = 'https://africaopendata.org/dataset'
TAGS = [('h5','dataset-heading'),('ul','resource-list'),('div','actions')]
LAST_SCRAPE_DATE = 'May 20, 2018'
SORTED_SITE = True
DATE_TAG = ('div','dataset-date')
DATE_FORM = '%B %d, %Y'


'''NEXT_TEXT = 'next ›'
URL = 'https://www.wri.org/our-work/project/energy-access/publications'
TAGS = [('h2','article-title--large'),('li','download-item')]
DATE_TAG = ('span','byline-date')
DATE_FORM = '%B %Y'
LAST_SCRAPE_DATE = 'December 2016'
SORTED_SITE = True'''


'''#NEXT_TEXT = ['Latest','View more','>>']
NEXT_TEXT = 'next pull-right'
URL = 'https://openknowledge.worldbank.org/recent-submissions'
#TAGS = [('div','content date-info'),('div','bitstream-link-wrapper')]
TAGS= [('div','content author-info'),('div','bitstream-link-wrapper')]
DATE_TAG = TAGS[0]
#DATE_FORM = '%B %d, %Y'
DATE_FORM = '(%Y-%m)'
LAST_SCRAPE_DATE = '(2018-01)'
SORTED_SITE = True'''


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
        #pages = pages[0].find('a',href=True)
        pages = URL_PREFIX+pages[0]['href']
        #pages = URL_PREFIX+pages['href']
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
                date = each.parent.find(DATE_TAG[0],class_ = DATE_TAG[1])      ####### OPENAFRICA,GOGLA ######
                date = each.find(DATE_TAG[0],class_ = DATE_TAG[1])               ####### WRI #######
                print ("DATE")
                print (date)
                if date is not None and 'view' not in date.text:
                    date = date.text.split('|')[0][8:].strip()       ####### OPENAFRICA #######
                    ######date = date.text.strip()                  ########### WRI,GOGLA #########
                    date = datetime.datetime.strptime(date,DATE_FORM).date()
                    last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE,DATE_FORM).date()
                    if date>=last_date:
                        links.append(each)
                    elif SORTED_SITE:
                        pages=''
                        break
                else:
                    links.append(each)
        print (links)
        for each in links:
            pdf_ = each.find_all('a',href=True)
            for link in pdf_:
                pdf_url= link['href']
                if 'metadata' in pdf_url:
                    continue
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
