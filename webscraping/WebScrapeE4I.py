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


'''FUNCTION: GO THROUGH LIST OF TAGS AND ADD ALL LINKS TO A LIST
        OUTPUT: LIST OF HTML INFO ASSOCIATED WITH EACH TAG'''
def tags_by_date(TAGS, links, html_soup):
    for tag_type,tag in TAGS:
        #find all occurances of each html tag
        links_page = html_soup.find_all(tag_type, class_ = tag) 
        if len(links_page)==0:
            #if tag did not appear, continue to next tag
            continue
        for each in links_page:
            links.append(each)
    return links


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
                if 'file' in pdf_url:           #### IF FILE IN URL, IT IS A PDF
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
                else:
                    #add to all_links if it is not a pdf or xlsx
                    all_links.append(pdf_url)
    if 'file' in current:                       #### IF FILE IN URL, IT IS A PDF
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    #remove current url from all_links and add to links_visited
    all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links


'''FUNCTION: COMBINE ALL ABOVE FUNCTIONS IF WEBSITE ONLY HAS ONE PAGE
        OUTPUT: list of pdf_links and xlsx_links'''
def one_page(URL_PREFIX, prefix_length, TAGS, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE):
    #continue to repeat process while there are more links in the list all_links
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')

        links = tags_by_date(TAGS, [], html_soup)
        
        pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, prefix_length, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
            
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
def scrape_website(URL, TAGS, pdf_links = [], xlsx_links = [], links_visited = [], PRINT_MODE=True):
    
    URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
    prefix_length = len(URL_PREFIX)
    all_links = [URL]

    pdf_links, xlsx_links = one_page(URL_PREFIX, prefix_length, TAGS, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE)
    
    return pdf_links, xlsx_links
        

              
#################################################################################
URL = 'https://www.energy4impact.org/publications'
TAGS = [('div', 'o-btn btn--style-2')]

pdf_links, xlsx_links = scrape_website(URL, TAGS)


