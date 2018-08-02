import cv2
import numpy as np
import re
import subprocess
from PIL import Image as im
from pdfminer.pdfpage import PDFPage
from PyPDF2 import PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
regex = "^(?!\s)(Table|Annex|TABLE)\s+([1-9]+[A-Z]?|[A-Z]?)\.?:?\s?"


def pdf_setup(src="sample.pdf"):
    # set up: organize PDF to use with PDFMiner
    fp = open(src, 'rb')
    parser = PDFParser(fp)
    # determine number of pages and dimensions pdf
    pdf = PdfFileReader(open(src, 'rb'), strict=False)
    num = pdf.getNumPages()
    return pdf, num


'''FUNCTION: FIND DIMENSIONS OF PDF AND JPG BY PAGE'''


def find_dimensions(pdf_file, page_no, src='../output/img/'):
    file = im.open(src + 'image-' + str(page_no) + '.jpg')
    jpg_width, jpg_height = file.size
    page = pdf_file.getPage(page_no).mediaBox
    # page is structured as (0, 0, width, height)
    pdf_width = int(page[2])
    pdf_height = int(page[3])
    return jpg_width, jpg_height, pdf_width, pdf_height


'''FUNCTION: CONVERT COORDINATES FROM JPG TO PDF'''


# returns converted coordinates (PDF Form)


def convert(x1, y1, x2, y2, jpg_width, jpg_height, pdf_width, pdf_height):
    x1_pdf = (x1 / jpg_width) * pdf_width
    y1_pdf = (y1 / jpg_height) * pdf_height
    x2_pdf = (x2 / jpg_width) * pdf_width
    y2_pdf = (y2 / jpg_height) * pdf_height
    return x1_pdf, y1_pdf, x2_pdf, y2_pdf


'''FUNCTION: PARSE THROUGH PDF TO FIND ALL TABLE HEADERS BY REGEX'''


# returns a list of the top coordinates of each table header on the page and the number of tables on that page


def find_table_headers(layout, pdf_height, regex_string, print_mode=False):
    top_coords = []
    tables = 0
    for lt_obj in layout:
        # goes through the document by textbox objects
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # if the object is a textbox or line, look for regex
            text = lt_obj.get_text()
            result = re.search(regex_string, text)
            if result is None:
                continue
            # found the regex in that box object
            if print_mode:
                print(text)
            tables += 1
            l, b, r, top = lt_obj.bbox
            top = pdf_height - top
            top_coords.append(top)
            # top_coords is an array of the top coordinates of each table header on a page
        elif isinstance(lt_obj, LTFigure):
            # if the object is a figure, recursively parse through the figure
            find_table_headers(lt_obj, pdf_height, regex_string)
    return top_coords, tables


'''FUNCTION: IMPLEMENTS FIND_TABLE_HEADERS BY PAGE'''


# inputs page number
# returns top coordinates array of tbale headers and number of tables on that page


def find_tables(src, page_num, pdf_height):
    fp = open(src, 'rb')
    page = PDFPage.get_pages(fp, pagenos=[page_num])
    for p in page:
        interpreter.process_page(p)
    layout = device.get_result()
    arr, tables_per_page = find_table_headers(layout, pdf_height, regex)
    return tables_per_page, arr


'''FUNCTION: FIND LINES AND COORDINATES OF THOSE LINES BY PAGE'''


# returns array of coordinates of all lines on a page and number of total lines


def get_lines(page_no, lines, line_image, img, jpg_width, jpg_height, pdf_width, pdf_height, linefile_name):
    lines_arr = []
    num_lines = 0
    if lines is not None:
        # lines is an array of all lines detected using computer vision
        num_lines = len(lines)
        for line in lines:
            for x1, y1, x2, y2 in line:
                # draw the line onto line_image by coordinates
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 5)
                # convert coordinates from jpg to pdf
                new_coords = convert(x1, y1, x2, y2, jpg_width, jpg_height, pdf_width, pdf_height)
                lines_arr.append(new_coords)
        lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
        # write the jpg file with lines drawn onto it
        cv2.imwrite(linefile_name + str(page_no) + '.jpg', lines_edges)
    # sorts lines by y coordinates (top of page to bottom of page)
    lines_arr = sorted(lines_arr, key=lambda x: x[1])
    return lines_arr, num_lines


'''FUNCTION: DETERMINE BOX COORDINATES OF A TABLE'''


# combines data from top coordinates (table headers) and line coordinates to give an overall box around the table
# returns bottom, top, left, right coordinates


def find_table_coords(top_coords, line_coords, line_count, table_header_count):
    # line_coords is structured as (x1, y1, x2, y2)
    # horizontal lines: y1=y2
    bottom = line_coords[line_count - 1][1]
    top = top_coords[table_header_count]
    left = line_coords[line_count - 1][0]
    right = line_coords[line_count - 1][2]
    return bottom, top, left, right


'''FUNCTION: PRINT OUT COORDINATES'''


def print_details(table_header_count, left, right, top, bottom, width, height):
    print("table " + str(table_header_count) + " coordinates :")
    print("left: " + str(left))
    print("right: " + str(right))
    print("bottom: " + str(bottom))
    print("top: " + str(top))
    print("width: " + str(width))
    print("height: " + str(height))


'''FUNCTION: IMAGE PRE-PROCESSING'''


def image_processing(src, page_no, kernel_size):
    # read in jpg by page
    img = cv2.imread(src + 'image-' + str(page_no) + '.jpg')
    # convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur the image slightly (improves line detection)
    blur = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    # detect outlines/edges of all lines and words
    edges = cv2.Canny(blur, 50, 150)
    # line_image is a copy of the image on which to later print the detected horizontal lines
    line_image = np.copy(img) * 0
    return img, edges, line_image


'''FUNCTION: CREATE TEXT FILE USING COORDINATES OF TABLE'''


def pdftotext(pdf_file, text_file, table, left, top, width, height, table_number):
    output = text_file + str(table_number) + ".txt"
    subprocess.call(["pdftotext", "-f", str(table), "-l", str(table), "-x", str(int(left)), "-y", str(int(top)), "-W",
                     str(int(width)), "-H", str(int(height)), "-layout", pdf_file, output])


'''FUNCTION: LAST TABLE OF THE PAGE OR PAGE WITH ONLY ONE TABLE'''


# creates a text file for that table
# returns table_count


def one_table(pdf_file, page_no, num_lines, top_coords, line_coords, line_count, table_header_count, table_count,
              text_file, print_mode=False):
    # PRINT BOX COORDINATES: TOP - REGEX, LEFT & RIGHT & BOTTOM - LAST LINE OF TABLE
    # go to the last line
    line_count = num_lines
    bottom, top, left, right = find_table_coords(top_coords, line_coords, line_count, table_header_count)
    width = right - left
    height = bottom - top
    if print_mode:
        print_details(table_header_count, left, right, top, bottom, width, height)
    table_header_count += 1
    # IF NEGATIVE HEIGHT OR WIDTH, CONTINUE TO NEXT REGEX (NOT A TABLE)
    if height < 0 or width < 0:
        if print_mode:
            print("not a table")
            print()
        return table_count
    # CREATE TEXT FILE BASED ON COORDINATES
    pdftotext(pdf_file, text_file, page_no + 1, left, top, width, height, table_count)
    # INCREASE TABLE COUNT AND LINE COUNT
    table_count += 1
    return table_count


'''FUNCTION: PAGE WITH MULTIPLE TABLES'''


# creates a text file for each table
# returns counts for table headers, lines, and total tables to use as a starting point for the next table


def multiple_tables(pdf_file, page_no, line_count, top_coords, line_coords, table_header_count, table_count,
                    text_file, print_mode=False):
    bottom, top, left, right = find_table_coords(top_coords, line_coords, line_count, table_header_count)
    width = right - left
    height = bottom - top
    if print_mode:
        print_details(table_header_count, left, right, top, bottom, width, height)
    table_header_count += 1
    # IF NEGATIVE HEIGHT OR WIDTH, CONTINUE TO NEXT REGEX
    if height < 0 or width < 0:
        if print_mode:
            print("not a table")
            print()
        return table_header_count, table_count, line_count
    # CREATE TEXT FILE BASED ON COORDINATES
    pdftotext(pdf_file, text_file, page_no + 1, left, top, width, height, table_count)
    # INCREASE TABLE COUNT AND LINE COUNT
    table_count += 1
    line_count += 1
    return table_header_count, table_count, line_count


# input = kernel_size, rho, theta, threshold, minLineLength, maxLineGap
# returns number of tables in the whole document
def detect_tables(src, dst='../output/txt/', image='../output/img/', kernel_size=5, rho=1, theta=np.pi / 2, threshold=50, min_line_length=500,
                  maxLineGap=1, file='temp', debug=False):
    fp, num = pdf_setup(src)
    table_count = 0
    for page_no in range(num):
        # '''FIND DIMENSIONS OF PAGE'''
        jpg_width, jpg_height, pdf_width, pdf_height = find_dimensions(fp, page_no)

        '''IMAGE PRE-PROCESSING FOR HOUGHLINE DETECTION'''
        img, edges, line_image = image_processing(image, page_no, kernel_size)

        '''FIND TABLES ON EACH PAGE BY REGEX'''
        number_of_tables, top_coords = find_tables(src, page_no, pdf_height)

        '''FIND AND DRAW LINES'''
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, maxLineGap)
        linefile_name = '../output/img/houghlines'
        line_coords, num_lines = get_lines(page_no, lines, line_image, img, jpg_width, jpg_height, pdf_width,
                                           pdf_height, linefile_name)

        '''PRINT PAGE INFORMATION'''
        if debug:
            print("page " + str(page_no + 1))
            print("JPG width: " + str(jpg_width))
            print("JPG height: " + str(jpg_height))
            print("PDF width: " + str(pdf_width))
            print("PDF height: " + str(pdf_height))
            print("number of tables: " + str(number_of_tables))
            print("table headings: ")
            print(top_coords)
            print("lines:")
            print(line_coords)
            print("total lines: " + str(num_lines))

        '''EACH PAGE HAS 3 POSSIBLE CASES: MORE THAN 1 TABLE, 1 TABLE, NO TABLE'''
        # Beginning of page: set table header and line counts to 0
        table_header_count = 0
        line_count = 0
        '''MORE THAN ONE TABLE ON A PAGE'''
        if number_of_tables > 1 and num_lines > 0:
            while line_count < num_lines:
                if table_header_count > number_of_tables - 1:
                    # BEYOND LAST TABLE HEADER
                    break
                if table_header_count == number_of_tables - 1:
                    # LAST TABLE HEADER
                    table_count = one_table(src, page_no, num_lines, top_coords, line_coords, line_count,
                                            table_header_count, table_count, dst + file)
                    break
                else:
                    # ANY TABLE HEADER EXCEPT THE LAST
                    line_count_before_loop = line_count
                    # loop through lines to get to the last line of a table
                    # last line detected by: y-coordinate of line is greater than the table header top coordinate and
                    # y-coordinate of line is less than top coordinate of next table header
                    while (line_count < num_lines and line_coords[line_count][3] > top_coords[table_header_count] and
                           line_coords[line_count][3] < top_coords[table_header_count + 1]):
                        line_count += 1
                    if line_count == line_count_before_loop:
                        # if there are no lines between 2 table headers, it is not a table
                        # likely this regex was found inside the text
                        table_header_count += 1
                        if debug:
                            print("not a table")
                            print()
                    else:
                        table_header_count, table_count, line_count = multiple_tables(src, page_no, line_count,
                                                                                      top_coords, line_coords,
                                                                                      table_header_count, table_count,
                                                                                      dst + file)

        '''PAGE ONLY HAS ONE TABLE'''
        if number_of_tables == 1 and num_lines > 0:
            table_count = one_table(src, page_no, num_lines, top_coords, line_coords, line_count, table_header_count,
                                    table_count, dst + file)

        '''PAGE HAS NO TABLES'''
        if number_of_tables < 1:
            if debug:
                print("no tables")
            continue

    if debug:
        print("TOTAL TABLES: " + str(table_count))
    return table_count
