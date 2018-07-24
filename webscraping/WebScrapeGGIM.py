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

def tags_by_date(TAGS, DATE_TAG, DATE_FORM, links, html_soup, pages):
    #print (html_soup)
    #links_page = html_soup.find_all('div', class_ = 'i-tree') 
    #print ("LINKS ARE HERE")
    #print (links_page)
    #for each in links_page:
    #    links.append(each)
    for tag_type, tag in TAGS:
        links_page = html_soup.find_all(tag_type, class_ = tag) 
        for each in links_page:
            links.append(each)
    links_page = html_soup.find_all('div', id = 'ctl00_ctlContentPlaceHolder_ctl00_ctl00_ctl00_ctl00_ctlPanelBar_ctlViewArticleAttachments_ctl00_ctlViewAttachments_ctl00_ctlDataList') 
    for each in links_page:
        links.append(each)
        
    return links, pages


def scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            print ("TEXT HERE")
            print (link.text)
            if 'pdf' in link.text:
                pdf_url= link['href']
                if pdf_url[:prefix_length] != URL_PREFIX:
                    pdf_url = URL_PREFIX+str(pdf_url)
                print ("PDF URL HERE")
                print (pdf_url)
                if pdf_url not in links_visited:
                    links_visited.append(pdf_url)
                    pdf_links.append(pdf_url)
            else:
                pdf_url= link['href']
                if pdf_url[:prefix_length] != URL_PREFIX:
                    pdf_url = URL_PREFIX+str(pdf_url)
                if pdf_url not in links_visited:
                    links_visited.append(pdf_url)
                    all_links.append(pdf_url)
    if 'pdf' in current:
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links


def one_page(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, all_links, pdf_links, xlsx_links, links_visited):
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
    
        links,pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, [], html_soup, '')
        print (links)
    
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
        
def multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, all_links, pdf_links, xlsx_links, links_visited):
    page_num = 1
    while all_links:
        pages = get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX)
        
        while all_links:
            current = all_links[0]
            response = get(current)
            html_soup = BeautifulSoup(response.text, 'lxml')
            
            links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, [], html_soup, pages)
            print (links)
            
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
URL = 'http://ggim.un.org/knowledgebase/'
TAGS = [('div','i-panel-content')]#,('div',id,'ctl00_ctlContentPlaceHolder_ctl00_ctl00_ctl00_ctl00_ctlPanelBar_ctlViewArticleAttachments_ctl00_ctlViewAttachments_ctl00_ctlDataList')]#('div','i-tree')]
LAST_SCRAPE_DATE = ''
SORTED_SITE = False
DATE_TAG = []
DATE_FORM = ''



URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
prefix_length = len(URL_PREFIX)
    
if NEXT_TEXT == '':
    print ("ONE PAGE")
    one_page(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])
else:
    print ("MULTIPLE PAGES")
    multiple_pages(NEXT_TEXT, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, all_links = [URL], pdf_links = [], xlsx_links = [], links_visited = [])