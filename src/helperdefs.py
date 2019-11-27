from PIL import Image, ImageDraw
import palette
import os
import sys
import argparse

#this function simply returns all the arguments. i made this to separe the argument stuff from the main.
def get_args():
    #help and version arguments
    parser = argparse.ArgumentParser(description='This is a tool which can help in various tasks related to images. It can join images for easy recoloring, separing them, quickly resize all of them and much more.')
    parser.add_argument('-v', '--version', action='version', version='SMBX Image Tool version 1.3')
    #action arguments
    parser.add_argument('-j', '--join', choices=['images', 'spritesheet'], help='Joins the images in the folder specified by --input-dir. When --input-dir is not specified, it will use the directory ./edit, located in the program\'s directory. You can choose between joining images normally (by writing \'images\' after --join) or joining in a spritesheet (by writing \'spritesheet\'). If joining in a spritesheet, you\'ll need to specify --width and --height too.\n')
    parser.add_argument('-s', '--separe', action='store_true', help='Separes the images in the folder specified by --input-dir. It can only separe images with a .cfg file (created with --join), but can separe other images if --image-width and --image-height are specified.')
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
def gif_to_png(im, immask):
    #convert the images
    im = im.convert('RGBA')
    immask = immask.convert('RGBA')
    #change all white pixels in the mask to trasparency
    immask.putdata(palette.replace_color(immask.getdata(), (255, 255, 255, 255), (255, 255, 255, 0)))
    #change all black pixels in the image to trasparency
    im.putdata(palette.replace_color(im.getdata(), (0, 0, 0, 255), (255, 255, 255, 0)))
    #paste the image
    immask.paste(im, (0, 0), im)
    return immask

#this function parses the cfg file of an image. it takes the filename of the cfg file and returns all the lines related to the images contained in it, plus width, height and space of the joined image (converted to int)
def parse_cfg(filename):
    with open(filename) as cfg:
        lines = cfg.read().splitlines()
        t, w, h, space = lines[-1].rstrip('\n').split('|')
        lines.remove(lines[-1])
        return (lines, int(t), int(w), int(h), int(space))

def isposn(n): return n != None and n > 0

def has_right_wh(w, h, imw, imh): return w == imw and h == imh

def is_mask(im): return im.filename[-5:] == 'm.gif'

def has_mask(f): return os.path.isfile(os.path.splitext(f)[0] + 'm.gif')

def has_cfg(im): return os.path.isfile(os.path.splitext(im.filename)[0] + '.cfg')

def check_sp_args(spw, sph, imw, imh): return isposn(spw) and isposn(sph) and isposn(imw) and isposn(imh)

def can_separe_sp(im, imw, imh): return has_cfg(im) or (isposn(imw) and isposn(imh))

#this function checks what the real output directory should be (this is because users can pass same to the -odir argument to save in the same directory as -idir)
def get_save_dir(odir, fn): return odir if odir != 'same' else os.path.dirname(fn)

#this function gets the images on which to operate and returns a list of images. can search recursively as well.
def get_images(d, include_gifs, include_subdirs):
    img_list = []
    print('Searching for images in ' + os.path.abspath(d) + '...')
    for f in sorted(os.listdir(d)):
        if f.endswith('png') or include_gifs and f.endswith('gif'):
            print("Found image: " + f)
            img_list.append(Image.open(d + '/' + f))
        elif os.path.isdir(d + '/' + f) and include_subdirs:
            img_list += get_images(d + '/' + f, include_gifs, include_subdirs)
    if len(img_list) == 0: print('No images found.')
    return img_list

def get_max_lenght(spritesheet_lenght, image_lenght, space):
    return image_lenght * spritesheet_lenght + space * (spritesheet_lenght - 1)

#edits a filename until it is unique in the directory it should be in.
def get_filename(f, d):
    num = 2
    newf = f
    while os.path.isfile(d + '/' + newf):
        bn, ext = os.path.splitext(f)
        newf = bn + ' (' + str(num) + ')' + ext
        num += 1
    return newf

#this function checks the input directories and the output directories. it'll automatically remove any input directory that doesn't exist, but it'll raise an error if no input directory remains, or if the output directory doesn't exist. when everything is ok, it'll return the directories.
def check_dirs(idir, odir):
    if not os.path.isdir(odir) and odir != 'same':
        raise FileNotFoundError('ERROR: ' + odir + ' was not found. Please make sure it exists first.')

    dirsToRemove = []
    for d in idir:
        if not os.path.isdir(d):
            print('ERROR: ' + d + ' was not found. Please make sure it exists first. (The directory will be removed)')
            dirsToRemove.append(d)
    for d in dirsToRemove:
        idir.remove(d)
    if len(idir) == 0:
        raise FileNotFoundError("ERROR: No real input directory found. Quitting the joining process.")

    if len(dirsToRemove) > 0: 
        print("Any directory not found will be skipped.\n")
    return (idir, odir)

def initUI(args):
    print('=== SMBX Image Tool ===', end='\n\n')
    print('Choose one of the following:')
    print('    1. Join all the images from \'edit\' directory')
    print('    2. Join all the images from \'edit\' directory into a spritesheet')
    print('    3. Separe the image/spritesheet \'joinedImages.png\' from the current directory')
    print('    4. Separe a spritesheet without a cfg file')
    print('    5. Resize all the images from \'edit\' directory by 50% or 200%')
    print('    6. Generate the palette from the images from \'edit\' directory')
    
    try:
        choice = int(input('Please insert a number from 1 to 6: '))
    except ValueError as e:
        raise type(e)('Invalid choice.')
    if choice < 1 or choice > 6:
        raise ValueError('Invalid choice.')

    if choice == 1:
        args.join = 'images'
        args.output_dir = os.getcwd()
    elif choice == 2:
        args.join = 'spritesheet'
        args.output_dir = os.getcwd()
        print('To join into a spritesheet, you\'ll need to insert width and height (in number of images) for the spritesheet and the size (in pixels) for a single image.')
        try:
            args.spritesheet_width = int(input('Insert the spritesheet width: '))
            args.spritesheet_height = int(input('Insert the spritesheet height: '))
            args.image_width = int(input('Insert the image width: '))
            args.image_height = int(input('Insert the image height: '))
        except ValueError as e:
            raise type(e)('Invalid choice.')
    elif choice == 3:
        args.separe = True
        args.input_dir = [os.getcwd()]
        args.input_name = 'joinedImages.png'
    elif choice == 4:
        args.separe = 'spritesheet'
        args.input_dir = [os.getcwd()]
        args.output_dir = './output'
        args.input_name = input('Insert the name of the image (with extension)(make sure it doesn\'t have a cfg file): ')
        args.output_name = input('Insert the name you want to give to the cropped images (a number will be added at the end): ')
        print('To separe a spritesheet, you\'ll need to insert the size (in pixels) for a single image.')
        try:
            args.image_width = int(input('Insert the image width: '))
            args.image_height = int(input('Insert the image height: '))
        except ValueError as e:
            raise type(e)('Invalid choice.')
    elif choice == 5:
        args.skip = True
        args.output_dir = 'same'
        try:
            args.resize = int(input('Insert a resize number (in %): '))
        except ValueError as e:
            raise type(e)('Invalid choice.')
    elif choice == 6:
        args.skip = True
        args.output_dir = 'same'
        args.output_name = 'images'
        args.separe_palette = True
    print('')
    return args
