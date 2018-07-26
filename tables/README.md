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

The the `detect_tables` function has the following signature: `detect_tables(src, dst='../output/txt/', image='../output/img/', kernel_size=5, rho=1, theta=np.pi / 2, threshold=50, min_line_length=500, maxLineGap=1, file='temp', debug=False)`:
* `src` is the filepath of the PDF
* `dst` is an optional parameter that denotes where the extracted text files will be placed; by default set to `'../output/txt/', image='`
* `image` is an optional parameter denoting the directory where HoughLine images will be  stored; by default set to `'../output/img/'`
* `kernel_size`, `rho`, `theta`, `threshold`, `min_line_length`, `maxLineGap` are optional parameters that are used in the Hough Line detection algorithm. By default, they are set to the values we found most generalizable.
* `file` is an optional parameter denoting the name of the Hough Line Image output
* `debug` prints out helpful information for debugging

