from PIL import Image, ImageDraw
import os
import sys
import re
import helperdefs
import palette
import imagejoin

def real_main():
    args = helperdefs.get_args()
    
    if not args.join and not args.separe and not args.skip:
        args = helperdefs.initUI(args)

    args.input_dir, args.output_dir = helperdefs.check_dirs(args.input_dir, args.output_dir)
    
    #get all the images
    image_list = []
    for d in args.input_dir:
        image_list += helperdefs.get_images(d, args.convert_gifs, args.include_subdirs)
    if len(image_list) == 0:
        raise ValueError("ERROR: No image found in any directory.")

    cfg_str = ''
    max_width, max_height = 0, 0
    palettes = []
    resn = float(args.resize / 100)
    new_image_list = []

    for img in image_list:
        w, h = img.size
        fn = img.filename
        
        try:
            bn = os.path.basename(fn)
            #don't get a gif image if it doesn't have a mask, or if it's a mask.
            if fn.endswith('.gif'):
                if fn.endswith('m.gif'):
                    raise ValueError(bn + ' is a gif mask image. Skipping.')
                #elif not helperdefs.has_mask(fn):
                #    raise FileNotFoundError('Mask not found for ' + bn + '. Skipping.')
            elif args.input_name != None and not re.match(args.input_name, os.path.basename(img.filename)): #output name
                raise ValueError(bn + ': The name of the image didn\'t match the input name. Skipping.')
            elif (args.join or args.skip) and helperdefs.isposn(args.image_width) and helperdefs.isposn(args.image_height) and not helperdefs.has_right_wh(w, h, args.image_width, args.image_height):
                raise ValueError(bn + ': The image doesn\'t have the right width or height.')
        except Exception as e:
            print(e)
            continue

        if img.filename.endswith('.gif'):
            if not helperdefs.has_mask(fn):
                img = helperdefs.gif_to_png(img)
            else:
                img = helperdefs.gif_to_png_mask(img, Image.open(os.path.splitext(img.filename)[0] + 'm.gif'))
            fn = os.path.splitext(fn)[0] + '.png'
        w, h = int(w * resn), int(h * resn);
        cfg_str += os.path.basename(fn) + '|' + str(w) + '|' + str(h) + '\n'
        img = img.resize((w, h), Image.NEAREST)

        #if not joining or separing, we can stop here
        if args.skip:
            save_dir = helperdefs.get_save_dir(args.output_dir, fn, args.same_dir)
            imagejoin.save_image(img, os.path.basename(fn), save_dir)
        #copy the resulting image to a new list and preserve filename
        img.filename = fn 
        new_image_list.append(img)
        
        #get palette and append it to the palette list
        pal = palette.get_palette(img)
        if not palette.check_subset(pal, palettes):
            pal.sort()
            palettes.append(pal)
        
        #only get max_width and max_height when joining
        if not args.join == 'images': 
            continue 
        if h > max_height:
            max_height = h
        max_width += w + args.space
    
    #check again if there are no images
    if len(new_image_list) == 0:
        raise ValueError("ERROR: No image remaining.")
   
    #get an image of the palette (to be pasted on joinedImages or to save separately)
    pal_image = palette.get_pal_image(palettes)
    if args.separe_palette:
        save_dir = helperdefs.get_save_dir(args.output_dir, new_image_list[0].filename, args.same_dir)
        print('Saving palette image in ' + save_dir)
        pal_image.save(save_dir + '/' + args.output_name + 'Palette.png')

    if args.join:
        #error checking for save dir
        if args.same_dir and len(args.input_dir) != 1:
            raise ValueError('ERROR: Saving to the same directory isn\'t supported with multiple input directories. Please specify an output directory.')
        save_dir = helperdefs.get_save_dir(args.output_dir, new_image_list[0].filename, args.same_dir)

        #join the images
        if args.join == 'images':
            new_image = imagejoin.join_images(new_image_list, args.space, max_width, max_height)
            cfg_str += '0|' + str(max_width) + '|' + str(max_height) + '|' + str(args.space)
        else:
            if not helperdefs.check_sp_args(args.spritesheet_width, args.spritesheet_height, args.image_width, args.image_height):
                raise ValueError('ERROR: Can\'t join into a spritesheet without each one of the following:\n --spritesheet-width;\n --spritesheet-height;\n --image-width;\n --image-height')
            max_width = helperdefs.get_max_lenght(args.spritesheet_width, args.image_width, args.space)
            max_height = helperdefs.get_max_lenght(args.spritesheet_height, args.image_height, args.space)
            cfg_str += '1|' + str(max_width) + '|' + str(max_height) + '|' + str(args.space)
            new_image = imagejoin.join_spritesheet(new_image_list, args.space, max_width, max_height)
        
        #paste the palette
        if not args.separe_palette:
            print('Pasting palette')
            new_image = palette.paste_palette(new_image, pal_image)
        
        #Write to the cfg file.
        with open(save_dir + '/' + args.output_name + '.cfg', 'w') as image_data: image_data.write(cfg_str)
        
        #save the joined image
        imagejoin.save_image(new_image, args.output_name + '.png', save_dir)
    if args.separe:
        for img in new_image_list:
            save_dir = helperdefs.get_save_dir(args.output_dir, img.filename, args.same_dir)
            print('Separing image: ' + os.path.basename(img.filename))
            if helperdefs.has_cfg(img):
                try:
                    imagejoin.separe_withcfg(img, save_dir, resn)
                except ValueError as e:
                    print('ERROR: Cannot parse the cfg file correctly.')
            elif helperdefs.can_separe_sp(img, args.image_width, args.image_height):
                imagejoin.separe_spritesheet(img, save_dir, resn, args.output_name, args.image_width, args.image_height, args.space)
            else:
                print('Can\'t separe ' + os.path.basename(img.filename) + '. Skipping.')
