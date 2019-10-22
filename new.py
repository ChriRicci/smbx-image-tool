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


def joinImages(dirList, imgDir, imgName, resNum, imageSpace, sepPal):
    imageList = getImages(dirList)
    if len(imageList) == 0:
        print("ERROR: No image found in any directory. Quitting the joining process.")
        quitProgram()

    #resize images if requested
    if resNum != 1:
        print('The images will be resized.')
        imageList = resizeImages(imageList, resNum)
    #get palette
    print("\nGenerating palette...")
    palettes = getPalette(imageList)
    paletteImage, palw, palh  = createPaletteImage(palettes)

    #get width and height for the new image
    print("Searching for width and height of the new image...")
    maxHeight = getMaxHeight(imageList)
    maxWidth = getMaxWidth(imageList, imageSpace)
    if sepPal:
        print("Requested to separate palette. Saving palette image...")
        newImg.save(newImgDir + "/" + newImgName + "Palette.png")
    else:
        #update maxwidth and maxheight so we can paste the palette image into the joined image
        if maxWidth < palw: maxWidth = palw
        maxHeight = maxHeight + palh 

    print("Saving image data...")
    saveImagesData(imgDir + "/" + imgName + ".txt", imageList, maxWidth, maxHeight)

    print("Creating new image: width = " + str(maxWidth) + "; height = " + str(maxHeight))
    newImage = Image.new('RGBA', (maxWidth, maxHeight), (255, 120, 255, 255)).convert("RGBA")
    newImage = joinImagesOld(newImage, imageList, imageSpace)
    if not sepPal:
        print("Pasting palette") 
        newImage.paste(paletteImage, (0, maxHeight))

    print("Saving image: name = " + imgName + "; destination = " + imgDir)
    newImage.save(imgDir + "/" + imgName + ".png")


#this function separes images that have config (.txt) with them. because the names of the images are contained in the config file, there's no need to specify any output name. if --extract-palette is specified, it will get the palette pasted in the image (if it's there) and save it as a new image in output dir, or generate a new one if needed.
def separeImages(inputDirs, outputDir, inputName, res_num, get_pal):
    imageList = getJoinedImages(inputDirs)
    if len(imageList) == 0:
        print("ERROR: No image found in any directory. Quitting the joining process.")
        quitProgram()
    for img in imageList:
        print('Splitting image: ' + os.path.basename(img.filename))
        with open(os.path.splitext(img.filename)[0] + '.txt') as config:
            #the config's last line contains the real height and width (without the palette) and the space between images.
            lines = config.read().splitlines()
            realw, realh, space = lines[-1].rstrip('\n').split('|')
            lines.remove(lines[-1])

            #separating the images
            x = 0
            for line in lines:
                line = line.rstrip('\n')
                filename, w, h = line.split('|')
                print('Cropping image ' + fileName + ', width = ' + str(w) + ', height = ' + str(h))
                diff = (imagesHeight - h) / 2
                newimg = img.crop((x, diff, x + w, diff + h))
                newimg = newimg.resize((int(w * res_num), int(h * res_num)))
                newimg.save(outputDir + '/' + filename)
                x += w + space
           
            #palette related stuff
            imgw, imgh = img.size
            if get_pal and imgh != realh:
                print("Saving palette of " + os.path.basename(img.filename))
                paletteimg = img.crop((0, realh, imgw, imgh))
                paletteimg.save(outputDir + '/' + os.path.basename(os.path.splitext(img.filename)[0]) + '.png')
            else:
                print("the palette isn't pasted on the image, so whatever. TODO TODO DOTO TODO")
