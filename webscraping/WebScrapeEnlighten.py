from bs4 import BeautifulSoup
from requests import get
import urllib.request
import datetime
import re

NEXT_TEXT = 'More'
URL = 'https://united4efficiency.org/resources/publications/'
TAGS = [('div', 'featured-img'), ('div', 'entry-content')]
LAST_SCRAPE_DATE = 'Dec 31, 2017'
SORTED_SITE = True
DATE_TAG = ('div', 'list-content items-list')
DATE_FORM = '%b %d, %Y'

all_links = [URL]
links_visited = []
pdf_links = []
xlsx_links = []
URL_PREFIX = re.search('.*org/|.*com/|.*edu/', URL).group(0)
prefix_length = len(URL_PREFIX)


def get_next_page(all_links, NEXT_TEXT, URL_PREFIX):
    main_url = all_links[0]
    print(main_url)
    response = get(main_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    pages = html_soup.find_all('a', text=NEXT_TEXT)
    print('PAGE: ' + str(page_num))
    if len(pages) > 0:
        pages = URL_PREFIX + pages[0]['href']
    print(pages)
    return pages


def tags_by_date(TAGS, DATE_TAG, DATE_FORM, links, html_soup, pages):
    for tag_type, tag in TAGS:
        links_page = html_soup.find_all(tag_type, class_=tag)
        if len(links_page) == 0:
            continue
        for each in links_page:
            '''date = each.find(DATE_TAG[0], class_=DATE_TAG[1])
            print("DATE")
            print(date)
            if date is not None:
                date = date.text.strip()
                date = datetime.datetime.strptime(date, DATE_FORM).date()
                last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE, DATE_FORM).date()
                if date >= last_date:
                    links.append(each)
                elif SORTED_SITE:
                    pages = ''
                    break
            else:
                links.append(each)'''
            links.append(each)
    return links, pages


def scrape_page(links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for each in links:
        anchor_tags = each.parent.find_all('a', href=True)
        for link in anchor_tags:
            pdf_url = link['href']
            if pdf_url[:prefix_length] != URL_PREFIX:
                pdf_url = URL_PREFIX + str(pdf_url)
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
    return pdf_links, xlsx_links, links_visited, all_links


page_num = 1
while all_links:
    pages = get_next_page(all_links, NEXT_TEXT, URL_PREFIX)

    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
        print(html_soup)
        links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, [], html_soup, pages)
        print(links)

        pdf_links, xlsx_links, links_visited, all_links = scrape_page(links, URL_PREFIX, pdf_links, xlsx_links,
                                                                      links_visited, all_links)

    if len(pages) > 0:
        all_links.append(pages)
        page_num += 1

print('all_links')
print(all_links)
print('links_visited')
print(len(links_visited))
print(links_visited)
print('pdf_links')
print(len(pdf_links))
for i in pdf_links:
    print(i)
print('xlsx_links')
print(len(xlsx_links))
for i in (xlsx_links):
    print(i)
