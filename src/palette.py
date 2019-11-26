from PIL import Image, ImageDraw
import collections

#this function gets the palette of an images. it should sort the colors too TODO
def get_palette(img):
    pal = []
    for colorTuple in img.getcolors():
        if colorTuple[1][3] != 0: #check trasparency value
            pal.append(colorTuple[1])
    return pal

#this function takes a palette set and creates a new image from it. returns the image itself, plus its width and height.
def get_pal_image(palette_set):
    #get the width and height for the image
    w = 0
    for palette in palette_set: 
        if len(palette) > w: w = len(palette)
    h = len(palette_set)
    #create blank image
    img = Image.new('RGBA', (w, h)).convert('RGBA')
    #draw the palette into the image
    x, y = 0, 0
    for palette in palette_set:
        for color in palette:
            img.putpixel((x, y), color)
            x += 1
        x = 0
        y += 1
    return img

def paste_palette(img, img_pal):
    imw, imh = img.size
    palw, palh = img_pal.size
    if palw > imw:
        imw = palw
    img_with_pal = Image.new('RGBA', (imw, imh + palh), (0, 0, 0, 0)).convert("RGBA")
    img_with_pal.paste(img, (0, 0))
    img_with_pal.paste(img_pal, (0, imh))

    return img_with_pal

def replace_color(data, oldc, newc):
    newdata = []
    for item in data:
        if item == oldc:
            newdata.append(newc)
        else:
            newdata.append(item)
    return newdata

def check_subset(p, plist):
    for pal in plist:
        if set(p).issubset(set(pal)):
            return True
    return False
