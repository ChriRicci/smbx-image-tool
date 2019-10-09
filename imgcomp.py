#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os
import time
import sys
import argparse
import collections

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

#this function takes a palette set and creates a new image from it. returns the image itself.
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
    #Check if the folders exist.
    if not checkDir(imgDir):
        quitProgram()

    dirsToRemove = []
    for d in dirList:
        if not checkDir(d):
            dirsToRemove.append(d)
    for d in dirsToRemove:
        dirList.remove(d)
    
    if len(dirList) == 0:
        print("No real directory found. Quitting the joining process.")
        quitProgram()
    if len(dirsToRemove) > 0:
        print("Any directory not found will be skipped.\n")
    
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

def separeImg(joinedImgFolder, outputFolder, joinedImgName, ext, resizeNum):
    #Check if the folders exist.
    if (not os.path.isdir(joinedImgFolder)):
        print(joinedImgFolder + ' folder not found. Please make sure it actually exists!')
        quitProgram()
    if (not os.path.isdir(outputFolder)):
        print(outputFolder + ' folder not found. Please make sure it actually exists!')
        quitProgram()
    #Check if the files exist.
    if (not os.path.isfile(joinedImgFolder + '/' + joinedImgName + '.' + ext)):
        print('The image ' + joinedImgName + '.' + ext + ' was not found. Please check if ' + joinedImgFolder + ' is empty.')
        quitProgram()
    if (not os.path.isfile(joinedImgFolder + '/' + joinedImgName + '.txt')):
        print('The configuration file ' + joinedImgName + '.txt was not found. Please check if ' + joinedImgFolder + ' is empty.')
        quitProgram()
    
    print('Splitting image: ' + joinedImgName + '.' + ext)
    print('From: ' + joinedImgFolder)
    print('Using configuration: ' + joinedImgName + '.txt')
    
    widthIndex = 0
    imageSpace = 2
    
    im = Image.open(joinedImgFolder + '/' + joinedImgName + '.' + ext)
    imagesWidth, imagesHeight = 0, 0
    with open(joinedImgFolder + '/' + joinedImgName + '.txt', 'r') as ins:
        for line in ins:
            line = line.rstrip("\n")
            d = line.split("|")
            if len(d) == 2:
                imagesWidth = int(d[0])
                imagesHeight = int(d[1])
    #Separe the images.
    with open(joinedImgFolder + '/' + joinedImgName + '.txt', 'r') as ins:
        for line in ins:
            line = line.rstrip("\n")
            d = line.split("|")
            if len(d) == 2: 
                print(line + ': not a line that describes an image')
                continue
            fileName = d[0]
            w = int(d[1])
            h = int(d[2])
            diff = (imagesHeight - h) / 2
            print('Cropping image ' + fileName + ' with width ' + str(w) + ' and height = ' + str(h))
            piece = im.crop((widthIndex, diff, widthIndex + w, diff + h))
            piece = piece.resize((int(w * resizeNum), int(h * resizeNum)))
            piece.save(outputFolder + '/' + fileName)
            widthIndex = widthIndex + w + imageSpace
    ins.close()

def quitProgram():
    input('\nPress any key to exit...')
    sys.exit()

parser = argparse.ArgumentParser(description='This program compiles images in a specified folder into one image for easy recoloring.')
parser.add_argument('-c', '--compile', action='store_true', help='Compiles the images in the folder specified by --edit-folder. When --edit-folder is not specified, it will use a folder called "edit", located in the program\'s directory.')
parser.add_argument('-s', '--separe', action='store_true', help='Separates the images in the folder specified by --joined-folder. When --joined-folder is not specified, it will use the image found in the program\'s directory (if it finds it).')
parser.add_argument('-idir', '--input-dir', nargs='+', default=['./edit'], metavar='PATH', help= 'The input directory, more directories can be specified. The default is ./edit when joining and the same dir as the program (\'.\') when separating.')
parser.add_argument('-odir', '--output-dir', default='.', metavar='PATH', help='The output directory. Unlike --input-dir, you can only specify one. The default is the same dir as the program (\'.\') when joining and is ./output when separating.')
parser.add_argument('-n', '--name', default='joinedImages', help='The name to give to the big, compiled image. Default is \'joinedImages\'.')
parser.add_argument('-r200', '--resize-to-200', action='store_true', help='If present, the images will be resized to 200%% (nearest neighbor) before being joined.')
parser.add_argument('-r50', '--resize-to-50', action='store_true', help='If present, the images will be resized to 50%% (nearest neighbor) before being joined.')
parser.add_argument('-v', '--version', action='version', version='SMBX Image Compiler: version is 1.2')
args = parser.parse_args()

#By default, the program should ask whether it should compile and separe images and what extension to use.
while ((not args.compile and not args.separe) or (args.compile and args.separe)):
    print('Press \'c\' for compile, \'s\' for separe: ', end='')
    choice = input()
    if (choice == 'c'):
        args.compile = True
        args.separe = False
    elif (choice == 's'):
        args.separe = True
        args.compile = False
    else:
        print('Please choose only either \'c\' or \'s\'.\n')

res_num = 1
if args.resize_to_200 and args.resize_to_50:
    print('Both resize arguments are present. They will be ignored.')
    args.resize_to_200 = false
    args.resize_to_50 = false
elif args.resize_to_200: res_num = 2
elif args.resize_to_50: res_num = 0.5
    
if (args.compile):
    joinImages(args.edit_folder, args.joined_folder, args.name, res_num, 2, 0)
if (args.separe):
    separeImg(args.joined_folder, args.output_folder, args.name, "png", res_num)
print('\nDone!')

quitProgram()
