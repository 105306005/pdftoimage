# for pdf formate 1 - tag on the right of image + 3 images on one page
# Reference 1 - How to Extract Images from PDF in Python : https://www.thepythoncode.com/article/extract-pdf-images-in-python 
# Reference 2 - pic_getinfo: https://github.com/pymupdf/PyMuPDF/issues/1017
# Reference 3 - textbox-extraction: https://github.com/pymupdf/PyMuPDF-Utilities/tree/master/textbox-extraction

import fitz # PyMuPDF - pip3 install PyMuPDF Pillow
import io
import os
from PIL import Image

# put your local path here
path = "/Users/maggiesun/Documents/Testing/pdftoimage2/" 
# put pdf file name
pdf_file_name = 'test1.PDF' 
# put words that can help us locate the correct page for image (ex. Title of that page)
page_determinators = ["ADDITIONAL PHOTOGRAPH ADDENDUM", "Subject Photo Page"] 

# -------------------------------------------------------------------------------

def pic_getinfo(doc,page, item): 
    """for getting image information"""  
    xref, _, width, height, _, _, _, name , _ = item
    rect = page.get_image_bbox(name)
    img = Image.open(io.BytesIO(doc.extractImage(xref)['image']))
    return {"height":height,"width":width,"xref":xref, "name":name, "rect":rect,"img":img }

def make_text(words):
    """Return textstring output of get_text("words").
    Word items are sorted for reading sequence left to right,
    top to bottom.
    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda w: w[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 1)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return "\n".join([" ".join(line[1]) for line in lines])

# open the file
pdf_file = fitz.open(path+pdf_file_name)

# iterate over PDF pages
for page_index in range(len(pdf_file)):
    # get the page itself
    page = pdf_file[page_index]
    image_list = page.getImageList(full=True)
    
    # printing number of images found in this page - but may contain signiture or other things
    if image_list:
         print(f"[+] Found a total of {len(image_list)} images in page {page_index+1}")
    # else:
    #     print("[!] No images found on page", page_index)
    text = page.get_text("text")
    

    if any(deter in text for deter in page_determinators):
        # print(text)

        for image_index, img in enumerate(page.getImageList(), start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = pdf_file.extract_image(xref)
            # get image information
            img_info = pic_getinfo(pdf_file,page, img)
            # get image Rectangle
            img_rect = img_info["rect"] #x0, y0, x1, y1 
            #set word Rectangle that we want to detect -> noe, Make decisions by guessing
            word_rect = (img_rect[0], img_rect[1], img_rect[2]+1000, img_rect[3]+100)
            # Desired output - the word detect in word Rectangle
            print(page.get_textbox(word_rect))
            # get image
            image_bytes = base_image["image"]
            # get the image extension - file type
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # save it to local disk
            print(f"image{page_index+1}_{image_index}.{image_ext}")
            imgname = f"image{page_index+1}_{image_index}.{image_ext}"
            image.save(open(os.path.join(path, imgname), "wb"))


