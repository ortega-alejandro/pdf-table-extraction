#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 15:14:26 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import datetime
import re


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
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text = NEXT_TEXT)
    print ('PAGE: '+str(page_num))
    print (main_url)
    if len(pages)>0:
        pages = URL_PREFIX+pages[0]['href']
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
                if 'file' in pdf_url:           #### E4I
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
                else:
                    all_links.append(pdf_url)
    if 'file' in current:                       #### E4I
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
        
def multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited):
    page_num = 1
    while all_links:
        pages = get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX)
        
        while all_links:
            current = all_links[0]
            response = get(current)
            html_soup = BeautifulSoup(response.text, 'lxml')
            
            links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, [], html_soup, pages)
            
            pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
    
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
        

        
        
#################################################################################
NEXT_TEXT = ''
URL = 'https://www.energy4impact.org/publications'
TAGS = [('div', 'o-btn btn--style-2')]
DATE_TAG = []
DATE_FORM = ''
SORTED_SITE = True
LAST_SCRAPE_DATE = ''




#TEXT_FILE = 'ruralelec.txt'

#URL, TAGS, SORTED_SITE, DATE_TAG, DATE_FORM, NEXT_TEXT, LAST_SCRAPE_DATE = get_url_attributes(TEXT_FILE)

#print(DATE_TAG)

URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
prefix_length = len(URL_PREFIX)
    
if NEXT_TEXT == '':
    print ("ONE PAGE")
    one_page(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])
else:
    print ("MULTIPLE PAGES")
    multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])



