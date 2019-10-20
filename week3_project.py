#!/usr/bin/env python
# coding: utf-8

# # The Project #
# 1. This is a project with minimal scaffolding. Expect to use the the discussion forums to gain insights! It’s not cheating to ask others for opinions or perspectives!
# 2. Be inquisitive, try out new things.
# 3. Use the previous modules for insights into how to complete the functions! You'll have to combine Pillow, OpenCV, and Pytesseract
# 4. There are 4 functions you need to complete to have a working project. These functions are described using the RE formula, which stands for Requires and Effects. Each function will have its own RE located directly above the function definition. The Requires section describes what is needed in the function argument (inbetween the function definition parenthesis). The Effects portion outlines what the function is supposed to do. 
# 5. There are hints provided in Coursera, feel free to explore the hints if needed. Each hint provide progressively more details on how to solve the issue. This project is intended to be comprehensive and difficult if you do it without the hints.
# 
# ### The Assignment ###
# Take a [ZIP file](https://en.wikipedia.org/wiki/Zip_(file_format)) of images and process them, using a [library built into python](https://docs.python.org/3/library/zipfile.html) that you need to learn how to use. A ZIP file takes several different files and compresses them, thus saving space, into one single file. The files in the ZIP file we provide are newspaper images (like you saw in week 3). Your task is to write python code which allows one to search through the images looking for the occurrences of keywords and faces. E.g. if you search for "pizza" it will return a contact sheet of all of the faces which were located on the newspaper page which mentions "pizza". This will test your ability to learn a new ([library](https://docs.python.org/3/library/zipfile.html)), your ability to use OpenCV to detect faces, your ability to use tesseract to do optical character recognition, and your ability to use PIL to composite images together into contact sheets.
# 
# Each page of the newspapers is saved as a single PNG image in a file called [images.zip](./readonly/images.zip). These newspapers are in english, and contain a variety of stories, advertisements and images. Note: This file is fairly large (~200 MB) and may take some time to work with, I would encourage you to use [small_img.zip](./readonly/small_img.zip) for testing.
# 
# Here's an example of the output expected. Using the [small_img.zip](./readonly/small_img.zip) file, if I search for the string "Christopher" I should see the following image:
# ![Christopher Search](./readonly/small_project.png)
# If I were to use the [images.zip](./readonly/images.zip) file and search for "Mark" I should see the following image (note that there are times when there are no faces on a page, but a word is found!):
# ![Mark Search](./readonly/large_project.png)
# 
# Note: That big file can take some time to process - for me it took nearly ten minutes! Use the small one for testing.

# In[3]:


from zipfile import ZipFile

from PIL import Image, ImageDraw
import pytesseract
import cv2 as cv
import numpy as np

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

# the rest is up to you!


# In[6]:


cd readonly


# In[7]:


get_ipython().system('ls')


# In[8]:


# extract files using context manager
zipfile = 'small_img.zip'
small_file_list = 0
with ZipFile(zipfile, 'r') as zp:
    print('Extracting files...')
    zp.printdir()
    zp.extractall()
    small_file_list = zp.namelist()
    print('Completed!')


# In[9]:


# draw rectangles around faces
def draw_face_rect(faces_matrix, draw_on, return_box = False):
    """
    Displays rectangles around faces or returns boxes around faces.
    Returns list of tuples which contain coordinates of rectangles.
    List of tuples is in format (x1,y1,x2,y2).
    """
    pil_img = Image.open(draw_on).convert('RGB')
    # create drawing context
    drawing = ImageDraw.Draw(pil_img)
    # store location of rectangles in a list
    boxes = []
    # iterate through each face
    for x, y, w, h in faces_matrix:
        drawing.rectangle((x, y, x+w, y+h), outline='red')
        boxes.append((x, y, x+w, y+h))
    if return_box:
            return boxes
    return pil_img

def faces_resize(faces, draw_on):
    """
    returns size (int) and a list if resized cropped face images
    """
    # return the detected faces' boxes
    face_box = draw_face_rect(faces, draw_on, return_box=True)
    # open image
    pil_img = Image.open(draw_on).convert('RGB')
    # the goal is to calculate the average size in order to fit pictures on contact sheet evenly
    size_list = []
    for tup in face_box:
        fb = pil_img.crop(tup)
        size_list.append(fb.size)

    # find average size of image
    size_xy = int(np.mean(np.array(size_list)))

    # iterate through boxes, crop, and resize image
    faces_list = []
    for tup in face_box:
        fb = pil_img.crop(tup)
        faces_list.append(fb.resize((size_xy, size_xy)))
        
    return size_xy, faces_list

# size_xy = faces_resize(faces, draw_on=img_file)[0]
         
def create_contact_sheet(size, faces_list, img_file):
    orig_img = Image.open(img_file)
    # create contact sheet and size it according to the average image size found earlier
    contact_sheet = Image.new(orig_img.mode, (size*5, size*2))
    x = 0
    y = 0
    for img in faces_list:
        contact_sheet.paste(img, (x, y))
        if x + img.width > contact_sheet.width:
            x = 0
            y = y + img.height
        else:
            x = x + img.width
    return contact_sheet


# In[10]:


# extract text from image
def search_keyword(keyword, img_file, scaleFactor):
    # open original image and convert to grayscale
    grayscale = Image.open(img_file).convert('L')
    image_text = pytesseract.image_to_string(grayscale)
    if keyword in image_text:
        # if found keyword then detect faces
        img = cv.imread(img_file)
        gray_img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        
        # define classifier and params
        params = {'image': gray_img,
                  'scaleFactor': scaleFactor,
                  'minNeighbors': 3,
                  'minSize': (120,120),
                  'maxSize': (315,315)
                 }
        faces = face_cascade.detectMultiScale(**params)
        num_faces = len(faces)
        
        # if faces have been detected
            # crop faces, create contact sheet and paste faces sized accordingly
        if num_faces > 0:
            size_xy, faces_list = faces_resize(faces, draw_on=img_file)
            print('Results found in file', img_file)
            display(create_contact_sheet(size_xy, faces_list, img_file))
            
        if num_faces < 1:
            print('\nResults found in file', img_file)
            print('But there were no faces in that file!')


# In[11]:


# search images.zip for keyword 'Mark'
# extract files using context manager
zipfile = 'images.zip'
large_file_list = 0
with ZipFile(zipfile, 'r') as zp:
    print('Extracting files...')
    zp.printdir()
    zp.extractall()
    large_file_list = zp.namelist()
    print('Completed!')


# In[ ]:


for png in small_file_list:
    search_keyword('Christopher', png, scaleFactor=1.5)


# In[ ]:


for png in large_file_list:
    search_keyword('Mark', png, scaleFactor=1.5)

