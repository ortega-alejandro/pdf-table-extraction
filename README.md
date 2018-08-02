# Project 24
## Dependencies
* ImageMagick
* GhostScript
## Python Packages
* PdfMiner
* PyPdf2
* cv2
* PIL
* Wand

## Documentation
The functions `convert_pdf(pdf_path)`, `detect_tables(pdf_path)` and `convert_all()` perform the table extraction. 

The `detect_tables` function has the following parameters:
* `src` is the filepath of the PDF
* `dst` is  where the extracted text files will be placed; by default set to `'../output/txt/', image='`
* `image` is the directory where HoughLine images will be  stored; by default set to `'../output/img/'`
* `kernel_size`, `rho`, `theta`, `threshold`, `min_line_length`, `maxLineGap` are optional parameters that are used in the Hough Line detection algorithm. By default, they are set to the values we found most generalizable.
* `file` is the name of the Hough Line Image output
* `debug` prints out helpful information for debugging

The `convert_all` function has the following parameters:
* `src` is the filepath of the text files; by default set to `'../output/txt/'`; __Note:__ this parameter and the `dst` parameter of `detect_tables` should be set to the same values
* `dst` is where the converted CSV files will be placed; by default set to `'../output/csv/'`
* `name` is the name of the csv output; by default set to table
* `debug` prints out helpful information for debugging
