from bs4 import BeautifulSoup
from requests import get
import urllib.request
import datetime
import re

NEXT_TEXT = '>>'
URL = 'https://openknowledge.worldbank.org/recent-submissions'
TAGS = [('div', 'content author-info'), ('div', 'bitstream-link-wrapper')]
DATE_TAG = TAGS[0]
DATE_FORM1 = '(%Y)'
DATE_FORM2 = '(%Y-%m)'
DATE_FORM3 = '(%Y-%m-%d)'
LAST_SCRAPE_DATE = '(2018-01)'
SORTED_SITE = False


all_links = [URL]
links_visited = []
pdf_links = []
xlsx_links = []
URL_PREFIX = re.search('.*org/|.*com/|.*edu/', URL).group(0)
prefix_length = len(URL_PREFIX)



page_num = 1
while all_links:
    main_url = all_links[0]
    print (main_url)
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text=NEXT_TEXT)
    print('Page length ', len(pages))
    print('PAGE: '+str(page_num))
    if len(pages)>0:
        # pages = pages[0].find('a',href=True)
        pages = URL_PREFIX+pages[0]['href']
        # pages = URL_PREFIX+pages['href']
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
        links = []
        for tag_type, tag in TAGS:
            links_page = html_soup.find_all(tag_type, class_=tag)
            # print('Length of Links {}', len(links_page))
            if len(links_page) == 0:
                continue
            for each in links_page:
                # print(each)
                date = each.parent.find(DATE_TAG[0], class_=DATE_TAG[1])      # ###### OPENAFRICA,GOGLA ######
                # date = each.find(DATE_TAG[0],class_ = DATE_TAG[1])               # ###### WRI #######
                print("DATE")
                if date is not None:
                    date = date.text.split()[-1].strip()       # ###### OPENAFRICA #######
                    form = len(date.split('-'))
                    # #####date = date.text.strip()                  ########### WRI,GOGLA #########
                    print(date)
                    if form == 1:
                        date = datetime.datetime.strptime(date, DATE_FORM1).date()
                    elif form == 2:
                        date = datetime.datetime.strptime(date, DATE_FORM2).date()
                    elif form == 3:
                        date = datetime.datetime.strptime(date, DATE_FORM3).date()

                    last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE, DATE_FORM2).date()
                    if date >= last_date:
                        print('greater than')
                        links.append(each)
                    elif SORTED_SITE:
                        pages = ''
                        break
                else:
                    links.append(each)
        print(links)
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
    if len(pages) > 0:
        all_links.append(pages)
        page_num += 1
        if page_num == 3:
            break

    
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
