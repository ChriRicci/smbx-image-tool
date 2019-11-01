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
    parser.add_argument('--skip', '--no-join-or-separe', action='store_true', help='Don\'t join pr separe, instead simply save the images to output directory. This can be used for debugging purposes, or to just do single actions like resizing the images or extracting their palettes.')
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
    parser.add_argument('-sp', '--space', default=0, type=int, metavar='', help='Specified the space between the images. Default is no space.')
    parser.add_argument('-r', '--resize', default=100, type=int, metavar='', help='Specifies to resize the output image(s) by a certain number. pass 200 to resize them by double, 50 to resize them by half.')
    parser.add_argument('--separe-palette', action='store_true', help='When specified, the tool will the save the palette as a separate image.')
    parser.add_argument('--convert-gifs', action='store_true', help='When specified, it will convert any gif found and include them.')
    parser.add_argument('--include-subdirs', action='store_true', help='When specified, the tool will search for images in subdirectories too.')
    args = parser.parse_args()
    return args

#this function gets the defaults for each action and returns the arguments.
def getDefaults(args):
    if not args.input_dir:
        if args.join or args.skip: args.input_dir = ['./edit']
        elif args.separe: args.input_dir = ['.']
        else: args.input_dir = ['nodir']
    if not args.output_dir:
        if args.join: args.output_dir = '.' 
        elif args.separe or args.skip: args.output_dir = './output'
        else: args.output_dir = 'nodir' 
    if not args.output_name:
        if args.join: args.output_name = 'joinedImages'
        elif args.separe: args.output_name = 'image'
        else: args.output_name = 'noname' 
    return args

#this function checks the input directories and the output directories. it'll automatically remove any input directory that doesn't exist, but it'll raise an error if no input directory remains, or if the output directory doesn't exist. when everything is ok, it'll return the directories.
def check_dirs(idir, odir):
    if not os.path.isdir(odir):
        raise FileNotFoundError('ERROR: ' + odir + ' was not found. Please make sure it exists first.')

    dirsToRemove = []
    for d in idir:
        if not os.path.isdir(d):
            print('ERROR: ' + d + ' was not found. Please make sure it exists first.')
            dirsToRemove.append(d)
    for d in dirsToRemove:
        idir.remove(d)
    if len(idir) == 0:
        raise FileNotFoundError("ERROR: No real input directory found. Quitting the joining process.")

    if len(dirsToRemove) > 0: 
        print("Any directory not found will be skipped.\n")
    return (idir, odir)

#this function simply checks if one of the arguments for spritesheets is valid.
def check_spritesheet_arg(arg, argname):
    if arg == None or arg <= 0:
        raise ValueError('ERROR: Bad argument given to ' + argname + '.')

#this function performs various checks on an image. they are done when getting the images.
def check_image(img, match, should_separe):
    if img.filename.endswith('gif'):
        if img.filename[-5:] == 'm.gif':
            raise ValueError('This image is a gif mask image. Skipping.')
        elif not os.path.isfile(os.path.splitext(img.filename)[0] + 'm.gif'):
            raise ValueError('Mask not found. Skipping.')
    elif should_separe and not os.path.isfile(os.path.splitext(img.filename)[0] + '.cfg'):
        raise ValueError('.cfg file not found. Skipping.')
    elif match != None and re.match(match, f) == None:
        raise ValueError('The name of the image didn\'t match the input name. Skipping.')
    return 

#this function gets the images on which to operate and returns a list of images. it takes care of various options, like including gifs and filtering based on the input name. note that this ONLY GETS the images, it doesn't do anything else.
def getImages(dirs, match, should_separe, include_gifs, include_subdirs):
    img_list = []
    for d in dirs:
        dir_list = []
        print('Searching for images in ' + d + '...')

        for f in sorted(os.listdir(d)):
            if f.endswith('png') or include_gifs and f.endswith('gif'):
                img = Image.open(d + '/' + f)
                print("Found image: " + f)
                try:
                    check_image(img, match, should_separe)
                except ValueError as e:
                    print(e)
                    continue
                img_list.append(img)
            elif os.path.isdir(d + '/' + f):
                dir_list.append(d + '/' + f)

        #use recursion to search in subdirectories
        if include_subdirs and len(dirList) != 0:
            img_list += getImages(dirList, match, should_separe, include_gifs, include_subdirs)

    return img_list

def gif_to_png(image, imagemask):
    #TODO
    print('converting ' + image.filename + ' with mask ' + imagemask.filename)

#this function gets the palette of an images. it should sort the colors too TODO
def getPaletteFromImage(img):
    pal = set()
    for _, color in img.convert('RGBA').getcolors():
        if color != (0, 0, 0, 0):
            pal.add(color)
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
    return (img, w, h)

#this function pastes a list of images into an image, using the old method (pasting them horizontally) and with optional space. it assumes the image is big enough and every image in the list is a png. Returns the new image.
def join_images(newimg, img_list, space, maxw, maxh):
    draw = ImageDraw.Draw(newimg)
    x = 0
    for img in img_list:
        w, h = img.size
        diff = int((maxh - h) / 2)
        draw.rectangle([(x, diff), (x + w-1, diff + h-1)], (0, 0, 0, 0))          
        newimg.paste(img, (x, diff))
        x += w + space
    return newimg

#this function parses the cfg file of an image. it takes the filename (complete path) of the cfg file and returns all the lines as a string and real width, height and space of the image the cfg file is associated to. note that 'realw' and 'realh' stand for the image's width and height WITHOUT the palette.
def parse_cfg(filename):
    with open(filename) as cfg:
        lines = cfg.read().splitlines()
        w, h, space = lines[-1].rstrip('\n').split('|')
        lines.remove(lines[-1])
        return (lines, int(w), int(h), int(space))

#this function takes an image and crops the image contained in it. it looks into its .cfg file for specifications. new images are automatically saved into the outpit directory.
def separe_image(img, odir):
    print('Separing image: ' + os.path.basename(img.filename))
    lines, realw, realh, space = parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
    x = 0
    for line in lines:
        line = line.rstrip('\n')
        filename, w, h = line.split('|')
        w, h = int(w), int(h)
        print('Cropping image: ' + filename + ', width: ' + str(w) + ', height: ' + str(h))
        diff = (realh - h) / 2
        img.crop((x, diff, x + w, diff + h)).save(odir + '/' + filename)
        x += w + space

#this function will simply save the images in the output directory.
def save_images(img_list, odir):
    for img in img_list:
        img.save(odir + '/' + os.path.basename(img.filename))

def real_main():
    args = getDefaults(getArgs())
    #error checking with arguments ahead
    args.input_dir, args.output_dir = check_dirs(args.input_dir, args.output_dir)
    if args.join == 'spritesheet' or args.separe == 'spritesheet':
        check_spritesheet_arg(args.spritesheet_width, '--spritesheet-width')
        check_spritesheet_arg(args.spritesheet_height, '--spritesheet-height')
        check_spritesheet_arg(args.image_width, '--image-width')
        check_spritesheet_arg(args.image_height, '--image-height')
    #also some stuff with resizing
    res_num = float(args.resize / 100) 
    if res_num != 1:
        print('The images will be resized.')
   
    #get the images
    image_list = getImages(args.input_dir, args.input_name, args.separe, args.convert_gifs, args.include_subdirs)
    if len(image_list) == 0:
        raise ValueError("ERROR: No image found in any directory.")
    
    #do common operations with images.
    image_configs = '' 
    maxw, maxh = 0, 0
    palette_set = set()
    new_image_list = [] 
    for img in image_list:
        w, h = img.size
        w = int(w * res_num)
        h = int(h * res_num)
        image_configs += os.path.basename(img.filename) + '|' + str(w) + '|' + str(h) + '\n'
        if args.convert_gifs and img.filename.endswith('.gif'):
            gif_to_png(img, Image.open(os.path.splitext(img.filename)[0] + 'm.gif'))
        img = img.resize((w, h), Image.NEAREST)
        #update max width and max height
        if h > maxh:
            maxh = h
        maxw += w + args.space
        #get the image's palette and add it to the palettes
        pal = getPaletteFromImage(img)
        palette_set.add(frozenset(pal))
        #copy the resulting image to a new list and add its filename.
        new_image_list.append(img)

    #get the palette image, then check if it should save it.
    pal_img, palw, palh = get_pal_image(palette_set)
    if args.separe_palette:
        print('Saving palette image in ' + args.output_dir)
        pal_img.save(args.output_dir + '/' + args.output_name + 'Palette.png')
    else:
        if maxw < palw: 
            maxw = palw
        maxh += palh

    if args.join:
        with open(args.output_dir + '/' + args.output_name + '.cfg', 'w') as image_data:
            image_data.write(image_configs + str(maxw) + '|' + str(maxh - palh) + '|' + str(args.space))
        print('Creating new image: width = ' + str(maxw) + '; height = ' + str(maxh))
        new_image = join_images(Image.new('RGBA', (maxw, maxh), (255, 120, 255, 255)).convert("RGBA"), new_image_list, args.space, maxw, maxh- palh)
        if not args.separe_palette:
            print('Pasting palette')
            ImageDraw.Draw(new_image).rectangle([(0, maxh - palh), (0 + palw-1, maxh + palh-1)], (0, 0, 0, 0))
            new_image.paste(pal_img, (0, maxh - palh))
        print('Saving image: ' + args.output_name + '; destination: ' + os.path.abspath(args.output_dir))
        new_image.save(args.output_dir + "/" + args.output_name + ".png")
    elif args.separe:
        for img in new_image_list:
            separe_image(img, args.output_dir)
    elif args.skip:
        save_images(new_image_list, args.output_dir)
    else:
        raise ValueError('No action argument specified. Please specify one of the following:\n --join\n --separe\n --skip')
        
def main():
    try:
        real_main()
    except FileNotFoundError as error:
        print(error)
    except ValueError as error:
        print(error)
    except KeyboardInterrupt:
        print('')
        sys.exit
    input('Press any key to continue...')
    sys.exit()

main()
