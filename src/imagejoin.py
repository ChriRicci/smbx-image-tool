from PIL import Image, ImageDraw
import os

def get_max_lenght(spritesheet_lenght, image_lenght, space):
    return image_lenght * spritesheet_lenght + space * (spritesheet_lenght - 1)

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
    maxw, maxh = get_max_lenght(sp_width, im_width, space), get_max_lenght(sp_height, im_height, space)

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
def separe_spritesheet(img, odir, res_num, lines, space, sp_width):
    x, y = 0, 0
    for line in lines:
        filename, w, h = line.rstrip('\n').split('|')
        w, h = int(float(w)*res_num), int(float(h)*res_num)
        print('Cropping image: ' + filename + ', width: ' + str(w) + ', height: ' + str(h) + '; saving to: ' + odir)
        img.crop((x, y, x + w, y + h)).save(odir + '/' + filename)
        if x >= get_max_lenght(sp_width, space, w):
            x = 0
            y += space + h
        else:
            x += space + w

#this function will simply save the images in the output directory.
def save_images(img, odir):
    print('Saving ' + img.filename + ' to ' + save_dir)
    img.save(odir + os.path.basename(img.filename))
