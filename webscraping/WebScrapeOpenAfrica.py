#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:20:47 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import datetime
import re


'''FUNCTION: GET THE NEXT PAGE TO SCRAPE
        NOTE: only use this function when NEXT_TEXT is not ''
        '''
def get_next_page(all_links, page_num, NEXT_TEXT, URL_PREFIX, PRINT_MODE):
    #first page: tag is of type class
    main_url = all_links[0]
    response = get(main_url)
    #use BeautifulSoup to create an html_soup object
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text = NEXT_TEXT)
    if PRINT_MODE:
        print ('PAGE: '+str(page_num))
        print (main_url)
    #if there are no more pages, pages = ''
    if len(pages)>0:
        pages = URL_PREFIX+pages[0]['href']
    return pages


'''FUNCTION: GO THROUGH LIST OF TAGS AND ADD ALL LINKS TO A LIST
        OUTPUT: LIST OF HTML INFO ASSOCIATED WITH EACH TAG, PAGES = NEXT PAGE'''
def tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, links, html_soup, pages):
    for tag_type,tag in TAGS:
        #find all occurances of each html tag
        links_page = html_soup.find_all(tag_type, class_ = tag) 
        if len(links_page)==0:
            #if tag did not appear, continue to next tag
            continue
        for each in links_page:
            #determine if date associated with the link is before or after the last scraped date
            date = each.find(DATE_TAG[0],class_ = DATE_TAG[1])
            if date is not None:
                #process date to remove "uploaded"
                date = date.text.split('|')[0][8:].strip()       ####### OPENAFRICA #######
                date = datetime.datetime.strptime(date,DATE_FORM).date()
                last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE,DATE_FORM).date()
                if date>=last_date:
                    links.append(each)
                elif SORTED_SITE:
                    #if site is sorted and you have reached the last scraped date, pages = ''
                    pages=''
                    break
            else:
                links.append(each)
    return links, pages


'''FUNCTION: FIND ALL ANCHOR TAGS IN EACH OBJECT OF LINKS
        INPUT: LINKS
        OUTPUT: PDF_LINKS, XLSX_LINKS, LINKS_VISITED, ALL_LINKS'''
def scrape_page(current, links, prefix_length, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        #find all anchor tags and url's
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            pdf_url= link['href']
            if pdf_url[:prefix_length] != URL_PREFIX:
                #append URL_PREFIX if necessary
                pdf_url = URL_PREFIX+str(pdf_url)
            if pdf_url not in links_visited:
                #only use link if it has not already been visited
                links_visited.append(pdf_url)
                if 'pdf' in pdf_url:
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
                else:
                    #add to all_links if it is not a pdf or xlsx
                    all_links.append(pdf_url)
    if 'pdf' in current:
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    #remove current url from all_links and add to links_visited
    all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links


'''FUNCTION: COMBINE ALL ABOVE FUNCTIONS IF WEBSITE HAS MULTIPLE PAGES
        OUTPUT: list of pdf_links and xlsx_links''' 
def multiple_pages(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE):
    page_num = 1
    while all_links:
        pages = get_next_page(all_links, page_num, NEXT_TEXT, URL_PREFIX, PRINT_MODE)
        
        while all_links:
            current = all_links[0]
            response = get(current)
            html_soup = BeautifulSoup(response.text, 'lxml')
            
            links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, [], html_soup, pages)
    
            pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, prefix_length, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
       
        if len(pages)>0:
            #append next link to all_links
            all_links.append(pages)
            page_num+=1
    if PRINT_MODE:
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
        
    return pdf_links, xlsx_links
        

'''FUNCTION: SCRAPE THE WEBSITE'''
def scrape_website(NEXT_TEXT, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, pdf_links = [], xlsx_links = [], links_visited = [], PRINT_MODE=True):
    
    URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
    prefix_length = len(URL_PREFIX)
    all_links = [URL]

    pdf_links, xlsx_links = multiple_pages(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE)

    return pdf_links, xlsx_links

#################################################################################    

NEXT_TEXT = 'next ›'
URL = 'https://africaopendata.org/dataset'
TAGS = [('h5','dataset-heading'),('ul','resource-list'),('div','actions')]
LAST_SCRAPE_DATE = 'May 20, 2018'
SORTED_SITE = True
DATE_TAG = ('div','dataset-date')
DATE_FORM = '%B %d, %Y'

pdf_links, xlsx_links = scrape_website(NEXT_TEXT, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE) 


