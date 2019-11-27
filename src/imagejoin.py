from PIL import Image, ImageDraw
import helperdefs
import os

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

#this function joins images in a spritesheet. it takes a list of images, a max width and height and a space argument and return the joined image.
def join_spritesheet(img_list, space, maxw, maxh):
    print('Creating new spritesheet: width = ' + str(maxw) + '; height = ' + str(maxh))
    new_image = Image.new('RGBA', (maxw, maxh), (255, 120, 255, 255)).convert('RGBA')
    draw = ImageDraw.Draw(new_image)
    x, y = 0, 0
    for img in img_list:
        print('Pasting ' + os.path.basename(img.filename))
        w, h = img.size
        draw.rectangle([(x, y), (x + w - 1, y + h - 1)], (0, 0, 0, 0))          
        new_image.paste(img, (x, y))
        x += space + w
        if y >= maxh:
            print('Some images might not have been pasted.')
            break
        elif x >= maxw:
            x = 0
            y += space + h
    return new_image

#separes an image with cfg file. Whether it's an array of images or a spritesheet is determined by looking into the cfg file. Images are resized and then 
def separe_withcfg(img, odir, resn):
    lines, issp, maxw, maxh, space = helperdefs.parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
    x, y = 0, 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        print('Cropping image: ' + filename + ', width: ' + w + ', height: ' + h + '; ', end='')
        w, h = int(float(w)*resn), int(float(h)*resn)
        if issp:
            cropped_img = img.crop((x, y, x + w, y + h))
            x += space + w
            if x >= maxw:
                x = 0
                y += space + h
        else:
            diff = (maxh - h) / 2
            cropped_img = img.crop((x, diff, x + w, diff + h))
            x += w + space
        cropped_img = cropped_img.resize((w, h), Image.NEAREST)
        save_image(cropped_img, filename, odir)

#this function takes an image and crops the image contained in it. it looks into its .cfg file for specifications. new images are automatically saved into the outpit directory.
def separe_image(img, odir, resn):
    lines, maxw, maxh, space = helperdefs.parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
    x = 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        print('Cropping image: ' + filename + ', width: ' + w + ', height: ' + h + '; ', end='')
        w, h = int(float(w)*resn), int(float(h)*resn)

#this function separes a spritesheet. takes on input the image (assuming it's a spritesheet) and a resizing number and returns a list with every image separated. this version uses a cfg file.
def separe_spritesheet_cfg(img, odir, resn):
    lines, maxw, maxh, space = helperdefs.parse_cfg(os.path.splitext(img.filename)[0] + '.cfg')
    x, y = 0, 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        print('Cropping image: ' + filename + ', width: ' + w + ', height: ' + h + '; ', end='')
        w, h = int(float(w)*resn), int(float(h)*resn)


def separe_spritesheet(img, odir, resn, fn, im_width, im_height, space):
    x, y, f = 0, 0, 1
    maxw, maxh = img.size
    while y < maxh:
        while x < maxw:
            newimg = img.crop((x, y, x + im_width, y + im_height))
            save_image(newimg, fn + str(f) + '.png', odir)
            f += 1
            x += space + im_width
        x = 0
        y += space + im_height

#this function will simply save the images in the output directory.
def save_image(img, fn, odir):
    print('Saving ' + fn + ' to ' + odir)
    img.save(odir + '/' + fn)
