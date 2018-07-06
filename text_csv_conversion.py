import re
import warnings

path = 'btest2.txt'
text = open(path,'r')
final = open('csvfile3.csv','w')
regex = '(\s\s)+[0-9]+'
regex_space = '([ ]{2,})+'


def text_list(text,lst):
    max_length = 0
    for line in text:
        lst.append(line)
        if len(line)>max_length:
            max_length = len(line)
    return lst, max_length

def find_spaces(text,regex,regex_space,data):
    for line in text:
        spaces = []
        match = re.finditer(regex_space,line, re.S)
        for each in match:
            if each is not None:
                spaces.append((each.start(),each.end()))
        data.append(spaces)      
    return data

def get_columns(data):
    columns = 0
    for each in data:
        if len(each)>columns and each[0][0] != 0:
            columns = len(each)
    if columns==0:
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
    for i in range(len(data)):
        if columns == 1:
            if len(data[i])>0:
                return i
        else:
            if len(data[i])>1:
                return i

def check_whitespace(text,points,top,max_length):
    print("top used: " + str(top))
    real_points = []
    for i in range(len(text)):
        line =text[i]
        if len(line)<max_length:
            line = line[:len(line)-1]+(' '*(max_length-len(line)-1))+line[len(line)-1]
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
    for i in range(len(points)):
        number = points[i]
        if len(line) > number:
            if line[number] == ' ':
                line = line[:number]+','+line[number+1:]
    return line
        
def one_column(text):
    for line in text:
        line = re.sub(',',' ',line)
        line = re.sub(regex_space,' ',line)
        final.write(line)
        print (line)
                
        
text, max_length = text_list(text,[])
data = find_spaces(text,regex,regex_space,[])
print("DATA")
for line in data:
    print (line)
columns, max_column_arr = get_columns(data)
print ('NUMBER OF COLUMNS')
print (columns)
print ('columns_arr')
print (max_column_arr)
print()
top = find_top(data,columns)
print ('top')
print (top)
print ()
if top is None:
    one_column(text)
else:
    points = check_whitespace(text,max_column_arr,top,max_length)
    print ('points')
    print (points)
    new_top, is_stacked = flag(max_column_arr,points, top)
    while True: 
        if not is_stacked:
            break
        print("new top: " + str(new_top))
        points = check_whitespace(text,max_column_arr,new_top,max_length) 
        new_top, is_stacked = flag(max_column_arr,points, new_top)
    print("final top: " + str(new_top))
    convert(text,points,data, new_top)
