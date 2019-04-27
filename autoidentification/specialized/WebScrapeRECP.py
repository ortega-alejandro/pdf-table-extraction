from bs4 import BeautifulSoup
from requests import get
import re


'''FUNCTION: GO THROUGH LIST OF TAGS AND ADD ALL LINKS TO A LIST
        NOTE: THIS FUNCTION CALLS SCRAPE_PAGE FOR EVERY TAG
        OUTPUT: LIST OF HTML INFO ASSOCIATED WITH EACH TAG'''
def tags_by_date(TAGS, links, html_soup, current, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links):
    for tag_type,tag in TAGS:
        #find all occurances of each html tag
        links_page = html_soup.find_all(tag_type, class_ = tag)
        if len(links_page)==0:
            #if tag did not appear, continue to next tag
            continue
        for each in links_page:
            links.append(each)
        #MUST CALL SCRAPE_PAGE FOR EACH TAG SINCE THE TAG IS RELEVANT TO WHICH LINKS ARE PDFS
        pdf_links, xlsx_links, links_visited, all_links = scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links, tag, TAGS) ####RECP
    return pdf_links, xlsx_links, links_visited, all_links


'''FUNCTION: FIND ALL ANCHOR TAGS IN EACH OBJECT OF LINKS
        NOTE: ONLY ADD LINKS TO ALL_LINKS UNDER CERTAIN CONDITIONS
        INPUT: LINKS, TAG, TAGS
        OUTPUT: PDF_LINKS, XLSX_LINKS, LINKS_VISITED, ALL_LINKS'''
def scrape_page(current, links, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links, tag, TAGS):  ##tag, TAGS parameters RECP
    for each in links:
        #find all anchor tags and url's
        anchor_tags = each.find_all('a',href=True)
        for link in anchor_tags:
            pdf_url= link['href']
            if pdf_url[:4] != 'http':
                #append URL_PREFIX if the link does not begin with http already
                pdf_url = URL_PREFIX+str(pdf_url)
            if pdf_url not in links_visited:
                #only use link if it has not already been visited
                links_visited.append(pdf_url)
                if 'pdf' in pdf_url:
                    pdf_links.append(pdf_url)
                elif 'xlsx' in pdf_url:
                    xlsx_links.append(pdf_url)
                if tag == TAGS[0][1]:
                    #ADD TO ALL_LINKS
                    #if you are on the main page
                    all_links.append(pdf_url)
                elif tag == TAGS[1][1]:
                    #ADD TO ALL_LINKS
                    #if you are on the second page of the depth-first search and the word 'link' is in the url
                    if 'link' in pdf_url:
                        all_links.append(pdf_url)
    if 'pdf' in current:
        pdf_links.append(current)
    elif 'xlsx' in current:
        xlsx_links.append(current)
    if current in all_links:
        all_links.remove(current)
    #add current link to links_visited
    links_visited.append(current)
    return pdf_links, xlsx_links, links_visited, all_links


'''FUNCTION: COMBINE ALL ABOVE FUNCTIONS IF WEBSITE ONLY HAS ONE PAGE
        OUTPUT: list of pdf_links and xlsx_links'''
def one_page(URL_PREFIX, TAGS, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE):
    #continue to repeat process while there are more links in the list all_links
    while all_links:
        current = all_links[0]
        response = get(current)
        html_soup = BeautifulSoup(response.text, 'lxml')

        pdf_links, xlsx_links, links_visited, all_links = tags_by_date(TAGS, [], html_soup, current, URL_PREFIX, pdf_links, xlsx_links, links_visited, all_links)
            
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
def scrape_website(URL, TAGS, pdf_links = [], xlsx_links = [], links_visited = [], PRINT_MODE=False):

    URL_PREFIX = re.search('.*org/|.*com/|.*edu/',URL).group(0)
    prefix_length = len(URL_PREFIX)
    all_links = [URL]

    pdf_links, xlsx_links = one_page(prefix_length, URL_PREFIX, TAGS, all_links, pdf_links, xlsx_links, links_visited, PRINT_MODE)
       
    return pdf_links, xlsx_links
        
              
#################################################################################
    

URL = 'https://www.africa-eu-renewables.org/market-information/'
TAGS = [('div','box reveal'),('div','nav-wrap'),('div','container')]
    
pdf_links, xlsx_links = scrape_website(URL,TAGS)