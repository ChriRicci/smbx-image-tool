#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os
import time
import sys
import argparse
import collections

def compileImg(folderList, newImgFolder, newImgName, ext, resizeNum):
    #Check if the folders exist.
    if (not os.path.isdir(newImgFolder)):
        print(newImgFolder + ' folder not found. Please make sure it actually exists!')
        quitProgram()
    for folder in folderList:
        if (not os.path.isdir(folder)):
            print('ERROR: ' + folder + ' folder not found. Please make sure it actually exists!')
            if len(folderList) == 1:
                print('ERROR: No folder found. Quitting the compiling process.')
                quitProgram()
            folderList.remove(folder)

    imagesHeight = 0
    imagesWidth = 0
    imageSpace = 2 #Space between the images.
    images = []
    imageData = open(newImgFolder + "/" + newImgName + ".txt", 'w')

    #Find the image with the maximum height (to be used later when creating an image with all the images)
    #Also record every image found in a text file.
    for folder in folderList:
        #Check if there are any images in the folder first. If it comes out empty, skip this step.
        if (len(os.listdir(folder)) == 0):
            print('ERROR: ' + folder + ' is empty. Put some images there first!')
            if len(folderList) == 1:
                print('ERROR: No images found in any folder. Quitting the compiling process.')
                quitProgram()
            continue
        
        print("Joining images in " + folder)
        if resizeNum != 0: print('The images will be resized.')
        print("Images found:")
        for file in os.listdir(folder):
            if (file.endswith(ext)):
                im = Image.open(folder + "/" + file)
                w, h = im.size
                
                #Resize the image (resizeNum = 1 by default, so it only applies with -r50 and -r200
                im = im.resize((int(w * resizeNum), int(h * resizeNum)))
                w = int(w*resizeNum)
                h = int(h*resizeNum)
                
                print(file + ', ' + 'Width = ' + str(w) + ', Height = ' + str(h))
                imageData.write(file + "|" + str(w) + "|" + str(h) + "\n")
                
                #Update the height for combined image
                if h > imagesHeight:
                    imagesHeight = h
                    
                #Update the width for combined image
                imagesWidth = imagesWidth + w + imageSpace
                
                #Add the image to a list of images (for quick reference)
                images.append(im)

    #Yep, i don't even feel like adding support for gifs...
    #Palettes stuff
    if ext == 'png':
        #Get the palettes from each image. The trasparency color is excluded.
        print('Generating palettes')
        palettes = set()
        for im in images:
            pal = set()
            for _, color in im.convert('RGBA').getcolors():
                if color != (0, 0, 0, 0): pal.add(color)
            palettes.add(frozenset(pal))
        
        #Create a new image with the palettes. Will be pasted into the other image.
        palW = 0
        for palette in palettes: 
            if len(palette) > palW: palW = len(palette)
        palH = len(palettes)
        palImg = Image.new('RGBA', (palW, palH)).convert('RGBA')
        palIndX = 0
        palIndY = 0
        for palette in palettes:
            for color in palette:
                palImg.putpixel((palIndX, palIndY), color)
                palIndX += 1
            palIndX = 0
            palIndY += 1
        
        #Calculate the actual width and height.
        actualWidth = 0
        if imagesWidth > palW: actualWidth = imagesWidth 
        else: actualWidth = palW
        actualHeight = imagesHeight + palH
        #Also, record the combined images' width and height and palettes' width and height.
        imageData.write(str(imagesWidth) + '|' + str(imagesHeight))
    imageData.close()
    
    print("Size for the compiled image is: width = " + str(imagesWidth) + ", height = " + str(imagesHeight))
    #Create the new image which will contain all the images.
    print('Creating new image')
    if (ext == "gif"): newImg = Image.new('RGB', (imagesWidth, imagesHeight), (255, 120, 255))
    if (ext == "png"): newImg = Image.new('RGBA', (actualWidth, actualHeight), (255, 120, 255, 255)).convert("RGBA")
    
    #The actual image joining part.
    widthIndex = 0
    
    print('Pasting images')
    for im in images:
        w, h = im.size
        diff = int((imagesHeight - h) / 2)
        if (ext == "png"):
            #When using png images, we gotta draw a bunch of trasparent rectangles first.
            draw = ImageDraw.Draw(newImg)
            im_alpha = Image.open(folder + "/" + file)
            im_alpha.putalpha(255)
            draw.rectangle([(widthIndex, diff), (widthIndex + w-1, diff + h-1)], (255, 120, 255, 0))                   
            newImg.paste(im, (widthIndex, diff))
        elif (ext == "gif"): 
            newImg.paste(im, (widthIndex, diff))
        widthIndex = widthIndex + w + imageSpace

    if ext == 'png':
        #Paste the palettes' image into the combined image.
        print('Pasting palettes')
        newImg.paste(palImg, (0, imagesHeight))

    #Save the new image.
    print("Saving " + ext.upper() + " image with name: " + newImgName + " and with destination: " + newImgFolder)
    newImg.save(newImgFolder + "/" + newImgName + "." + ext, ext.upper())

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
parser.add_argument('-e', '--extension', choices=['png', 'gif'], help='The extension to use.')
parser.add_argument('-ef', '--edit-folder', nargs='+', default=['./edit'], metavar='PATH', help='Choose the folder of the images to join. Default is ./edit. This option is ignored if separing images. This option accepts more than one folder.')
parser.add_argument('-jf', '--joined-folder', default=os.getcwd(), metavar='PATH', help='Choose the folder where to save the big image cointaining the joined images. Default folder is the program\'s directory.')
parser.add_argument('-of', '--output-folder', default='./output', metavar='PATH', help='Choose the folder where the separated images appear. Default is ./output. This option is ignored if compiling images.')
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

while (args.extension != 'png' and args.extension != 'gif' and args.extension != 'p' and args.extension != 'g'):
    if (args.extension is None): print('Write \'png\' or \'p\' to use png images, \'gif\' or \'g\' to use gif images: ', end='')
    else: print('Errors in the extension. Please try again: ', end='')
    args.extension = input()
    if (args.extension == 'p'): args.extension = 'png'
    elif (args.extension == 'g'): args.extension = 'gif'

resize_num = 1
if args.resize_to_200 and args.resize_to_50:
    print('Both resize arguments are present. They will be ignored.')
    args.resize_to_200 = false
    args.resize_to_50 = false
elif args.resize_to_200: resize_num = 2
elif args.resize_to_50: resize_num = 0.5
    
if (args.compile):
    compileImg(args.edit_folder, args.joined_folder, args.name, args.extension, resize_num)
if (args.separe):
    separeImg(args.joined_folder, args.output_folder, args.name, args.extension, resize_num)
print('\nDone!')

quitProgram()
