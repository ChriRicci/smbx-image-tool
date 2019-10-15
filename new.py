#this function takes a directory and check if it exists. if it does, it returns 1, otherwise, it prints a message and returns 0.
def checkDir(d):
    if (not os.path.isdir(d)):
        print('ERROR: ' + d + ' was not found. Please make sure it exists first.')
        return 0
    return 1

#this function takes a list of directories and searches for images with extension "png". if any images are found, it will add them to a list. the function then returns this list.
def getImages(dirList):
    imgList = []
    for d in dirList:
        print("Searching for images in " + d + "...")
        for f in sorted(os.listdir(d)):
            if f.endswith("png"):
                img = Image.open(d + "/" + f)
                w, h = img.size
                print("Found image: " + f + " | Width: " + str(w) + " | Height: " + str(h))
                imgList.append(img)
    return imgList

#this function takes a list of images and a file. it will loop through all the images and write their name and size to the file.
def saveImagesData(filename, imgList, maxw, maxh):
    imageData = open(filename, 'w')
    for img in imgList:
        w, h = img.size
        imageData.write(os.path.basename(img.filename) + "|" + str(w) + "|" + str(h) + "\n")   
    imageData.write(str(maxw) + '|' + str(maxh))
    imageData.close()

#this function takes a list of image and a number which can be 2 or 0.5. it will then resize the images to that number.
def resizeImages(imgList, resn):
    for img in imgList:
        #Resize the image (resizeNum = 1 by default, so it only applies with -r50 and -r200
        w, h = img.size
        img = img.resize((int(w * resizeNum), int(h * resizeNum)))
    return imgList

#this function takes a list of images and returns the max height between the images.
def getMaxHeight(imgList):
    maxHeight = 0
    for img in imgList:
        w, h = img.size
        if h > maxHeight:
            maxHeight = w
    return maxHeight

#this function takes a list of images and a space value that is space between the images. it returns the combined width of all images + space between them.
def getMaxWidth(imgList, space):
    maxWidth = 0
    for img in imgList:
        w, h = img.size
        maxWidth += w + space
    return maxWidth

#this function takes, you guessed it, a list of images and returns a set of the palette of each image, without sorting them.
def getPalette(imgList):
    paletteSet = set()
    for img in imgList:
        pal = set()
        for _, color in img.convert('RGBA').getcolors():
            if color != (0, 0, 0, 0):
                pal.add(color)
        paletteSet.add(frozenset(pal))
    return paletteSet

#this function takes a palette set and creates a new image from it. returns the image itself, plus its width and height.
def createPaletteImage(paletteSet):
    #get the width and height for the image
    w = 0
    for palette in paletteSet: 
        if len(palette) > w: w = len(palette)
    h = len(paletteSet)
    #create blank image
    img = Image.new('RGBA', (w, h)).convert('RGBA')
    #draw the palette into the image
    x = 0
    y = 0
    for palette in paletteSet:
        for color in palette:
            img.putpixel((x, y), color)
            x += 1
        x = 0
        y += 1
    return (img, w, h)

#this function pastes a list of images into an image, using the old method and with optional space. it assumes the image is big enough and every image in the list is a png.
#old method means that every image is pasted horizontally.
def joinImagesOld(newimg, imgList, space):
    maxw, maxh = newimg.size
    x = 0
    for img in imgList:
        w, h = img.size
        diff = int((maxh - h) / 2)
        
        #First we draw a trasparent rectangle, then we paste the image on the rectangle
        draw = ImageDraw.Draw(newimg)
        imgalpha = img
        imgalpha.putalpha(255)
        draw.rectangle([(x, diff), (x + w-1, diff + h-1)], (255, 120, 255, 0))          
         
        newimg.paste(img, (x, diff))
        x = x + w + space
    return newimg
