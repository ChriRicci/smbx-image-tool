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
def get_args():
    #help and version arguments
    parser = argparse.ArgumentParser(description='This is a tool which can help in various tasks related to images. It can join images for easy recoloring, separing them, quickly resize all of them and much more.')
    parser.add_argument('-v', '--version', action='version', version='SMBX Image Tool version 1.3')
    #action arguments
    parser.add_argument('-j', '--join', choices=['images', 'spritesheet'], help='Joins the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the directory ./edit, located in the program\'s directory. You can choose between joining images normally (by writing \'images\' after --join) or joining in a spritesheet (by writing \'spritesheet\'). If joining in a spritesheet, you\'ll need to specify --width and --height too.\n')
    parser.add_argument('-s', '--separe', choices=['images', 'spritesheet'], help='Separates the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the image found in the program\'s directory (if it finds it).')
    parser.add_argument('--skip', '--no-join-or-separe', action='store_true', help='Don\'t join pr separe, instead simply save the images to output directory. This can be used for debugging purposes, or to just do single actions like resizing the images or extracting their palettes.')
    #directory arguments
    parser.add_argument('-idir', '--input-dir', nargs='+', metavar='DIR', default=['./edit'], help= 'The input directory, more directories can be specified. The default is "./edit".')
    parser.add_argument('-odir', '--output-dir', metavar='DIR', default='./output', help='The output directory. Unlike --input-dir, you can only specify one. The default is "./output".')
    parser.add_argument('-in', '--input-name', metavar='', help='If given, when joining or separing the tool will search for filenames matching this name.')
    parser.add_argument('-on', '--output-name', metavar='', default='joinedImages', help='If given, the tool will rename any output images by this name, followed by numbers if there is more than one image. The default is \'joinedImages\'') 
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

#this function checks the input directories and the output directories. it'll automatically remove any input directory that doesn't exist, but it'll raise an error if no input directory remains, or if the output directory doesn't exist. when everything is ok, it'll return the directories.
def check_dirs(idir, odir):
    if not os.path.isdir(odir) and odir != 'same':
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

#this function checks what the real output directory should be (this is because users can pass same to the -odir argument to save in the same directory as -idir)
def get_save_dir(odir, img):
    if odir == 'same':
        save_dir = os.path.dirname(img.filename)
    else:
        save_dir = odir
    return save_dir

def gif_to_png(image, imagemask):
    #TODO
    print('converting ' + image.filename + ' with mask ' + imagemask.filename)

#this function gets the palette of an images. it should sort the colors too TODO
def get_pal(img):
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

#this function parses the cfg file of an image. it takes the filename (complete path) of the cfg file and returns all the lines as a string and real width, height and space of the image the cfg file is associated to. note that 'realw' and 'realh' stand for the image's width and height WITHOUT the palette.
def parse_cfg(filename):
    with open(filename) as cfg:
        lines = cfg.read().splitlines()
        w, h, space = lines[-1].rstrip('\n').split('|')
        lines.remove(lines[-1])
        return (lines, int(w), int(h), int(space))

#this function performs various checks on an image. they are done when getting the images.
def check_image(im, should_join, should_separe, imw, imh, match):
    basename = os.path.basename(im.filename)
    w, h = im.size
    if im.filename.endswith('gif'):
        if im.filename[-5:] == 'm.gif':
            raise ValueError(basename + ' is a gif mask image. Skipping.')
        elif not os.path.isfile(os.path.splitext(im.filename)[0] + 'm.gif'):
            raise FileNotFoundError('Mask not found for ' + basename + '. Skipping.')
    elif should_separe and not os.path.isfile(os.path.splitext(im.filename)[0] + '.cfg'):
        raise FileNotFoundError('.cfg file not found for ' + basename + '. Skipping.')
    elif match != None and re.match(match, basename) == None:
        raise ValueError(basename + ': The name of the image didn\'t match the input name. Skipping.')
    elif should_join == 'spritesheet' and (w != imw or h != imh):
        raise ValueError(basename + ': The image doesn\'t have the right width or height.')
    return 

#this function gets the images on which to operate and returns a list of images. it takes care of various options, like including gifs and filtering based on the input name. note that this ONLY GETS the images, it doesn't do anything else.
def get_images(d, include_gifs, include_subdirs):
    img_list = []
    print('Searching for images in ' + os.path.abspath(d) + '...')
    for f in sorted(os.listdir(d)):
        if f.endswith('png') or include_gifs and f.endswith('gif'):
            print("Found image: " + f)
            img_list.append(Image.open(d + '/' + f))
        elif os.path.isdir(d + '/' + f):
            img_list += get_images(d + '/' + f, include_gifs, include_subdirs)
    return img_list

#this function pastes a list of images into an image, using the old method (pasting them horizontally) and with optional space. it assumes the image is big enough and every image in the list is a png. Returns the new image.
def join_images(img_list, space, maxw, maxh):
    print('Creating new image: width = ' + str(maxw) + '; height = ' + str(maxh))
    new_image = Image.new('RGBA', (maxw, maxh), (255, 120, 255, 255)).convert("RGBA")
    draw = ImageDraw.Draw(new_image)
    x = 0
    for img in img_list:
        print('Pasting ' + os.path.basename(img.filename))
        w, h = img.size
        diff = int((maxh - h) / 2)
        draw.rectangle([(x, diff), (x + w-1, diff + h-1)], (0, 0, 0, 0))          
        new_image.paste(img, (x, diff))
        x += w + space
    return new_image

#this function joins images in a spritesheet. takes an image list, a space argument and each spritesheet argument. it won't try to figure out by itself how to lay out the images, instead it uses the spritesheet arguments for this job. this means there might be not enough space for every images.
#the function returns an image with each image from the list pasted in it.
def join_spritesheet(img_list, space, sp_width, sp_height, im_width, im_height):
    maxw = sp_width * im_width + space * (sp_width - 1)
    maxh = sp_height * im_height + space * (sp_height - 1)

    print('Creating new spritesheet: width = ' + str(maxw) + '; height = ' + str(maxh))
    new_image = Image.new('RGBA', (maxw, maxh), (255, 120, 255, 255)).convert("RGBA")

    draw = ImageDraw.Draw(new_image)
    x, y = 0, 0
    for img in img_list:
        print('Pasting ' + os.path.basename(img.filename))
        w, h = img.size
        draw.rectangle([(x, y), (x + im_width, y + im_height)], (0, 0, 0, 0))          
        new_image.paste(img, (x, y))
        if y >= maxh:
            print('Some images might not have been pasted.')
            break
        elif x >= maxw:
            x = 0
            y += space + im_height
        else:
            x += space + im_width
    return new_image

#this function takes an image and crops the image contained in it. it looks into its .cfg file for specifications. new images are automatically saved into the outpit directory.
def separe_image(img, odir, res_num, lines, space, maxh):
    x = 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        w, h = int(float(w)*res_num), int(float(h)*res_num)
        print('Cropping image: ' + filename + ', width: ' + str(w) + ', height: ' + str(h) + '; saving to: ' + odir)
        diff = (maxh - h) / 2
        img.crop((x, diff, x + w, diff + h)).save(odir + '/' + filename)
        x += w + space

#this function separes a spritesheet. takes on input the image (assuming it's a spritesheet) and a resizing number and returns a list with every image separated. this version uses a cfg file.
def separe_spritesheet(img, odir, res_num, lines, space, maxw):
    x, y = 0, 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        w, h = int(float(w)*res_num), int(float(h)*res_num)
        print('Cropping image: ' + filename + ', width: ' + str(w) + ', height: ' + str(h) + '; saving to: ' + odir)
        img.crop((x, y, x + w, y + h)).save(odir + '/' + filename)
        if x >= maxw:
            x = 0
            y += space + h
        else:
            x += space + w

#this function will simply save the images in the output directory.
def save_images(img, odir):
    save_dir = get_save_dir(odir, img)
    print('Saving ' + img.filename + ' to ' + save_dir)
    img.save(odir + os.path.basename(img.filename))

def real_main():
    args = get_args()
    #error checking with arguments ahead
    args.input_dir, args.output_dir = check_dirs(args.input_dir, args.output_dir)
    if args.join == 'spritesheet' or args.separe == 'spritesheet':
        check_spritesheet_arg(args.spritesheet_width, '--spritesheet-width')
        check_spritesheet_arg(args.spritesheet_height, '--spritesheet-height')
        check_spritesheet_arg(args.image_width, '--image-width')
        check_spritesheet_arg(args.image_height, '--image-height')

    #get the images
    image_list = []
    for d in args.input_dir:
        image_list += get_images(d, args.convert_gifs, args.include_subdirs)
    if len(image_list) == 0:
        raise ValueError("ERROR: No image found in any directory.")
    
    #check if the image is valid, then do common operations (get config, resize, get max width and height and get palette)
    image_configs = '' 
    maxw, maxh = 0, 0
    palette_set = set()
    res_num = float(args.resize / 100) 
    new_image_list = [] 
    for img in image_list:
        try:
            check_image(img, args.join, args.separe, args.image_width, args.image_height, args.input_name)
        except Exception as e:
            print(e)
            continue
        w, h = img.size
        w = int(w * res_num)
        h = int(h * res_num)
        f = img.filename
        image_configs += os.path.basename(img.filename) + '|' + str(w) + '|' + str(h) + '\n'
        if img.filename.endswith('.gif'):
            img = gif_to_png(img, Image.open(os.path.splitext(img.filename)[0] + 'm.gif'))

        img = img.resize((w, h), Image.NEAREST)

        #copy the resulting image to a new list and add its filename.
        img.filename = f
        new_image_list.append(img)
        
        #only get palette, maxw and maxh when joining
        if args.join:
            if h > maxh:
                maxh = h
            maxw += w + args.space

            palette_set.add(frozenset(get_pal(img)))

    if len(new_image_list) == 0:
        raise ValueError("ERROR: No image remaining.")

    if args.join:
        #output_dir related
        if args.output_dir == 'same' and len(args.input_dir) != 1:
            raise ValueError('ERROR: Saving to the same directory isn\'t supported with multiple input directories. Please specify an output directory.')
        save_dir = get_save_dir(args.output_dir, new_image_list[0])

        with open(save_dir + '/' + args.output_name + '.cfg', 'w') as image_data:
            image_data.write(image_configs + str(maxw) + '|' + str(maxh) + '|' + str(args.space))

        if args.join == 'images':
            new_image = join_images(new_image_list, args.space, maxw, maxh)
        else:
            new_image = join_spritesheet(new_image_list, args.space, args.spritesheet_width, args.spritesheet_height, args.image_width, args.image_height)

        pal_image = get_pal_image(palette_set)
        if args.separe_palette:
            print('Saving palette image in ' + save_dir)
            pal_image.save(save_dir + '/' + args.output_name + 'Palette.png')
        else:
            print('Pasting palette')
            new_image = paste_palette(new_image, pal_image)

        #save image
        print('Saving image: ' + args.output_name + '; destination: ' + save_dir)
        new_image.save(save_dir + '/' + args.output_name + '.png')

    elif args.separe:
        for img in new_image_list:
            save_dir = get_save_dir(args.output_dir, img)
            print('Separing image: ' + os.path.basename(img.filename))
#            try:
            lines, maxw, maxh, space = parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
            if args.separe == 'images':
                separe_image(img, save_dir, res_num, lines, space, int(maxh))
            else:
                separe_spritesheet(img, save_dir, res_num, lines, space, int(maxw))
#            except ValueError as e:
#                print('ERROR: Cannot parse the cfg file correctly.')
    elif args.skip:
        for img in new_image_list:
            save_images(img, args.output_dir)
    else:
        raise ValueError('No action argument specified. Please specify one of the following:\n --join\n --separe\n --skip')
        
def main():
    try:
        real_main()
    except FileNotFoundError as error:
        print(error)
#    except ValueError as error:
#        print(error)
    except re.error:
        print('ERROR: --input-name not a valid REGEX.')
    except KeyboardInterrupt:
        print('')
        sys.exit()
    input('Press any key to continue...')
    sys.exit()

main()
