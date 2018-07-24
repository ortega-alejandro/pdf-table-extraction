from bs4 import BeautifulSoup
from requests import get
import datetime
import re


'''FUNCTION: RETRIEVE WEBSITE INFORMATION FROM TEXTFILE
        INPUT: TEXTFILE NAME
        OUTPUT: URL, TAGS, SORTED_SITE, DATE_TAGS, DATE_FORM, NEXT_TEXT, LAST_SCRAPE_DATE '''
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


'''FUNCTION: PROCESS HTML TAGS
        OUTPUT: LIST OF TUPLES'''
def get_tags(line):
    tags = line.split('|')
    final_tags = []
    for tag in tags:
        final_tags.append(tag.split(','))
    return final_tags


'''FUNCTION: GET THE NEXT PAGE TO SCRAPE
        NOTE: only use this function when NEXT_TEXT is not ''
        '''
def get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX, PRINT_MODE):
    #main url is the homepage
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
            if len(DATE_TAG)>0:
                #if site has dates, determine if date associated with the link 
                #is before or after the last scraped date
                date = each.find(DATE_TAG[0],class_ = DATE_TAG[1])
                if date is not None:
                    date = date.text.strip()
                    date = datetime.datetime.strptime(date,DATE_FORM).date()
                    last_date = datetime.datetime.strptime(LAST_SCRAPE_DATE,DATE_FORM).date()
                    if date >= last_date:
                        links.append(each)
                    elif SORTED_SITE:
                        #if site is sorted and you have reached the last scraped date, pages = ''
                        pages=''
                        break
                else:
                    links.append(each)
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


'''FUNCTION: COMBINE ALL ABOVE FUNCTIONS IF WEBSITE ONLY HAS ONE MIN PAGE
        OUTPUT: list of pdf_links and xlsx_links'''
def one_page(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE):
   #continue to repeat process while there are more links in the list all_links
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')
    
        links, pages = tags_by_date(TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, [], html_soup, '')
    
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
  

'''FUNCTION: COMBINE ALL ABOVE FUNCTIONS IF WEBSITE HAS MULTIPLE PAGES
        OUTPUT: list of pdf_links and xlsx_links'''      
def multiple_pages(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE):
    page_num = 1
    while all_links:
        pages = get_next_page(page_num, all_links, NEXT_TEXT, URL_PREFIX, PRINT_MODE)
        
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
def scrape_website(TEXT_FILE, pdf_links = [], xlsx_links = [], links_visited = [], PRINT_MODE=False):
    URL, TAGS, SORTED_SITE, DATE_TAG, DATE_FORM, NEXT_TEXT, LAST_SCRAPE_DATE = get_url_attributes(TEXT_FILE)
    # print(DATE_TAG)
    URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
    prefix_length = len(URL_PREFIX)
    all_links = [URL]
    
    if NEXT_TEXT == '':
        print ("ONE PAGE")
        pdf_links, xlsx_links = one_page(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE)
    else:
        print ("MULTIPLE PAGES")
        pdf_links, xlsx_links = multiple_pages(NEXT_TEXT, prefix_length, URL_PREFIX, TAGS, DATE_TAG, DATE_FORM, LAST_SCRAPE_DATE, SORTED_SITE, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE)

    return pdf_links, xlsx_links


TEXT_FILE = 'ruralelec.txt'

pdf_links, xlsx_links = scrape_website(TEXT_FILE)

