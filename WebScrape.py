#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:20:47 2018

@author: brookeerickson
"""

from bs4 import BeautifulSoup
from requests import get
import urllib.request
import re

#url = 'http://energyaccess.org/resources/publications/'
#TAGS = ['list-content items-list']
#url = 'http://www.undp.org/content/undp/en/home/library.html?start=0&sort=date&view=cards&tag=topics:energy/energy-access'
#TAGS = ['library-card-image','small-12 medium-8 columns','docDownloads']
url = 'https://policy.practicalaction.org/resources/publications/collection/energy'
TAGS = [('div','list_item_content'),('ul','link')]

all_links = [url]
links_visited = []
pdf_links = []
xlsx_links = []
URL_PREFIX = re.search('(.*org/|.*com/|.*edu/)',url).group(0)
prefix_length = len(URL_PREFIX)


while all_links:
    main_url = all_links[0]
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text = 'Next »')
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
            links+=links_page
        for each in links:
            pdf_ = each.find_all('a',href=True)
            for link in pdf_:
                pdf_url= link['href']
                if pdf_url[:prefix_length] != URL_PREFIX:
                    pdf_url = URL_PREFIX+str(pdf_url)
                if pdf_url not in links_visited:
                    if pdf_url[-4:] == '.pdf':
                        pdf_links.append(pdf_url)
                        links_visited.append(pdf_url)
                    elif pdf_url[-5:] == '.xlsx':
                        xlsx_links.append(pdf_url)
                        links_visited.append(pdf_url)
                    else:
                        all_links.append(pdf_url)
                        links_visited.append(pdf_url)
        if current[-4:] == '.pdf':
            pdf_links.append(current)
        elif current[-5:] == '.xlsx':
            xlsx_links.append(current)
        all_links.remove(current)
        links_visited.append(current)
    if len(pages)>0:
        all_links.append(pages)

    
print ('all_links')
print (all_links)
print ('links_visited')
print (links_visited)
print ('pdf_links')
print (len(pdf_links))
for i in pdf_links:
    print (i)
print ('xlsx_links')
print (len(xlsx_links))
#urllib.request.urlretrieve(pdf_url,'energy_crisis_recovery.pdf')


'''url = 'http://www.undp.org/content/undp/en/home/librarypage/environment-energy/low_emission_climateresilientdevelopment/derisking-renewable-energy-investment/drei-tunisia.html'
TAGS = ['library-card-image','docDownloads']
all_links = [url]
links_visited = []
pdf_links = []
URL_PREFIX = re.search('(.*org/|.*com/|.*edu/)',url).group(0)
prefix_length = len(URL_PREFIX)

response2 = get(url)
html_soup_2 = BeautifulSoup(response2.text, 'html.parser')
links = []
for tag in TAGS:
    links += html_soup_2.find_all('div', class_ = tag)
for each in links:
    pdf_ = each.find_all('a',href=True)
    for link in pdf_:
        pdf_url= link['href']
        if pdf_url[:prefix_length] != URL_PREFIX:
            pdf_url = URL_PREFIX+str(pdf_url)
        if pdf_url not in links_visited:
            if pdf_url[-4:] == '.pdf':
                pdf_links.append(pdf_url)
                links_visited.append(pdf_url)
            else:
                all_links.append(pdf_url)
                links_visited.append(pdf_url)
if url[-4:] == '.pdf':
    pdf_links.append(url)
all_links.remove(url)
links_visited.append(url)


print ('all_links')
print (all_links)
print ('links_visited')
print (links_visited)
print ('pdf_links')
print (len(pdf_links))
for i in pdf_links:
    print (i)'''