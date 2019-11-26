from PIL import Image, ImageDraw
import palette
import os

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
        w, h, space = lines[-1].rstrip('\n').split('|')
        lines.remove(lines[-1])
        return (lines, int(w), int(h), int(space))

def isposn(n): return n != None and n > 0

def has_right_wh(w, h, imw, imh): return w == imw and h == imh

def is_mask(im): return im.filename[-5:] == 'm.gif'

def has_mask(f): return os.path.isfile(os.path.splitext(f)[0] + 'm.gif')

def has_cfg(im): return os.path.isfile(os.path.splitext(im.filename)[0] + '.cfg')

def check_sp_args(spw, sph, imw, imh): return isposn(spw) and isposn(sph) and isposn(imw) and isposn(imh)

def can_separe_sp(im, imw, imh): return has_cfg(im) or (isposn(imw) and isposn(imh))

#this function checks what the real output directory should be (this is because users can pass same to the -odir argument to save in the same directory as -idir)
def get_save_dir(odir, img): return odir if odir != 'same' else os.path.dirname(img.filename)

#this function gets the images on which to operate and returns a list of images. can search recursively as well.
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
