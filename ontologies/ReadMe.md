# Document Auto-Categorization

## Python Packages:
* PDFMiner 
* PyPDF2
* OwlReady2
* NLTK
* Pandas

## Documentation:
The function run(my_pdf, ontology_path) takes in a path to a PDF as a string and a path to an ontology (owl file) as a string. The algorithm locates all occurances of any word in the ontology in the PDF given as input. Based on a threshold, these words are determined as relevant or irrelevant by the optional parameter threshold. Using a tree structure, it determines the parent chains for each relevant keyword according to the ontology. The length of the parent chains is determined by the optional parameter number_of_levels. All parent words are also considered relevent.

The function ontology_dictionary(arr, stemmer) converts the ontology array (as shown below in Ontology Structure) into a dictionary of the form:

arr_stemmed_ontology = dictionary = {key, value} = {preferred label, list of stemmed alternate labels}

The function build_frequency_matrix(my_pdf, arr_stemmed_ontology, stemmer) creates a frequency matrix which is then converted into a pandas dataframe. This dataframe has words as column headers and page numbers as row headers.

The algorithm first finds word frequency for the entire document then continues to analyze the document page-by-page. Keywords are determined to be relevent on a page by the optional parameter page_threshold. The page-by-page analysis consists of 2 dictionaries shown below:

dictionary = {key, value} = {page number, list of most relevant keywords on that page in descending order of frequency}

dictionary = {key, value} = {keyword, list of most relevent pages for that keyword in descending order of frequency}

### Optional parameters include:
* page_threshold=0.005
* threshold=0.03
* number_of_levels=3

### Ontology Structure:
The algorithm currently runs on an owl file ontology, but will work for any ontology structure. To change the structure, only change the code between the '----REFERENCING OWL FILE ONTOLOGY----' headers. At the end of this section, the ontology should be stored in an array as follows:
  arr = [['term_1_label_1'], ['term_2_label_1', 'term_2_label_2', 'term_2_label_3'], ...]
  note: arr[i] contains the list of all labels for that term
