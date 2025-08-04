#This file converts txt file to .png! This file should ONLY be used for text conversion. NOT IMAGES!
from PIL import Image,ImageDraw,ImageFont
import Ascii_renderer as Ascii_renderer
import sys
import os
fileContents = []   
TempfilePath = ""
text = ""

def createimg():
    
    try:
        with open(f"{TempfilePath}","r") as content:
            fileContents = content.readlines()

    except Exception as e:
            print("Error: file not found: ",e)
            sys.exit(1)

        #Check the file contents.
    if(len(fileContents) < 1):
        print("Error: Text cannot be blank")
        sys.exit(1)
    else: 
        content = ''
        for lines in fileContents:
        #append elements to String text.
            content += lines.rstrip('\n') + "\n" 

        text = content
    #Now converting String -> img
    '''
    We need to decide font, char size in pixels (2,2)
    Create instance of Image.new with mode: L , (2,2)
    now we draw the img using ImageDraw.Draw(Image.new(L,(2,2)))
    THEN, we get corrdinates using textbbox, setting output on 0,0
    '''
    font = ImageFont.truetype("cour.ttf", 24)
    #each pixel size
    size = (5,5)
    dummy_img = Image.new("L",size)
    draw = ImageDraw.Draw(dummy_img)
    #this textbbox is used to render bounds. (0,0) means starting text pos, 'text' has string to be placed and font obj
    #Hence, textbbox returns a tuple -> (left,top,right,bottom)
    bbox = draw.textbbox((0,0),text,font=font)

#Calculate height from received tuple (left,top,right,bottom)
#h = bottom - top
#w = right - left
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    PADDING = 0

    if(len(text) > 0 and len(text) <= 3):
        PADDING = 25
    elif(len(text) > 3 and len(text) <= 7):
        PADDING = 15
        Ascii_renderer.PROJECTION_DISTANCE += 12
    elif(len(text) > 7 and len(text) <= 11):
        PADDING = 7
        Ascii_renderer.PROJECTION_DISTANCE += 14

    Height = text_height + (2 * PADDING)
    Width = text_width + (2 * PADDING)

    img = Image.new("L",(Width,Height),color=255)

    new_draw = ImageDraw.Draw(img)

# Compute centered offset
    x_offset = (Width - text_width) // 2
    y_offset = (Height - text_height) // 2

# Draw centered
    new_draw.text((x_offset, y_offset), text, font=font, fill=0)
#Atlast, save em
    img.save("Ascii_image.png")