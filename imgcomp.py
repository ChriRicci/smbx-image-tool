#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os
import time
import sys
import argparse
import collections
#import new.py

def checkDir(d):
    if (not os.path.isdir(d)):
        print('ERROR: ' + d + ' was not found. Please make sure it exists first.')
        return 0
    return 1

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

#this function gets the configuration of a joined image. it takes a filename and checks if it exists. it then returns the file's contents.
def getConf(filename):
    confFilename = os.path.splitext(filename)[0]
    print(confFilename) 
    if os.path.isfile(confFilename + "txt"):
        f = open(path + ".txt", 'r')
        content = f.read()
        return content
    return False

def getJoinedImages(dirList):
    imgList = []
    confList = []
    for d in dirList:
        print("Searching for images in " + d + "...")
        for f in sorted(os.listdir(d)):
            if f.endswith("png"):
                img = Image.open(d + "/" + f)
                conf = getConf(img.filename)
                if (not conf):
                    print("Configuration not found for " + f + ". Skipping.")
                    continue
                print("Found image: " + f)
                imgList.append(img)
                imgConf.append(conf)
    return (imgList, confList)

def separeImages(inputDirs, outputDir, imgName, resizeNum):
    #for d in imgDirs:
    #    Image.open(imgDir + '/' + imgName + '.png')
    imageList, confList = getJoinedImages(inputDirs)
    if len(imageList) == 0:
        print("ERROR: No image found in any directory. Quitting the joining process.")
        quitProgram()
    
def altro():
    print('Splitting image: ' + imgName + '.png; from: ' + imgDir + ' using configuration: ' + imgName + '.txt')
    
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

def main():
    parser = argparse.ArgumentParser(description='This is a tool which can help in various tasks related to images. It can join images for easy recoloring, separing them, quickly resize all of them and much more.')
    parser.add_argument('-v', '--version', action='version', version='SMBX Image Tool version 1.3')
    
    parser.add_argument('-j', '--join', choices=['images', 'spritesheet'], help='Joins the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the directory ./edit, located in the program\'s directory. You can choose between joining images normally (by writing \'images\' after --join) or joining in a spritesheet (by writing \'spritesheet\'). If joining in a spritesheet, you\'ll need to specify --width and --height too.\n')
    parser.add_argument('-s', '--separe', action='store_true', help='Separates the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the image found in the program\'s directory (if it finds it).')
    parser.add_argument('--resize-only', action='store_true', help='When specified, the tool will only resize the images without joining or separing.')
    parser.add_argument('--extract-palette-only', action='store_true', help='When specified, the tool will extract the palette from the images.')

    parser.add_argument('-spw', '--spritesheet-width', type=int, metavar='', help='The width of the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-sph', '--spritesheet-height', type=int, metavar='', help='The height of the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-imw', '--width', type=int, metavar='', help='The width of the images in the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-imh', '--height', type=int, metavar='', help='The width of the images in the spritesheet, will be ignored if joining images normally.')
    
    parser.add_argument('-idir', '--input-dir', nargs='+', default=['./edit'], metavar='DIR', help= 'The input directory, more directories can be specified. The default is ./edit when joining and the same dir as the program (\'.\') when separating.')
    parser.add_argument('-odir', '--output-dir', default='.', metavar='DIR', help='The output directory. Unlike --input-dir, you can only specify one. The default is the same dir as the program (\'.\') when joining and is ./output when separating.')
    parser.add_argument('-in', '--input-name', metavar='', help='If given, when joining or separing the tool will search for filenames matching this name.')
    parser.add_argument('-on', '--output-name', default='image', metavar='', help='If given, the tool will rename any output images by this name, followed by numbers if there is more than one image. The default is \'image\'') 

    parser.add_argument('-res', '--resize', type=int, metavar='', help='Specifies to resize the output image(s) by a certain number. pass 200 to resize them by double, 50 to resize them by half.')
    parser.add_argument('-seppal', '--separate-palette', action='store_true', help='When specified, the tool will the save the palette as a separate image.')
    args = parser.parse_args()

    #if args.join + args.separe == 0: 
    #    print("ERROR: No argument --join or --separe given.")
    #    quitProgram()
    #if args.join + args.separe == 2:
    #    print("ERROR: Both argument --join and --separe given.")
    #    quitProgram()

    #Check if the folders exist.
    if not checkDir(args.output_dir):
        quitProgram()

    dirsToRemove = []
    for d in args.input_dir:
        if not checkDir(d):
            dirsToRemove.append(d)
    for d in dirsToRemove:
        input_dir.remove(d)

    if len(args.input_dir) == 0:
        print("ERROR: No real directory found. Quitting the joining process.")
        quitProgram()
    if len(dirsToRemove) > 0:
        print("Any directory not found will be skipped.\n")

    if (args.join): joinImages(args.input_dir, args.output_dir, args.name, args.resize, 2, 0)
    elif (args.separe): separeImages(args.input_dir, args.output_dir, args.name, args.resize)
    print('\nDone!')

    quitProgram()

main()
