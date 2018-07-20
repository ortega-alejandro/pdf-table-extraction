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



URL = 'https://www.africa-eu-renewables.org/market-information/'
TAGS = [('div','box reveal'),('div','nav-wrap'),('div','container')]
SORTED_SITE = False


all_links = [URL]
links_visited = []
pdf_links = []
xlsx_links = []
URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
prefix_length = len(URL_PREFIX)


def tags(current, links, html_soup):
    for tag_type,tag in TAGS:
        links_page = html_soup.find_all(tag_type, class_ = tag)
        if len(links_page)==0:
            continue
        for each in links_page:
            links.append(each)
        print (links)
        if tag == "container":
            scrape_page_pdf(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
        else:
            scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
    return pdf_links, xlsx_links, links_visited, all_links

def scrape_page_pdf(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            pdf_url= link['href']
            if pdf_url[:4] != 'http':
                pdf_url = URL_PREFIX+str(pdf_url)
            if pdf_url not in links_visited:
                links_visited.append(pdf_url)
                if 'pdf' in pdf_url:
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
    if 'pdf' in current:
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    if current in all_links:
        all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links



def scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            pdf_url= link['href']
            if pdf_url[:4] != 'http':
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
    if current in all_links:
        all_links.remove(current)
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links

#page_num = 1
#while all_links:
    #pages = get_next_page(all_links, NEXT_TEXT, URL_PREFIX)
    
while all_links:
    current = all_links[0]
    response = get(current)
    html_soup = BeautifulSoup(response.text, 'lxml')
    
    pdf_links, xlsx_links, links_visited, all_links = tags(current, [], html_soup)
    
    #pdf_links, xlsx_links, links_visited, all_links = scrape_page(links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)

    #if len(pages)>0:
    #    all_links.append(pages)
    #    page_num+=1

    
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