from PIL import Image, ImageDraw
import os

def gif_to_png(image, imagemask):
    #TODO
    print('converting ' + image.filename + ' with mask ' + imagemask.filename)

#this function parses the cfg file of an image. it takes the filename (complete path) of the cfg file and returns all the lines as a string and real width, height and space of the image the cfg file is associated to. note that 'realw' and 'realh' stand for the image's width and height WITHOUT the palette.
def parse_cfg(filename):
    with open(filename) as cfg:
        lines = cfg.read().splitlines()
        w, h, space, spw = lines[-1].rstrip('\n').split('|')
        lines.remove(lines[-1])
        return (lines, int(w), int(h), int(space), int(spw))

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
