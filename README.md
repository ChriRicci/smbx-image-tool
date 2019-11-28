# SMBX Image Tool

This is a simple tool made to handle various tasks involving images. The principal task is to join images toghether in a single image, for easy recoloring, and splitting them afterwards. It can also resize images (to do) and import/export spritesheets (to do).

This tool was originally made by FrozenQuills, but I asked and was granted the permission to edit and extend it. Only contributor is me, I'm not asking for any more. 

# Arguments

    Action arguments: 
        --join {images, spritesheet}
        --separe {images, spritesheet}
        --skip, --no-join-or-resize

    Directory arguments:
        --input-dir
        --output-dir
        --output-name

    Filtering arguments:
        --input-name
        --image-width
        --image-height

    Spritesheet arguments:
        --spritesheet-width
        --spritesheet-height

    Other arguments:
        --resize
        --separe-palette
        --convert-gifs
        --include-subdirectories
        --space
