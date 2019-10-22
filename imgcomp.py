#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os
import time
import sys
import argparse
import collections
import re
#import new.py

#this function simply returns all the arguments. i made this to separe the argument stuff from the main.
def getArgs():
    #help and version arguments
    parser = argparse.ArgumentParser(description='This is a tool which can help in various tasks related to images. It can join images for easy recoloring, separing them, quickly resize all of them and much more.')
    parser.add_argument('-v', '--version', action='version', version='SMBX Image Tool version 1.3')
    #action arguments
    parser.add_argument('-j', '--join', choices=['images', 'spritesheet'], help='Joins the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the directory ./edit, located in the program\'s directory. You can choose between joining images normally (by writing \'images\' after --join) or joining in a spritesheet (by writing \'spritesheet\'). If joining in a spritesheet, you\'ll need to specify --width and --height too.\n')
    parser.add_argument('-s', '--separe', choices=['images', 'spritesheet'], help='Separates the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the image found in the program\'s directory (if it finds it).')
    parser.add_argument('--resize-only', action='store_true', help='When specified, the tool will only resize the images without joining or separing.')
    parser.add_argument('--extract-palette-only', action='store_true', help='When specified, the tool will extract the palette from the images.')
    #directory arguments
    parser.add_argument('-idir', '--input-dir', nargs='+', metavar='DIR', help= 'The input directory, more directories can be specified. The default is ./edit when joining and the same dir as the program (\'.\') when separating.')
    parser.add_argument('-odir', '--output-dir', metavar='DIR', help='The output directory. Unlike --input-dir, you can only specify one. The default is the same dir as the program (\'.\') when joining and is ./output when separating.')
    parser.add_argument('-in', '--input-name', metavar='', help='If given, when joining or separing the tool will search for filenames matching this name.')
    parser.add_argument('-on', '--output-name', metavar='', help='If given, the tool will rename any output images by this name, followed by numbers if there is more than one image. The default is \'image\'') 
    #spritesheet arguments
    parser.add_argument('-spw', '--spritesheet-width', type=int, metavar='', help='The width of the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-sph', '--spritesheet-height', type=int, metavar='', help='The height of the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-imw', '--image-width', type=int, metavar='', help='The width of the images in the spritesheet, will be ignored if joining images normally.')
    parser.add_argument('-imh', '--image-height', type=int, metavar='', help='The width of the images in the spritesheet, will be ignored if joining images normally.')
    #optional arguments, execute certain operations on images
    parser.add_argument('-res', '--resize', default=100, type=int, metavar='', help='Specifies to resize the output image(s) by a certain number. pass 200 to resize them by double, 50 to resize them by half.')
    parser.add_argument('-seppal', '--separate-palette', action='store_true', help='When specified, the tool will the save the palette as a separate image.')
    parser.add_argument('--convert-gifs', action='store_true', help='When specified, it will convert any gif found and include them.')
    parser.add_argument('--include-subdirs', action='store_true', help='When specified, the tool will search for images in subdirectories too.')
    args = parser.parse_args()
    return args

#this function gets the defaults for each action and returns the arguments.
def getDefaults(args):
    if not args.input_dir:
        if args.join or args.resize_only or args.extract_palette_only: args.input_dir = ["./edit"]
        elif args.separe: args.input_dir = ['.']
        else: args.input_dir = []
    if not args.output_dir:
        if args.join: args.output_dir = '.' 
        elif args.separe or args.resize_only or args.extract_palette_only: args.output_dir = "./output"
        else: args.output_dir = '' 
    if not args.output_name:
        if args.join: args.output_name = "joinedImages"
        elif args.separe: args.output_name = "image"
        else: args.output_name = ""
    return args

#this function checks the input directories and the output directories. it'll automatically remove any input directory that doesn't exist, but it'll raise an error if no input directory remains, or if the output directory doesn't exist. when everything is ok, it'll return the directories.
def check_dirs(idir, odir):
    #Check output dir
    if not os.path.isdir(odir):
        raise FileNotFoundError('ERROR: ' + odir + ' was not found. Please make sure it exists first.')

    #Check input dir
    dirsToRemove = []
    for d in idir:
        if not os.path.isdir(d):
            print('ERROR: ' + d + ' was not found. Please make sure it exists first.')
            dirsToRemove.append(d)
    
    #remove any directory that doesn't exist from the input dirs
    for d in dirsToRemove:
        idir.remove(d)
  
    #check if there are still any input directories
    if len(idir) == 0:
        raise FileNotFoundError("ERROR: No real input directory found. Quitting the joining process.")

    if len(dirsToRemove) > 0: 
        print("Any directory not found will be skipped.\n")

    return (idir, odir)

def check_spritesheet_args(args):
    if args.join == "spritesheet" or args.separe == "spritesheet":
        if args.spritesheet_width == None or args.spritesheet_width <= 0:
            raise ValueError("ERROR: Bad argument given to --spritesheet_width")
        elif args.spritesheet_height == None or args.spritesheet_height <= 0:
            raise ValueError("ERROR: Bad argument given to --spritesheet_height")
        elif args.image_width == None or args.image_width <= 0:
            raise ValueError("ERROR: Bad argument given to --image-width")
        elif args.image_height == None or args.image_height <= 0:
            raise ValueError("ERROR: Bad argument given to --image-height")

#this function gets the images on which to operate and returns a list of images. it takes care of various options, like including gifs and filtering based on the input name. note that this ONLY GETS the images, it doesn't do anything else.
def getImages(dirs, match, should_separe, include_gifs, include_subdirs):
    imgList = []
    for d in dirs:
        dirList = []
        print('Searching for images in ' + d + '...')
        for f in sorted(os.listdir(d)):
            if f.endswith('png') or include_gifs and f.endswith('gif'):
                img = Image.open(d + '/' + f)
                print("Found image: " + f)
                if include_gifs:
                    if img.filename[-5:] == 'm.gif':
                        print('This image is a gif mask image. Skipping.')
                        continue
                    if not os.path.isfile(os.path.splitext(img.filename)[0] + 'm.gif'):
                        print('Mask not found. Skipping.')
                        continue
                if should_separe and not os.path.isfile(os.path.splitext(img.filename)[0] + '.cfg'):
                    print('Configuration not found. Skipping.')
                    continue
                if match != None and re.match(match, f) == None:
                    print('The name of the image didn\'t match the input name. Skipping.')
                    continue
                imgList.append(img)
            elif os.path.isdir(d + '/' + f):
                dirList.append(d + '/' + f)
        if include_subdirs and len(dirList) != 0:
            newImgList = getImages(dirList, match, should_separe, include_gifs, include_subdirs)
            imgList += newImgList
    return imgList

def real_main():
    args = getDefaults(getArgs())
    print(args)
    # check if there are any errors with the input and output directories.
    args.input_dir, args.output_dir = check_dirs(args.input_dir, args.output_dir)

    #check if there are any errors with the spritesheet arguments
    check_spritesheet_args(args)

    imageList = getImages(args.input_dir, args.input_name, args.separe, args.convert_gifs, args.include_subdirs)
    if len(imageList) == 0:
        raise ValueError("ERROR: No image found in any directory.")
    
    for img in imgList:
        #do a lot of shit

#Execute main action.
   # if (args.join): joinImages(args.input_dir, args.output_dir, "joinedimages", args.resize, 2, 0)
   # elif (args.separe): separeImages(args.input_dir, args.output_dir, "joinedimages", args.resize, args.separate_palette)
   # else: 
   #     print("ERROR: No action command specified.")
   #     quitProgram()
    #print('\nDone!')

def main():
    try:
        real_main()
    except FileNotFoundError as error:
        print(error)
    except ValueError as error:
        print(error)
    except KeyboardInterrupt:
        print("^C")
        sys.exit
    input("Press any key to continue...")
    sys.exit()

main()
