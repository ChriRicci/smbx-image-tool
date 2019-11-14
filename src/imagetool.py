from PIL import Image, ImageDraw
import os
import sys
import argparse
import collections
import helperDefs
import palette
import imageJoin

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
    parser.add_argument('-idir', '--input-dir', nargs='+', metavar='DIR', default=[sys.path[0] + '/edit'], help= 'The input directory, more directories can be specified. The default is "./edit".')
    parser.add_argument('-odir', '--output-dir', metavar='DIR', default=sys.path[0] + '/output', help='The output directory. Unlike --input-dir, you can only specify one. The default is "./output".')
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
    return odir if odir != 'same' else os.path.dirname(img.filename)

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
        image_list += helperDefs.get_images(d, args.convert_gifs, args.include_subdirs)
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
            helperDefs.check_image(img, args.join, args.separe, args.image_width, args.image_height, args.input_name)
        except Exception as e:
            print(e)
            continue
        w, h = img.size
        w = int(w * res_num)
        h = int(h * res_num)
        f = img.filename
        image_configs += os.path.basename(img.filename) + '|' + str(w) + '|' + str(h) + '\n'
        if img.filename.endswith('.gif'):
            img = helperFunctions.helperDefs.gif_to_png(img, Image.open(os.path.splitext(img.filename)[0] + 'm.gif'))

        img = img.resize((w, h), Image.NEAREST)

        #copy the resulting image to a new list and add its filename.
        img.filename = f
        new_image_list.append(img)
        
        #only get palette, maxw and maxh when joining
        if args.join:
            if h > maxh:
                maxh = h
            maxw += w + args.space
            palette_set.add(frozenset(palette.get_palette(img)))

    if len(new_image_list) == 0:
        raise ValueError("ERROR: No image remaining.")

    if args.join:
        if args.output_dir == 'same' and len(args.input_dir) != 1:
            raise ValueError('ERROR: Saving to the same directory isn\'t supported with multiple input directories. Please specify an output directory.')
        save_dir = get_save_dir(args.output_dir, new_image_list[0])

        with open(save_dir + '/' + args.output_name + '.cfg', 'w') as image_data:
            image_data.write(image_configs + str(maxw) + '|' + str(maxh) + '|' + str(args.space) + '|' + str(args.spritesheet_width))

        if args.join == 'images':
            new_image = imageJoin.join_images(new_image_list, args.space, maxw, maxh)
        else:
            new_image = imageJoin.join_spritesheet(new_image_list, args.space, args.spritesheet_width, args.spritesheet_height, args.image_width, args.image_height)

        pal_image = palette.get_pal_image(palette_set)
        if args.separe_palette:
            print('Saving palette image in ' + save_dir)
            pal_image.save(save_dir + '/' + args.output_name + 'Palette.png')
        else:
            print('Pasting palette')
            new_image = palette.paste_palette(new_image, pal_image)

        print('Saving image: ' + args.output_name + '; destination: ' + save_dir)
        new_image.save(save_dir + '/' + args.output_name + '.png')

    elif args.separe:
        for img in new_image_list:
            save_dir = get_save_dir(args.output_dir, img)
            print('Separing image: ' + os.path.basename(img.filename))
            try:
                lines, maxw, maxh, space, spw = helperDefs.parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
                if args.separe == 'images':
                    imageJoin.separe_image(img, save_dir, res_num, lines, space, maxh)
                else:
                    imageJoin.separe_spritesheet(img, save_dir, res_num, lines, space, spw)
            except ValueError as e:
                print('ERROR: Cannot parse the cfg file correctly.')
    elif args.skip:
        save_dir = get_save_dir(args.output_dir, img)
        for img in new_image_list:
            imageJoin.save_images(img, args.output_dir)
    else:
        raise ValueError('No action argument specified. Please specify one of the following:\n --join\n --separe\n --skip')
