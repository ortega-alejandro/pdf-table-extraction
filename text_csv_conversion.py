def text_list(text):
	'''
	Parameters:
	text is the object returned from opening the text file of the table
	
	Function that takes a file object and places it's lines in an array; also finds the max line length of the file.
	
	Return Values:
	lst is the array representation of the file
	max_length is the max line length in the file
	
	'''
	lst = []
    max_length = 0
    for line in text:
        lst.append(line)
        if len(line)>max_length:
            max_length = len(line)
    return lst, max_length

def find_spaces(text,regex_space):
	'''
	Parameters:
	text is the array representation of the table's text file
	regex_space is a regex for finding spaces
	
	function that finds spaces in the table based on regular expression parameter, and appends the regular expression match object for each line into an 
	array. These objects contain character positions that can be used as coordinates to place commas
	
	Return Values
	an array of arrays for regular expression match objects for each line
	'''
	data = []
    for line in text:
        spaces = []
        match = re.finditer(regex_space,line, re.S)
        for each in match:
            if each is not None:
                spaces.append((each.start(),each.end()))
        data.append(spaces)      
    return data

def get_columns(data):
	'''
	Parameters:
	data is an array of regular expression match objects for whitespace returned by find_spaces()
	
	function that determines columns in the table by first setting the number of columns to the largest length of spaces. 
	Then it iterates through the text file and adds the starting coordinate of the whitespace if it matches the number of 
	columns
	
	Return Values:
	columns, the number of columns
	max_column_arr, the array of starting corrdiantes of whitespace for lines that match the max number of columns
	'''
    columns = 0
    for each in data:
        if len(each)>columns and each[0][0] != 0:
            columns = len(each)
    if columns==0: # This is for the case that the table has white space to begin every row
        for each in data:
            if len(each)>columns:
                columns = len(each)
    arr = []
    max_column_arr = []
    for i in range(columns):
        max_column_arr.append(0)
    for each in data:
        if len(each) == columns:
            for i in range(len(each)):
                start,end = each[i]
                if start>max_column_arr[i]:
                    max_column_arr[i] = start
    return columns, max_column_arr

def find_top(data,columns):
	'''
	Parameters:
	data is an array of regular expression match objects for whitespace returned by find_spaces()
	coumns is th number of columns, returned by get_columns()
	
	function that finds the row where the headers end in the table begins by checking against the number of coumns.
	
	Return Values:
	i, the index of the table where the headers end
	'''
    for i in range(len(data)):
        if columns == 1:
            if len(data[i])>0:
                return i
        else:
            if len(data[i])>1:
                return i

def check_whitespace(text,points,top,max_length):
	'''
	Parameters:
	text is the array representation of the table returned by text_list()
	points is the array of starting coordinates for whitespace returned by get_columns
	top is the index returned by find_top
	max_length is the max line length in the table returned by text_list
	
	function that finds the coordinates to insert commas. Makes a call to checklines to ensure there is whitespace vertically 
	in all rows of the table.
	
	Return Values:
	real_points are the coordinates to insert commas in the text file. 
	'''
    print("top used: " + str(top))
    real_points = []
    for i in range(len(text)):
        line =text[i]
        if len(line)<max_length:
            line = line[:len(line)-1]+(' '*(max_length-len(line)-1))+line[len(line)-1] # Adds padding to the line if needed to avoid index out of bound
        text[i]=(line)
    for i in range(len(points)):
        index = points[i]
        while not check_lines(text,index,top):
            if index > max_length:
                break
            index = index+1
        real_points.append(index)
    return real_points
        
def check_lines(text,index,top):
	'''
	Parameters:
	text is the array representation of the table returned by text_list()
	index is the current index of the foor loop
	top is the index returned by find_top
	
	Checks that all columns have whites space in the specified index for insertion of commas.
	
	Return Values:
	check is a boolean value for whether there is whitespace in all columns at the specified index.
	'''
    check = False
    success = False
    if text[top][index-1:index+1] == '  ':
        success = True
    elif text[top][index:index+2] == '  ':
        success = True
    if success:
        for j in range(top+1,len(text)):
            if text[j][index] == ' ':
                check = True
                continue
            else:
                check = False
                break
    return check
    

def flag(points,real_points, top):
	'''
	Parameters:
	text is the array representation of the table returned by text_list()
	real_points is the array of points where commas are to be inserted
	top is the index returned by find_top
	
	function that produces a warning if there are duplicates in real_points, meaning whitespace could not be found and likely indicates stacked headers
	
	Return Values:
	The incremented top value
	boolean for whether a warning is warranted
	'''
    print("points: ")
    print(points)
    print("real points: ")
    print(real_points)
    warning = False 
    if len(set(real_points)) != len(points):
        warning = True
        warnings.warn("STACKED HEADERS, MANUAL CHECK")
        print("top: " + str(top))
        top += 1 
    return top, warning    
        
def convert(text,points,data, top):
	'''
	Parameters:
	text is the array representation of the table returned by text_list()
	points is the array of coordinates where commas are to be inserted
	data is an array of regular expression match objects for whitespace returned by find_spaces()
	top is the index returned by find_top
	
	function that inserts the commas into the lines of text and writes the lines to a CSV file, performing regex substitutions to remove extra 
	white space, character misencodings and other issues. 
	'''
    line_count = 0
    for line in text:
        if line_count < top or len(data[line_count])==0:          
            line = re.sub(',',' ',line)
            line = re.sub(regex_space,' ',line)
            final.write(line)
        else:
            line = re.sub("\n", "NEWLINE", line)
            line = re.sub(',',' ',line)
            line = write_line_with_commas(line,points)          
            line = re.sub(regex_space,' ',line)
            line = re.sub("NEWLINE", "\n", line)
            final.write(line)
        line_count+=1
        print (line)

def write_line_with_commas(line,points):
	'''
	Parameters:
	line is the current line of the text array
	points is the array of coordinates where commas are to be inserted
	
	function that inserts the commas into the lines of text, called by convert()
	'''
    for i in range(len(points)):
        number = points[i]
        if len(line) > number:
            if line[number] == ' ':
                line = line[:number]+','+line[number+1:]
    return line
        
def one_column(text):
	'''
	Parameters:
	text is the array representation of the table returned by text_list()
	
	if the table only has one column, then it can be written directly to CSV.
	'''
    for line in text:
        line = re.sub(',',' ',line)
        line = re.sub(regex_space,' ',line)
        final.write(line)
        print (line)
                
 