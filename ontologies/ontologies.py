from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFTextExtractionNotAllowed, PDFPage
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from owlready2 import *
from nltk.stem.porter import *
import re
from nltk.stem.porter import *
import operator
from PyPDF2 import PdfFileReader
import pandas as pd



###################################### LOAD/PROCESS THE ONTOLOGY ##################################################


'''---------------------------------------REFERENCING OWL FILE ONTOLOGY---------------------------------------'''

#store all terms in the ontology into an array
#EXAMPLE: arr = [['Solar Home Systems'], ['RCT', 'Randomized Control Trials', 'Randomized Control Trials (RCT)'], ...]
#arr[i] contains the list of all synonyms
def populate_ontology_array():
    arr = []
    for i in onto.individuals():
        arr.append(i.label)  
    for i in onto.classes():
        arr.append(i.label)
    return arr


#boolean function to determine whether a word (synonym) is a preflabel
def is_pref_label(synonym):
    is_preflabel = len(onto.search(prefLabel = synonym)) 
    if (is_preflabel == 0):      
        return False
    return True

#returns the parent of a word as a string
def get_parent(word):
    parent = onto.search(label = word)      #query the ontology for word
    parent = parent[0].is_a[0]              #determines the parent of that word
    parent = parent.label
    return parent
    
'''---------------------------------------REFERENCING OWL FILE ONTOLOGY---------------------------------------'''

def initialize_stemmer():
    stemmer = PorterStemmer()
    return stemmer
 
#stem the ontology into arr_stemmed_ontology 
#arr_stemmed_ontology = dictionary = {key, value} = {original word, list of stemmed labels}
def ontology_dictionary(arr, stemmer):
    arr_stemmed_ontology = {}
    for term in arr: 
        real_label = ''       
        #CASE #1: term = ['preferred label', 'label 2', 'label 3', ...] (multiple labels for a term in ontology)
        if (len(term) > 1):  
            for synonym in term:
                if is_pref_label(synonym) == True:
                    real_label = synonym
                else:
                    continue
            if (real_label == ''):
                raise Exception(word + " has no preferred label")     
            for x in range(len(term)):
                arr_stemmed2 = ''
                word = term[x].split()
                for k in range(len(word)):
                    arr_stemmed2 = arr_stemmed2 + stemmer.stem(word[k].lower()) + " "   
                if (real_label not in arr_stemmed_ontology.keys()):
                    arr_stemmed_ontology[real_label] = []
                arr_stemmed_ontology[real_label].append(arr_stemmed2.strip()) 
        #CASE #2: term = ['only label']
        else:               
            real_label = term[0]
            arr_stemmed2 = ''
            word = real_label.split()
            for k in range(len(word)):
                arr_stemmed2 = arr_stemmed2 + stemmer.stem(word[k].lower()) + " "   
            if (real_label not in arr_stemmed_ontology.keys()):
                arr_stemmed_ontology[real_label] = []
            arr_stemmed_ontology[real_label].append(arr_stemmed2.strip())
    return arr_stemmed_ontology
        


    


#################################### FINDING MATCHES BETWEEN PDF AND ONTOLOGY #####################################


'''CREATE A FREQUENCY MATRIX WHERE:
    ROWS = PAGE NUMBER
    COLUMNS = ONTOLOGY
    CELLS = # OF TIMES A KEYWORD IN ONTOLOGY APPEARS ON PAGE __'''


#function to process pdf text, for each page
#result: remove irrelevant characters and all words are stemmed
def process_pdf(page_text, stemmer):
    page_text = re.sub("\.", "", page_text)
    page_text = re.sub("[0-9]+", "", page_text)
    page_text = re.sub("-\n", "", page_text)
    page_text = page_text.lower()
    page_text = re.sub("(\W+)", " ", page_text)
    page_text = re.sub("ﬁ", "fi", page_text)
    pdf_arr = page_text.split()
    pdf_arr_stemmed = []
    for i in range(len(pdf_arr)):
        pdf_arr_stemmed.append(stemmer.stem(pdf_arr[i]))
    page_text = " ".join(pdf_arr_stemmed)
    return page_text

#initialize frequency matrix
#Uses PDFMiner
def build_frequency_matrix(my_pdf, arr_stemmed_ontology, stemmer):
    frequency_matrix = []
    
    #set up document for PDFMiner
    fp = open(my_pdf, "rb")
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    #initialize page counter
    page_number = 0
    #variable to store processed text for the whole pdf document
    doc_text = ""
    
    for page in PDFPage.create_pages(document):
        #Create string of text both by page and append each page to create string of text for entire doc
        #variable to store processed text for each page
        page_text = ""
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                page_text += lt_obj.get_text()
                
        #process the text: stem all words
        page_text = process_pdf(page_text, stemmer)
        doc_text += page_text
        
        frequency_matrix.append([])
        for key in arr_stemmed_ontology.keys():
            #key = word (not stemmed)
            #synonym_list = stemmed list word/synonyms
            synonym_list = arr_stemmed_ontology[key]
            freq = 0
            
            #find number of occurance of all synonyms on a page
            #add this value to frequency_matrix at index of current page
            for syn in synonym_list:
                freq += len(re.findall(syn, page_text))
            frequency_matrix[page_number].append(freq)
            
        page_number += 1
        
    return frequency_matrix, doc_text

#converting frequency matrix into dataframe, renaming column headers
def convert_into_df(frequency_matrix, arr_stemmed_ontology):
    column_headers = []
    for key in arr_stemmed_ontology.keys():
        column_headers.append(key)
    frequency_matrix_df = pd.DataFrame(frequency_matrix, columns = column_headers)
    return frequency_matrix_df, column_headers







'''FIND MATCHES BETWEEN ONTOLOGY AND THE ENTIRE DOCUMENT WHERE:
    matches_count (dictionary) = {key,value} = {word, number of times each word appears in the entire document}
    matches_freq (dictionary) = {key,value} = {word, number of times each word appears in the entire document/total number of words in document}'''

def find_matches_wholedoc(doc_text, arr_stemmed_ontology, threshold):
    matches_count = {}
    matches_freq = {}

    #num_of_words = total number of relevant words in the document
    num_of_words = len(doc_text.split())

    for key in arr_stemmed_ontology.keys():
        regex = arr_stemmed_ontology[key]
        freq = 0
        for r in regex:      
            freq += len(re.findall(r, doc_text))
        #freq = number of times word appears in doc
        if (freq/num_of_words)*100 < threshold:
            continue 
        #build dictionary
        if key not in matches_count.keys():
            matches_count[key] = freq
            matches_freq[key] = round((freq/num_of_words)*100, 5)
        else:
            matches_count[key] += freq
            matches_freq[key] += round((freq/num_of_words)*100, 5)
    #Sort matches
    matches_count_sorted = sorted(matches_count.items(), key=operator.itemgetter(1), reverse=True)
    matches_freq_sorted = sorted(matches_freq.items(), key=operator.itemgetter(1), reverse=True)
    #initialize array of matches, sorted
    matches_sorted = [] 
    for i in range(len(matches_freq_sorted)):
        matches_sorted.append(matches_freq_sorted[i][0])
    return matches_sorted, matches_count, matches_freq, matches_freq_sorted







'''DISPLAY MATCHES, ON A PAGE BY PAGE BASIS:
    FIRST DICTIONARY: pmatches_by_page: {key, value} = {page #, frequent word appeareances according to page_threshold}
    SECOND DICTIONARY: pmatches_by_keyword: {key, value} = {matched word, pages that word appears on, in order of importance}'''

#Uses PYPDF2
def get_num_of_pages(my_pdf):
    pdf2 = PdfFileReader(open(my_pdf, 'rb'))
    num_of_pages = pdf2.getNumPages()
    return num_of_pages, pdf2

'''FIRST DICTIONARY'''

def build_first_dict(my_pdf, frequency_matrix, column_headers, page_threshold):
    pmatches_by_page = {}
    num_of_pages, pdf2 = get_num_of_pages(my_pdf)
    for p in range(num_of_pages):
        page = pdf2.getPage(p)
        num_of_words_page = (len(page.extractText()))
        pmatches_by_page[p] = []
        if (num_of_words_page == 0):
            continue
        for x in range(len(frequency_matrix[p])):     
            #frequency_matrix[p] is one row of df
            if (frequency_matrix[p][x]/num_of_words_page > page_threshold):
                    pmatches_by_page[p].append(column_headers[x])
    return pmatches_by_page

    
'''SECOND DICTIONARY'''
#inputs: matches_sorted = array of all matched keywords sorted by importance
#        frequency_matrix_df = dataframe (row headers = page numbers, column headers = words in ontology)
#        page_thresh = minimum threshold to determine relevancy on one page
def build_second_dict(matches_sorted, frequency_matrix_df, page_thresh):
    pmatches_by_keyword = {}
    pdf3 = PdfFileReader(open(my_pdf, 'rb'))
    for word in matches_sorted:   
        if word not in pmatches_by_keyword.keys():
            pmatches_by_keyword[word] = []
        col_headers = frequency_matrix_df.columns.values.tolist()
        #find column that matches specific word
        for position, header in enumerate(col_headers):
            if (header == word):
                column_num = position
        #page_list = list of occurances for a word by page
        page_list = frequency_matrix_df.iloc[:,column_num].tolist()
        freq_list = []
        #determine frequency for each page as opposed to count
        for index in range(len(page_list)):
            page = pdf3.getPage(index)
            num_of_words_page = (len(page.extractText()))
            freq = round((page_list[index]/num_of_words_page),5)
            if freq >= page_thresh:
                freq_list.append((index+1,freq))
        freq_list = sorted(freq_list, key=operator.itemgetter(1), reverse=True)
        #freq_list becomes value of dictionary
        pmatches_by_keyword[word] = freq_list
    return pmatches_by_keyword
      



###################################### FINDING PARENT CHAINS OF EACH KEYWORD ####################################

#recursive function to find the parent of a word
#word = word match found; TYPE = STRING 
def find_parent_chain(word, chain):        
    parent = get_parent(word)
    if len(parent) == 0:
        return 
    chain.insert(0, parent[0])
    find_parent_chain(parent[0], chain)

    
#finding all parent chains of all matched words
#matches_sorted = array of all matched keywords sorted by importance
def all_chains(matches_sorted):
    all_chains = []
    for keyword in matches_sorted: 
        parent_chain = [keyword]
        find_parent_chain(keyword, parent_chain)
        all_chains.append(parent_chain)
    return all_chains


'''TRAVERSE THROUGH THE TREE,
    PRINT OUT A SIMPLIFIED LIST OF PARENT CHAIN PATHS
    ie, A -> B -> C -> D
    [A, B, C] [A, B] -> ONLY [A, B, C] IS PRINTED'''


def traverse_tree(all_chains):
    root = Node()

    #initializing first layer of tree
    first_level = set([])
    for i in range(len(all_chains)):
        first_level.add(all_chains[i][0])
    root.createChildren(list(first_level))
    #create the rest of the tree
    root.add_children(1, all_chains)
    #traverse through the paths of the tree
    path = root.traverse([])
    return path


 ##########################################  CREATE TREE WITH PATHS   ###########################################

class Node(object):
    def __init__(self,data=''):
        self.visited = False
        self.data = data
        self.child = []
        
    def createNode(self, data):
        return Node(data)
    
    def createChildren(self,info):
        for i in range(len(info)):
            n = self.createNode(info[i])
            self.child.append(n)
    
    def add_children(self, count, all_chains): 
        for i in range(len(self.child)):
            kids = set([])
            for j in range(len(all_chains)):
                if (count >= len(all_chains[j])):
                    continue
                if (count < len(all_chains[j])):    
                    if (all_chains[j][count - 1] == self.child[i].data):
                        kids.add(all_chains[j][count])
            if (len(list(kids)) == 0):
                return
            self.child[i].createChildren(list(kids))
            self.child[i].add_children(count+1, all_chains)
          
    def traverse(self,local_path):
        path = []
        if (self.data is not ''):
            local_path.append(self.data)
        if len(self.child) != 0:
            for n in self.child:
                path.extend(n.traverse(local_path[:]))
        else:
            path.append(local_path)
        return path




################################ MAIN RUN FUNCTION ###############################################

def run(my_pdf, ontology_path, page_threshold=0.005, threshold=0.03, number_of_levels=3, print_output=True, print_debug=False):
    stemmer = initialize_stemmer()
    arr = populate_ontology_array()
    arr_dictionary = ontology_dictionary(arr, stemmer)
    frequency_matrix, doc_text = build_frequency_matrix(my_pdf, arr_dictionary, stemmer)
    frequency_matrix_df, column_headers = convert_into_df(frequency_matrix, arr_dictionary)
    pmatches_by_page = build_first_dict(my_pdf, frequency_matrix, column_headers, page_threshold)
    matches_sorted, matches_count, matches_freq, matches_freq_sorted = find_matches_wholedoc(doc_text, arr_dictionary, threshold)
    pmatches_by_keyword = build_second_dict(matches_sorted, frequency_matrix_df, page_threshold)
    all_chain = all_chains(matches_sorted)
    simplified_chains = traverse_tree(all_chain)
    
    if print_debug:
        print("Entire ontology: ")
        print(arr)    
        print("\nFrequency matrix: ")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            display(frequency_matrix_df) 
        print("\nStemmed ontology:")
        for key in arr_dictionary:
            print(key, arr_dictionary[key])       
        print("\nALL CHAINS: ")
        print ("Total number of chains: " + str(len(all_chains)))
        for i in all_chains:
            print(i)
    if print_output:
        print("\nMATCHED WORDS, FOR ENTIRE DOCUMENT: ")
        print("Total number of matched words: " + str(len(matches_sorted)))
        for word in matches_sorted:
            print (word + " appears "+ str(matches_count[word]) + " times with frequency " + str(matches_freq[word]))  
        print("\nMATCHES BY PAGE: ")
        for key in pmatches_by_page:
            print(str(key+1), pmatches_by_page[key])   
        print("\nMATCHES BY KEYWORD: ")
        for key in pmatches_by_keyword:
            print(key, pmatches_by_keyword[key])
        print("\nSIMPLIFIED CHAINS: ")
        print ("Total number of chains: "+str(len(simplified_chains)))
        for i in simplified_chains:
            print(i[:number_of_levels])
    
    return simplified_chains, matches_freq_sorted, pmatches_by_page, pmatches_by_keyword


my_pdf = "desktop/OneDrive_2018-05-27/ml/1A4098F8BD1AF9D0AEB01C96DB34FDC2FEB6E764.pdf"
ontology_path = "file:///users/brookeerickson/downloads/root-ontology-v9.owl"
onto = get_ontology(ontology_path).load()

run(my_pdf, ontology_path)

#keyword frequency threshold value, for the entire document automatically set to threshold = 0.03
#keyword frequency threshold value, for each page automatically set to page_threshold = 0.005
#number of levels of the ontology to display to the user automatically set to number_of_levels = 3
#print_output automatically set to True
#print_debug automatically set to False


