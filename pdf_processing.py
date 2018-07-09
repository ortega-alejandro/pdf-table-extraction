import os
import subprocess
from wand.image import Image

def convert_pdf(src, dst='images/'):
	'''
	Parameters: 
	src is a String denoting the location of the file, 
	dst is the destination of the jpeg output, by default saves to the current working directory in a folder called images
	
	Function that converts PDF pages to jpeg images suitable for OCR using Wand, or directly through Ghostscript if Wand 
	Throws a corrupt image error.
	
	'''
    try:
        with Image(filename=path, resolution=200) as img:
            img.save(filename=dst + 'image.jpg')
    except:
        subprocess.call(["convert", "-density","200",path,"-quality","100","-sharpen","0x1.0",dst + "image.jpg"])
