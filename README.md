# Super Mario Bros X Image Tool

This is a simple tool made to handle various tasks involving images. The principal task is to join images toghether in a single image, for easy recoloring, and splitting them afterwards. It can also resize images (to do) and import/export spritesheets (to do).

This tool was originally made by FrozenQuills, but I asked and was granted the permission to edit and extend it. Only contributor is me, I'm not asking for any more. 

# Arguments

Action arguments: 
- --join {images, spritesheet}
- --separe {images, spritesheet}
- --skip, --no-join-or-resize

I/O arguments:
- --input-dir
- --output-dir
- --input-name
- --output-name

Spritesheet arguments:
- --spritesheet-width
- --spritesheet-height
- --image-width
- --image-height

Optional arguments:
- --resize
- --separate-palette
- --convert-gifs
- --include-subdirectories
- --space

# To Do
- Add support for spritesheet (i.e. use the spritesheet arguments instead of pasting the images horizontally)
- Sort the colors when getting a palette from an image
- Support converting a gif with mask
- Add new.py as a module for imagetool.py and paste all helper functions there
- Try to make the code more readable, think of better ways to do some stuff
