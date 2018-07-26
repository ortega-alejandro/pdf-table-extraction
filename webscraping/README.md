# Data Virtualization
## Python Packages:
* BeautifulSoup
## Documentation
The function `scrape_website(text_file)` in `WebScrapeGeneral.py` takes in a text_file that contains information required to scrape PDF links, namely:
* the HTML text for the link that directs to the next page, or `""` if all documents are on a single page
* the main URL for documents
* the HTML tags and CSS classes used to identify document links; if multiple pages are needed to access the links from the main URL then the tags and classes for each page are placed in a list. Typically, most sites have a list of size one or two
* 0 or 1 for whether the site's documents are sorted by date. If so, then only the documents added since the last scrape have to be processed
* The HTML tags and CSS classes used to identify the date a document was uploaded.
* The format of dates on the site so that date comparisons via Python's DateTime module can be completed
* The last scrape date, which will be updated in the text file after the code is run (hopefully)

Using the information in the text file, `scrape_website()` returns lists of all links that end in .pdf or .xslx, which are then fed into the binary classifier to determine relevancy. Although we have seen links to pdf's that do not end in the .pdf extension, there is typically no way to differentiate these links from other ones. Given that difficulty and their overall rarity, we have not tried to add those links.

For the `WebScrape<Site-Name>.py` files, these sites have minor deviations that require changes to the general webscraping algorithm. For these files, calling `scrape_website(<PARAMETERS>)` with the URL, TAGS and other parameters as nececssary for that particular site.

