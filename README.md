micro.py
========

A simple multimedia library inspired by the BASIC functions provided by
the micro-computers of the 1980's.  Built on top PySDL2, provides a very
high-level and simplified interface to SDL's input, audio and graphics 
systems.  Aimed at beginner Python programmers and people in a hurry!


How micro.py works
------------------


### Resources


Resource are the multimedia files (images, sound, music and tile-maps)
used by your application.  Each resource is identified by a name, resource
names follow the same rules as Python's variables.  Resources are loaded 
from the resource directory (a parameter of the init() function).  The 
resource directory defaults to the same directory as your applications 
main script. 

When a function needing a resource is called, it is passed a resource name.
The resource is then searched for in the resource directory.  If a file 
with the same name as the resource is found and in a supported format, this
file is loaded and used by the function.  If a matching resource not found 
a KeyError is raised.  If an invalid resource name is provided a ValueError
is raised.  Finally if there is an error during loading the resource an 
IOError is raised.  These exceptions can be raised by all function 
reacquiring a resource.

micro.py support the following resource types.  For images:
 *  Windows Bitmap Images (.bmp)
 *  Graphics Interchange Format (.gif)
 *  Joint Photographic Experts Group (.jpg/.jpeg)
 *  Portable Network Graphics (.png)
 *  Truevision TARGA (.tga)
 *  Tagged Image File Format (.tif/.tiff)
With an optional configuration file (.ini), for storing information 
regarding tile geometry, transparency colours (colorkey) and animations.

Supported fonts formats:
 *  Windows Bitmap Font Files (.fon)
 *  TrueType Font Files (.ttf)
 
Supported sound and music formats:
 *  Audio Intercange Format (.aif/,aiff)
 *  Free Lossless Audio Codec (.flac)
 *  MPEG-1 or MPEG-2 Audio Layer III (.mp3)
 *  Ogg Vorbis (.ogg)
 *  Waveform Audio File Format (.wav)
 
Simple text files (.txt) are used for tile-mapped graphics.


#### Tile-map format example

    # '#' and ';' characters mark the begging of a comment.  All comments
    # and white-space are ignored by the tile-map format.
    
    # The first non-blank line should name the image to use as the source
    # of tiles for this tile-map.
    tiles = my_tiles
    
    # Each subsequent non-blank line is a comma-separated list of either
    # tile indices, or animation names the the source image has defined.
    # Zero is used to define a transparent tile.
    # The following creates a small 4x5 tile-map.
    0,0,bird,0
    1,2,2,3
    4,5,5,6
    4,5,5,6
    4,5,5,6
    7,8,8,9
    
	
#### Image configuration format example

    # The .meta section store information about the image: Tile geometry,
    # and the colour-key (transparent colour).
    [.meta]
    # The width and height (in pixels) of each tile in the image.  Defaults
    # to the total width and height of the image resulting in only one tile
    # being defined.
    tile_width   = 16
    tile_height  = 12
    
    # The number of pixels between each tile
    tile_spacing = 2
    # The number of pixels that surround the entire tile set.
    tile_margin  = 10
    
    # The transparency colour used in this image.
    colorkey     = rgb(255, 0, 255)
    
    # All subsequent sections define animations available for this image.
    [animation1]
    rate   = 10   # The frame rate the animation should run at in fps.
    loop   = loop # The type of loop the animation should run in.
    frames = 1, 2 # The index of the tiles to use as the frames of this 
                  # animation.
    
    [animation2]
    rate   = 20
    loop   = none
    frames = 3, 4, 5, 6
    
	
### Colours

For simplicity all colours in micro.py are specified as strings.  The 
format used is an extended version of what is available in CSS.  Colours
can be specified by name:

    draw_color('red')
    
By hex codes:

    draw_color('#f00')       # #rgb
    draw_color('#ff0000')    # #rrggbb
    draw_color('#f008')      # #rgba
    draw_color('#ff000080')  # #rrggbbaa
    
By rgb, rgba style:

    draw_color('rgb(255, 0, 0)')
    draw_color('rgba(255, 0, 0, 0.5)')
    
An by hsl, hsla style:

    draw_color('hsl(0, 100%, 50%)')
    draw_color('hsla(0, 100%, 50%, 0.5)')
    
	
### Type conversion

All functions in micro.py have a documented type associated with each 
parameter.  Be it int, str, bool, etc.  Where possible functions will 
attempt to convert any value into the correct type.  When this conversion 
is not possible or fails a TypeError is raised.  This means all functions
accepting parameters can raise TypeError's.  It is advisable to ensure 
that values are converted before being passed to a function to avoid 
surprises.
