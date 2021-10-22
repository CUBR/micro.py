# micro.py --  A simple multimedia library.
#
# Copyright (c) 2014 James Cox
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

# CUBR changes:
# 15/9/2021- added comments on potential changes

'''
micro.py - A simple multimedia library inspired by the BASIC functions 
provided by the micro-computers of the 1980's.  Built on top PySDL2, 
provides a very high-level and simplified interface to SDL's input, audio 
and graphics systems.  Aimed at beginner Python programmers and people in 
a hurry!

Notes
-----

Resources
~~~~~~~~~
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

Tile-map format example
^^^^^^^^^^^^^^^^^^^^^^^
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
    
Image configuration format example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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
    
Colours
~~~~~~~
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
    
Type conversion
~~~~~~~~~~~~~~~
All functions in micro.py have a documented type associated with each 
parameter.  Be it int, str, bool, etc.  Where possible functions will 
attempt to convert any value into the correct type.  When this conversion 
is not possible or fails a TypeError is raised.  This means all functions
accepting parameters can raise TypeError's.  It is advisable to ensure 
that values are converted before being passed to a function to avoid 
surprises.
'''


def __init__():
    import atexit
    from   ctypes import c_int, byref, addressof
    import gzip
    import inspect
    import os
    import platform
    import re
    import sys

    
    STDOUT = sys.stdout
    
    
    def log(*args):
        STDOUT.write(' '.join(str(arg) for arg in args) + '\n')
        
    
    def runtime():
        if sys.platform == 'win32':
            bit = 'x64' if sys.maxsize > 2**32 else 'x86'
            return ['windows', bit]
        elif sys.platform[:5] == 'linux':
            return ['linux', platform.machine()]


    os.environ['PYSDL2_DLL_PATH'] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'native', *runtime()))     
    from .sdl2 import (SDL_BLENDMODE_BLEND,
                       SDL_Color,
                       SDL_CreateRenderer,
                       SDL_CreateTexture,
                       SDL_CreateTextureFromSurface,
                       SDL_CreateWindow,
                       SDL_Delay,
                       SDL_DestroyRenderer,
                       SDL_DestroyTexture,
                       SDL_DestroyWindow,
                       SDL_Event,
                       SDL_FLIP_HORIZONTAL,
                       SDL_FLIP_VERTICAL,
                       SDL_FreeSurface,
                       SDL_GetKeyName,
                       SDL_GetNumRenderDrivers,
                       SDL_GetMouseState,
                       SDL_GetRenderDriverInfo,
                       SDL_GetRendererInfo,
                       SDL_GetTicks,
                       SDL_GetWindowSize,
                       SDL_GetWindowTitle,
                       SDL_INIT_AUDIO,
                       SDL_INIT_JOYSTICK,
                       SDL_INIT_VIDEO,
                       SDL_Init,
                       SDL_JoystickClose,
                       SDL_JoystickGetAxis,
                       SDL_JoystickGetButton,
                       SDL_JoystickName,
                       SDL_JoystickNumAxes,
                       SDL_JoystickNumButtons,
                       SDL_JoystickOpen,
                       SDL_JoystickUpdate,
                       SDL_KEYDOWN,
                       SDL_KEYUP,
                       SDL_MapRGB,
                       SDL_NumJoysticks,
                       SDL_PIXELFORMAT_RGB888,
                       SDL_PIXELFORMAT_RGBA8888,
                       SDL_Point,
                       SDL_PollEvent,
                       SDL_QUIT,
                       SDL_Quit,
                       SDL_RENDERER_ACCELERATED,
                       SDL_RENDERER_PRESENTVSYNC,
                       SDL_RENDERER_SOFTWARE,
                       SDL_RENDERER_TARGETTEXTURE,
                       SDL_RWFromConstMem,
                       SDL_Rect,
                       SDL_RendererInfo,
                       SDL_RenderClear,
                       SDL_RenderCopy,
                       SDL_RenderCopyEx,
                       SDL_RenderGetViewport,
                       SDL_RenderPresent,
                       SDL_RenderSetViewport,
                       SDL_SetColorKey,
                       SDL_SetRenderDrawBlendMode,
                       SDL_SetRenderDrawColor,
                       SDL_SetRenderTarget,
                       SDL_SetTextureAlphaMod,
                       SDL_SetTextureColorMod,
                       SDL_SetWindowFullscreen,
                       SDL_SetWindowSize,
                       SDL_SetWindowTitle,
                       SDL_ShowCursor,
                       SDL_TEXTUREACCESS_TARGET,
                       SDL_TRUE,
                       SDL_WINDOWEVENT,
                       SDL_WINDOWEVENT_RESIZED,
                       SDL_WINDOWPOS_CENTERED,
                       SDL_WINDOW_FULLSCREEN_DESKTOP,
                       SDL_WINDOW_RESIZABLE,
                       SDL_WINDOW_SHOWN,
                       SDLK_ESCAPE,
                       SDLK_F11)
    from .sdl2.sdlimage import IMG_Init, IMG_Load, IMG_Load_RW, IMG_Quit
    from .sdl2.sdlttf import (TTF_CloseFont, 
                              TTF_FontAscent,
                              TTF_FontLineSkip,
                              TTF_GetError,
                              TTF_Init,
                              TTF_OpenFont,
                              TTF_OpenFontRW,
                              TTF_Quit,
                              TTF_RenderUTF8_Blended,
                              TTF_RenderUTF8_Solid)
    from .sdl2.sdlmixer import (Mix_CloseAudio,
                                MIX_DEFAULT_FORMAT,
                                Mix_FreeChunk,
                                Mix_FreeMusic,
                                Mix_HaltMusic,
                                MIX_INIT_FLAC,
                                MIX_INIT_MOD,
                                MIX_INIT_MP3,
                                MIX_INIT_OGG,
                                Mix_Init,
                                Mix_LoadWAV,
                                Mix_LoadMUS,
                                MIX_MAX_VOLUME,
                                Mix_OpenAudio,
                                Mix_PauseMusic,
                                Mix_PlayChannel,
                                Mix_PlayMusic,
                                Mix_RewindMusic,
                                Mix_Quit,
                                Mix_Volume,
                                Mix_VolumeMusic)
    
    from .resources import ResourceManager
    from .colors import color_from_name
    from .input import InputHandler
    
    
    class FrameLimiter:
        def __init__(self, api):
            self.api = api
            
            self.rate   = 0
            self._count = 0
            self.last_update = None
            self.frame_start = None
    
        def update(self):
            if self.last_update is None:
                self.last_update = self.api.now()
            
            if self.api.now() - self.last_update > 1.0:
                self.last_update = self.api.now()
                self.rate = self._count
                self._count = 0
                
    
        def count(self):
            self._count += 1
            
            
        def limit(self, fps):
            now = SDL_GetTicks()
            if self.frame_start is None:
                self.frame_start = now
            
            delta = (now - self.frame_start)
            target = 1000 // fps
            
            if delta < target:
                SDL_Delay(target - delta)
                
            self.frame_start = SDL_GetTicks()
            
    
    class OutputRedirector:
        def __init__(self, api):
            self.__api = api
            
            
        def write(self, text):
            self.__api.draw_text(text)
            
        
        def flush(self):
            pass
         

    class GraphicsSettings:
        def __init__(self):
            self.background = 'gray'
            self.fill       = 'black'
            self.draw       = 'white'
            self.x = self.y = 0
            
            self.font      = 'builtin'
            self.font_size = 8
            
        
        @property
        def background(self): return self._bg_value
        @background.setter
        def background(self, value):
            self._bg_color = color_from_name(value)
            self._bg_value = value
            
            
        @property
        def fill(self): return self._fill_value
        @fill.setter
        def fill(self, value):
            self._fill_color = color_from_name(value)
            self._fill_value = value
            
        
        @property
        def draw(self): return self._draw_value
        @draw.setter
        def draw(self, value):
            self._draw_color = color_from_name(value)
            self._draw_value = value    

    
    def integer(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise TypeError('Could not convert {name} into a integer')
            
    
    def floating_point(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise TypeError('Could not convert {name} into a floating-point number')
            
            
    def greater_than_zero(value):
        if value > 0:
            return value
        else:
            raise ValueError('{name} must be greater than zero')
    
    
    def dir_exists(value):
        if os.path.exists(value) and os.path.isdir(value):
            return value
        else:
            raise ValueError('{name} must be a path to an existing directory')
    
    
    class MicroPyApi:
        def public(symbol):
            symbol.export = True
            return symbol

            
        def export(self, target=None):
            if target is None:
                target = globals()
        
            for name in dir(self):
                symbol = getattr(self, name)
                if hasattr(symbol, 'export'):
                    target[symbol.__name__] = symbol
        
        
        @staticmethod
        def check_param(name, value, *rules, ignore_none=False):
            if ignore_none and value is None:
                return
            
            for rule in rules:
                try:
                    value = rule(value)
                except Exception as error:
                    raise type(error)(error.args[0].format(name='`%s`' % name))
                    
            return value
                
                
        def __init__(self):
            self.initialised = False
            
            self.window     = None
            self.renderer   = None
            self.backbuffer = None
            
            self.resources = None
            
            self.input    = None
            self.g        = None
            
            self.original_stdout = None


        def ensure_init(self):
            if not self.initialised:
                self.init()


        @public #P
        def init(self, width=320, height=180, fullscreen=False, title=None, resources_dir=None, redirect_output=True):
            '''
            Initialises the micro.py library.
            
            Creates the graphics window and sets various configurations options used
            throughout micro.py's operation.
            
            Parameters
            ----------
            width: int (greater than zero)
                The width of the graphics window.
            height: int (greater than zero)
                The height of the graphics window.
            fullscreen: bool
                Weather the graphics window should be displayed in fullscreen.
            title: str
                The title of the graphics window.
            resources_dir: str (path to an existing directory)
                The directory where resources should be searched for, and loaded from 
                by micro.py.
            redirect_output:
                Weather STDOUT should be redirected to the graphics window.  This has
                the effect of causing Python's built-in print function to render text
                using micro.py's draw_text function.
            
            Raises
            ------
            RuntimeError
                If initialisation could not be completed.
                
            Notes
            -----
            This function doesn't have to be called by programs using micro.py.  All 
            micro.py function test if init() has been called and if not call init() 
            with it's default options.  This means that if init() hasn't been called
            explicitly, any of micro.py's functions could raise the same exceptions as
            init().
            '''
            
            width           = self.check_param('width', width, integer, greater_than_zero)
            height          = self.check_param('height', height, integer, greater_than_zero)
            fullscreen      = bool(fullscreen) #potentially change to check param
            title           = str(title) if title is not None else None
            resources_dir   = self.check_param('resources_dir', resources_dir, str, dir_exists, ignore_none=True)
            redirect_output = bool(redirect_output) #potentially change to check param
            
            if self.initialised:
                self.quit()
                
            SDL_Init(SDL_INIT_AUDIO | SDL_INIT_JOYSTICK | SDL_INIT_VIDEO)
            IMG_Init(0)
            TTF_Init()
            Mix_Init(0)


            if title is None:
                title = os.path.splitext(os.path.basename(sys.argv[0]))[0]
          
            if resources_dir is None:
                resources_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                
            title = title.encode()
            
            self.frames = FrameLimiter(self)
            
            self.width  = width
            self.height = height
            
            self.window = SDL_CreateWindow(
                    title,
                    SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
                    width, height, SDL_WINDOW_RESIZABLE | SDL_WINDOW_SHOWN)
            if not self.window:
                self.dispose()
                raise RuntimeError('Unable to create main window')

            self.renderer = self.create_renderer()
            if not self.renderer:
                self.dispose()
                raise RuntimeError('Unable to create renderer')
                
            self.backbuffer = SDL_CreateTexture(
                        self.renderer, SDL_PIXELFORMAT_RGB888,
                        SDL_TEXTUREACCESS_TARGET, width, height)
            if not self.backbuffer:
                self.dispose()
                raise RuntimeError('Unable to create backbuffer')
    
            SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_BLEND)
            SDL_SetRenderTarget(self.renderer, self.backbuffer)

            self.resources_dirs = [resources_dir, os.path.join(os.path.dirname(__file__), 'builtin')]
        
            self.g        = GraphicsSettings()
            self.resources = ResourceManager(self)
            
            self.input    = InputHandler(self)

            self.keys    = set()
            self.buttons = {}
            self.axis    = {}
        
            Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024)

            
            if redirect_output:
                self.original_stdout = sys.stdout
                sys.stdout = OutputRedirector(self)
        
            self._running     = True
            self.initialised = True
        
            self._fullscreen = None
            self.fullscreen(fullscreen)
                
            self.clear()
            
            atexit.register(self.quit)
            

        @public #P
        def quit(self):
            '''
            Release all resources allocated by micro.py and closes the graphics window.
            
            Notes
            -----
            This function is automatically called after init() has been called.  
            However when running your scripts in IDLE, atexit handlers  do not work 
            correctly, therefore it is highly advisable that you put a call to quit() 
            at the end of all programs that use micro.py.
            '''
                
            if not self.initialised:
                return
            
            if self.input:
                self.input.dispose()
                self.input = None
                
            if self.resources:
                self.resources.dispose()
                self.resources = None
                
            if self.backbuffer:
                SDL_DestroyTexture(self.backbuffer)
                self.backbuffer = None
            
            if self.renderer:
                SDL_DestroyRenderer(self.renderer)
                self.renderer = None

            if self.window:
                SDL_DestroyWindow(self.window)
                self.window = None

            if self.original_stdout:
                sys.stdout = self.original_stdout
                self.original_stdout = None

            Mix_CloseAudio()

            Mix_Quit()
            TTF_Quit()
            IMG_Quit()
            SDL_Quit()

            self.initialised = False
            
        
        @public #P
        def now(self, start=0.0):
            '''
            Returns the number of seconds since micro.py's init() function was called.

            Optionally can return the number of seconds since `start'.
            
            Parameters
            ----------
            start: float
                The starting point to measure from, the default is 0.0 which is the 
                time init() was called.
                
            Returns
            -------
            float
                number of seconds.
            '''
            
            self.ensure_init()
            
            self.check_param('start', start, floating_point)
            
            return (SDL_GetTicks() / 1000.0) - start
                
                
        #might change the following to parameters
        @public #P
        def background_color(self, color=None):
            '''
            Gets and optionally sets the current background colour.  
            
            This is the colour used when clearing the screen.
            
            Parameters
            ----------
            color: str (colour name)
                The background colour.
            
            Returns
            -------
            str
                The background colour.
                
            Raises
            ------
            ValueError
                If the colour supplied is not a valid colour value.
            '''
            
            self.ensure_init()
            
            if color is not None:
                self.g.background = str(color) #potentially change to check param
            
            return self.g.background

        

        @public #P
        def fill_color(self, color=None):
            '''
            Gets and optionally sets the current fill colour.  
            
            This is the colour used when drawing filled shapes to the screen.
            
            Parameters
            ----------
            color: str (colour name)
                The fill colour.
            
            Returns
            -------
            str
                The fill colour.
            
            Raises
            ------
            ValueError
                If the colour supplied is not a valid colour value.
            '''
            self.ensure_init()
            
            if color is not None:
                self.g.fill = str(color)
            
            return self.g.fill
            
            
        @public #P
        def draw_color(self, color=None):
            '''
            Gets and optionally sets the current draw colour.  
            
            This is the colour used when drawing text, outlined shapes and recolouring
            images and tile-maps.
            
            Parameters
            ----------
            color: str (colour name)
                The fill colour.
            
            Returns
            -------
            str
                The fill colour.
            
            Raises
            ------
            ValueError
                If the colour supplied is not a valid colour value.
            '''
            self.ensure_init()
            
            if color is not None:
                self.g.draw = str(color)
            
            return self.g.draw
            
            
        @public #P
        def font(self, name=None, size=None):
            '''
            Gets and optionally sets the current font.
            
            This is the font used by default, by text drawing functions.
            
            Parameters
            ----------
            name: str
                The name of the font to be set as the current font.
            size: int
                The size of the font to be set as the current font.
            
            Returns
            -------
            str
                The name of the current font.
            int (greater than zero)
                The size of the current font.
                
            Raises
            ------
            ValueError
                If the font name is not a valid resource identifier.
                Or if the font size less than or equal to 0.
            KeyError
                If no font by the given name can be found in the resources_dir.
            '''
            
            name = self.font_name(name)
            size = self.font_size(size)
            
            return name, size

            
        @public #P
        def font_name(self, name=None):
            '''
            Gets and optionally sets the name of the current font.
            
            This is the font used by default, by text drawing functions.
            
            Parameters
            ----------
            name: str
                The name of the font to be set as the current font.
            
            Returns
            -------
            str
                The name of the current font.
                
            Raises
            ------
            ValueError
                If the font name is not a valid resource identifier.
            KeyError
                If no font by the given name can be found in the resources_dir.
            '''
            
            self.ensure_init()
            
            if name is not None:
                name = str(name).strip().lower()
                self.resources.get_font(name, self.g.font_size)
                self.g.font = name
            
            return self.g.font
        
        
        @public #P
        def font_size(self, size=None):
            '''
            Gets and optionally sets the size of current font.
            
            This is the font used by default, by text drawing functions.
            
            Parameters
            ----------
            size: int (greater than zero)
                The size of the font to be set as the current font.
            
            Returns
            -------
            int
                The size of the current font.
                
            Raises
            ------
            ValueError
                If the font size less than or equal to 0.
            '''
            
            self.ensure_init()
            
            if size is not None:
                size = self.check_param('size', size, integer, greater_than_zero)
                self.g.font_size = size
                
            return self.g.font_size
        
        
        @public #P
        def location(self, x=None, y=None):
            '''
            Gets and optionally sets the current location of the graphics cursor.
            
            This location is the default locations used by drawing functions.
            
            Parameters
            ----------
            x: int
                The x location to set the graphics cursor to.
            y: int
                The y location to set the graphics cursor to.
            
            Returns
            -------
            int
                The x location of the graphics cursor.
            int
                The y location of the graphics cursor.
            '''
            self.ensure_init()
            
            if x is not None:
                self.g.x = self.check_param('x', x, integer)
            if y is not None:
                self.g.y = self.check_param('y', y, integer)
            
            return self.g.x, self.g.y
        
        @public #P
        def location_x(self, x=None):
            '''
            Gets and optionally sets the current x location of the graphics cursor.
            
            This location is the default locations used by drawing functions.
            
            Parameters
            ----------
            x: int
                The x location to set the graphics cursor to.
            
            Returns
            -------
            int
                The x location of the graphics cursor.
            '''

            x, _ = location(x)
            return x
        
        @public #P
        def location_y(self, y=None):
            '''
            Gets and optionally sets the current y location of the graphics cursor.
            
            This location is the default locations used by drawing functions.
            
            Parameters
            ----------
            y: int
                The y location to set the graphics cursor to.
            
            Returns
            -------
            int
                The y location of the graphics cursor.
            '''

            _, y = location(y=y)
            return y
            
        
        @staticmethod
        def flip_str_to_flags(flip_str):
            flip_flags = 0
            for ch in flip_str.lower().strip():
                if ch in '-h':
                    if flip_flags & SDL_FLIP_HORIZONTAL:
                        flip_flags &= ~SDL_FLIP_HORIZONTAL
                    else:
                        flip_flags |= SDL_FLIP_HORIZONTAL
                elif ch in '|v':
                    if flip_flags & SDL_FLIP_VERTICAL:
                        flip_flags &= ~SDL_FLIP_VERTICAL
                    else:
                        flip_flags |= SDL_FLIP_VERTICAL
                else:
                    raise ValueError('invalid flip flag %r' % ch)
       
            return flip_flags
        
        
        @public #P
        def clear(self, color=None):
            '''
            Clears the graphics window.
            
            When no colour is specified, the current background colour is used.
            
            Parameters
            ----------
            color: str (color name)
                The colour to fill the background of the graphics window with.
            '''
            self.ensure_init()
            
            self.g.x = 0
            self.g.y = 0
            
            if color is not None:
                rgba = color_from_name(str(color))
            else:
                rgba = self.g._bg_color
            
            SDL_SetRenderDrawColor(self.renderer, *rgba)
            SDL_RenderClear(self.renderer)
            
            
        @public #P
        def draw_image(self, name, x=None, y=None, width=None, height=None, flip='', angle=0.0, time=None, color=None):
            '''
            Draws an image/animation to the graphics window.
            
            Parameters
            ----------
            name: str (resource name)
                The name of the image and optionally the animation or frame to render.
                To specify an animation or frame, simple place a forward slash after 
                the image name followed by either the frame index of animation name.
            x: int #potentially add an image parameter to define the center of the image, center parameter
                The x coordinate of the center of the image to be drawn.
            y: int
                The y coordinate of the center of the image to be drawn.
            width: int
                The width of the image to be drawn.  When no height is specified the 
                width is scaled by the images aspect ratio to provide a hight for 
                the image.
            height: int
                The height of the image to be drawn.  When no width is specified the 
                height is scaled by the images aspect ratio to provide a width for 
                the image.
            flip: str (flip flags)
                The direction (horizontal/vertical) that the image should be flipped 
                by.  This is a string containing the characters 'h' or 'v' to specify;
                horizontal flip and vertical flip respectively.
            angle: float
                The angle (in degrees) to rotate the image by.
            time: float
                The time position (in seconds) into the specified animation.  When not
                specified the current time is used.
            color: str (colour name)
                The colour to recolour the image with.  Defaults to the current draw 
                colour.
            '''
            
            self.ensure_init()

            name   = str(name) #potentially change to check param
            x      = self.check_param('x', x, integer, ignore_none=True)
            y      = self.check_param('y', y, integer, ignore_none=True)
            width  = self.check_param('width', width, integer, ignore_none=True)
            height = self.check_param('height', height, integer, ignore_none=True)
            flip   = str(flip) #potentially change to check param
            angle  = self.check_param('angle', angle, floating_point)
            time   = self.check_param('time', time, floating_point, ignore_none=True)
            color  = str(color) if color is not None else None #potentially change to check param
            
            if time is None: time = self.now()
            
            x = int(self.g.x if x is None else x)
            y = int(self.g.y if y is None else y)
            
            #center parameter
            x += self.width // 2
            y  = self.height // 2 - y
            
            parts      = name.split('/', 2)
            image_name = parts[0]
            if len(parts) == 2:
                anim_name = parts[1]
            else:
                anim_name = '0'
            
            image = self.resources.get_image(image_name)

            if width == 0 or height == 0:
                return
            
            src = image.get_source_rect(anim_name, time)
            if width is None and height is None:
                width = src.w
                height = src.h
            elif width is None:  
                width = int((src.w / src.h) * height)
            elif height is None: 
                height = int((src.h / src.w) * width)
            
            dst = SDL_Rect(x - width // 2, y - height // 2, width, height)
            
            flip_flags = self.flip_str_to_flags(flip)
            
            if width < 0:
                width = -width
                flip_flags |= SDL_FLIP_HORIZONTAL
            if height < 0:
                height = -height
                flip_flags |= SDL_FLIP_VERTICAL
            
            if color is None:
                r, g, b, a = self.g._draw_color
            else:
                r, g, b, a = color_from_name(color)
            
            texture = image.texture
            
            SDL_SetTextureColorMod(texture, r, g, b)
            SDL_SetTextureAlphaMod(texture, a)
            SDL_RenderCopyEx(self.renderer, texture, src, dst, angle, None, flip_flags)


        @public #P
        def fill_rectangle(self, width, height, x=None, y=None, angle=0.0, color=None):
            '''
            Draws a filled rectangle to the graphics window.
            
            Parameters
            ----------
            width: int
                The width of the rectangle to be drawn.
            height: int
                The height of the rectangle to be drawn.
            x: int #center parameter
                The x coordinate of the center of the rectangle to be drawn.
            y: int
                The y coordinate of the center of the rectangle to be drawn.
            anlge: float
                The angle (in degrees) to rotate the rectangle by.
            color: (colour name)
                The colour to fill the rectangle with.  Defaults to the current fill
                colour.
            '''
            
            self.ensure_init()
            
            x      = self.check_param('x', x, integer, ignore_none=True)
            y      = self.check_param('y', y, integer, ignore_none=True)
            width  = abs(self.check_param('width', width, integer, ignore_none=True))
            height = abs(self.check_param('height', height, integer, ignore_none=True))
            angle  = self.check_param('angle', angle, floating_point)
            color  = str(color) if color is not None else None #potentially change to check param
            
            if width == 0 or height == 0:
                return
            
            x = self.g.x if x is None else x
            y = self.g.y if y is None else y
            
            x = int(x)
            y = int(y)
            width  = int(width)
            height = int(height)
            
            #center parameter
            x += self.width // 2
            y  = self.height // 2 - y
            
            if color is None:
                color = self.g._fill_color
            else:
                color = color_from_name(color)
                
            texture = self.resources.get_image('.white', internal=True).texture
            
            rect = SDL_Rect(x - width // 2, y - height // 2, width, height)
            
            r, g, b, a = color

            SDL_SetTextureColorMod(texture, r, g, b)
            SDL_SetTextureAlphaMod(texture, a)
            SDL_RenderCopyEx(self.renderer, texture, None, rect, angle, None, 0)

            
        @public #P
        def draw_text(self, text, x=None, y=None, antialias=False, font_name=None, font_size=None, color=None):
            '''
            Draws text to the graphics window.
            
            When no other parameters are provided, the text is rendered at the graphics
            cursor's location with the text's base-line at the cursors y coordinate.  
            The text by default is not anti-aliased and is rendered in the current font

            and colour.  Afterwards the graphics cursor's location is set at the 
            end of the base-line of the last character rendered.
            

            Parameters

            ----------
            text: str
                The text to be rendered to the graphics window.
            x: int #center parameter
                The x coordinate to start text-rendering.
            y: int
                The y coordinate to start text-rendering.
            antialias: bool
                Weather the text should be anti-aliased (smoothed).

            font_name: str (resource name)
                The name of the font used to render the text.
            font_size: int
                The size of the font used to render the text.

            color: str (colour name)
                The colour used to render the text.
                
            Raises
            ------
            ValueError
                If the font name is not a valid resource identifier.
                Or if the font size less than or equal to 0.

            KeyError
                If no font by the given name can be found in the resources_dir.
            '''
            
            self.ensure_init()
            
            text      = str(text)
            x         = self.check_param('x', x, integer, ignore_none=True)
            y         = self.check_param('y', y, integer, ignore_none=True)
            antialias = bool(antialias)
            font_name = str(font_name) if font_name is not None else None
            font_size = self.check_param('font_size', font_size, integer, greater_than_zero, ignore_none=True)
            color     = str(color) if color is not None else None
            
            if color is None:
                rgba = self.g._draw_color
            else:
                rgba = color_from_name(color)
            
            if font_size is None:
                font_size = self.g.font_size
            
            if font_name is None:
                font_name = self.g.font
                
            ttf = self.resources.get_font(font_name, font_size)
                
            render = TTF_RenderUTF8_Blended if antialias else TTF_RenderUTF8_Solid
            color  = SDL_Color(255, 255, 255, 255)
            assent = TTF_FontAscent(ttf)
            line_h = TTF_FontLineSkip(ttf)
            r, g, b, a = rgba
            
            
            x = self.g.x if x is None else x
            y = self.g.y if y is None else y
            
            left = x
            
            #center parameter
            for line in re.split(r'(\n)', text):
                if line == '\n':
                    y -= line_h
                    x  = -self.width // 2
                elif line:
                    surface = render(ttf, line.encode('utf-8'), color)
                    texture = SDL_CreateTextureFromSurface(self.renderer, surface)
                    SDL_SetTextureColorMod(texture, r, g, b)
                    SDL_SetTextureAlphaMod(texture, a)
                    dst = SDL_Rect((x + self.width // 2), (self.height // 2 - y) - assent, surface.contents.w, surface.contents.h)
                    SDL_FreeSurface(surface)
                    SDL_RenderCopy(self.renderer, texture, None, dst)
                    SDL_DestroyTexture(texture)
                    
                    x += dst.w
            
            self.g.x = x
            self.g.y = y
                
        
        @public #P
        def draw_tilemap(self, name, x=None, y=None, tile_width=None, tile_height=None, time=0.0, color=None):
            '''
            Draws a tile-map to the graphics window.
            
            Parameters
            ----------
            name: str (resource name)
                The name of the tile-map to draw.
            x: int #center parameter
                The x coordinate of the center of the tile-map to be drawn.
            y: int
                The y coordinate of the center of the tile-map to be drawn.
            tile_width: int (greater than zero)
                The width of each individual tile in the tile-map.  When no tile height
                is given the width is scaled by the tile-maps tile's aspect ratio to 
                provide a default tile height.
            tile_height: int (greater than zero)
                The width of each individual tile in the tile-map.  When no tile height
                is given the width is scaled by the tile-maps tile's aspect ratio to 
                provide a default tile height.
            time: float
                The time position (in seconds) into each tiles animation.  When not
                specified the current time is used.
            color: str (colour name)
                The colour to recolour the tile-map with.  Defaults to the current draw
                colour.
            '''
            self.ensure_init()
            
            name        = str(name)
            x           = self.check_param('x', x, integer, ignore_none=True)
            y           = self.check_param('y', y, integer, ignore_none=True)
            tile_width  = abs(self.check_param('tile_width', tile_width, integer, ignore_none=True))
            tile_height = abs(self.check_param('tile_height', tile_height, integer, ignore_none=True))
            time        = self.check_param('time', time, floating_point, ignore_none=True)
            color       = str(color) if color is not None else None #potentially change to check param
            
            if time is None:
                time = self.now()
            else:
                time = float(time)
            #center parameter
            x = int(x if x is not None else self.g.x)
            y = int(y if y is not None else self.g.y)
            
            tilemap = self.resources.get_tilemap(name)
            tileset = self.resources.get_image(tilemap.tileset)
            texture = tileset.texture
            
            if color is None:
                r, g, b, a = self.g._draw_color
            else:
                r, g, b, a = color_from_name(color)
            
            SDL_SetTextureColorMod(texture, r, g, b)
            SDL_SetTextureAlphaMod(texture, a)
            
            if tile_width is None and tile_height is None:
                tile_width  = tileset.tile_width
                tile_height = tileset.tile_height
            elif tile_width is None:
                tile_width = int((tileset.tile_width / tileset.tile_height) * tile_height)
            elif tile_height is None:
                tile_height = int((tileset.tile_height / tileset.tile_width) * tile_width)
            else:
                tile_width  = int(tile_width)
                tile_height = int(tile_height)
            
            left   = (self.width // 2 + x) - (tilemap.width * tile_width) // 2
            right  = left + (tilemap.width * tile_width)
            top    = (self.height // 2 - y) - (tilemap.height * tile_height) // 2
            bottom = top + (tilemap.height * tile_height)
            
            screen_w = self.width // tile_width
            screen_h = self.height // tile_height
            
            start_x = abs(left // tile_width) - 1 if left < 0 else 0
            end_x   = (tilemap.width - right // tile_width + screen_w) + 1 if right // tile_width > screen_w else tilemap.width
            
            start_y = abs(top // tile_height) - 1 if top < 0 else 0
            end_y   = (tilemap.height - bottom // tile_height + screen_h) + 1 if bottom // tile_height > screen_h else tilemap.height
            
            dst = SDL_Rect(0, 0, tile_width, tile_height)
            for r in range(start_y, end_y):
                for c in range(start_x, end_x):
                    tile = tilemap.get(c, r)
                    if tile == '0': continue
                    
                    src = tileset.get_source_rect(tile, time)
                    
                    dst.x = left + c * tile_width
                    dst.y = top + r * tile_height
                    
                    SDL_RenderCopy(self.renderer, texture, src, dst)
        
        
        @public #P
        def update(self, target_fps=None):
            '''
            Updates the screen and reads the state of all input devices.
            
            This function must be called for anything to be displayed on
            the screen, and called regularly for a program to remain
            responsive to input.  When a `target_fps' is specified a 
            small delay is added to the function to attempt to maintain
            that frame-rate.

            Parameter
            ---------
            target_fps: int (greater than zero)
                The frame rate you want the game loop to run at.
                #potentially add a default fps in init
            '''
            
            self.ensure_init()
            
            target_fps = self.check_param('target_fps', target_fps, integer, greater_than_zero, ignore_none=True)
            
            self.input.update()
            
            self.poll()
            
            SDL_SetRenderTarget(self.renderer, None)
            self._update()
            SDL_RenderPresent(self.renderer)
            if target_fps is not None:
                self.frames.limit(target_fps)
                
            SDL_SetRenderTarget(self.renderer, self.backbuffer)
            
            self.frames.count()
            
            
        @public #P
        def keys(self):
            '''
            Returns a set of keys that are currently pressed down on the keyboard.
            
            Returns
            -------
            set of str
                Set of keys currently pressed.
            '''
        
            self.ensure_init()
            return set(self.input.keys.keys())
            
            
        @public #P
        def key(self, key_name):
            '''
            Gets the state of a keyboard key.
            
            Parameters
            ----------
            key_name: str
                The name of the key which is to be queried.
            
            Returns
            -------
            int:
                The number of frames the key has been pressed down for.
            '''
            
            self.ensure_init()
            
            return self.input.key(key_name)
            
        
        @public #P
        def mouse_position(self):
            '''

            Gets the mouse's current position.
            
            Returns
            -------
            int:
                The x location of the mouse.
            int:
                The y location of the mouse.
            '''
            
            self.ensure_init()
        
            return self.input.mouse
            
            
        @public #P
        def mouse_x(self):
            '''
            Gets the mouse's current x position.
            
            Returns
            -------
            int: #potentially add a vec2 type and return this as vec2
                The x location of the mouse.
            '''
            
            self.ensure_init()
            
            x, _ = self.input.mouse
            return x
            
        
        @public #P
        def mouse_y(self):
            '''
            Gets the mouse's current y position.
            
            Returns
            -------
            int:
                The y location of the mouse.
            '''
            
            self.ensure_init()
            
            _, y = self.input.mouse
            return y
            
        
        @public #P
        def mouse_movement(self):
            '''
            Gets the movement of the mouse between frames.
            
            Returns
            -------
            int #potentially add a vec2 type and return this as vec2
                The amount of movement in the x direction.
            int
                The amount of movement in the y direction.
            '''
            self.ensure_init()
        
            return self.input.mouse_rel
            
        
        @public #P
        def mouse_movement_x(self):
            '''
            Gets the x movement of the mouse between frames.
            
            Returns
            -------
            int
                The amount of movement in the x direction.
            '''
            
            self.ensure_init()
        
            x, _ = self.input.mouse_rel
        
            return x
            
        
        @public #P
        def mouse_movement_y(self):
            '''
            Gets the y movement of the mouse between frames.
            
            Returns
            -------
            int
                The amount of movement in the y direction.
            '''
            
            self.ensure_init()
        
            _, y = self.input.mouse_rel
        
            return y
            
            
        @public #P
        def mouse_button(self, button_name):
            '''
            Gets the state of a mouse button.
            
            Parameters
            ----------
            button_name: str
                The name of the button to be queried.
            
            Returns
            -------
            int
                The number of frames the mouse button has been held down.
            '''
            self.ensure_init()
            
            button_name = str(button_name).strip().lower()
            
            return self.input.mouse_buttons.get(button_name, 0)
        
        
        @public #P
        def joysticks(self):
            '''
            Gets a list of joysticks currently connected to the system. 
            #potentially rename joysticks to gamepads or controllers
            The names returned can be used by joy_axis()/joy_daxis() and 
            joy_button() to specify which joystick the should read from.
            
            Returns
            -------
            list of str
                The names of the currently connected joysticks.
            '''
            self.ensure_init()
            
            return list(self.input.joysticks.keys())
        
        
        @public #P
        def joy_axis_count(self, joystick=None):
            '''
            Gets the number of axes the specified joystick has.
            #potentially get info on wether axes are bound together in a stick and combine those
            #potentially a new function like joy_stick_count
            Parameter
            ---------
            joystick: str
                The name of the joystick to get the axis count of.  Defaults to the
                first joystick returned from joysticks().

            Returns
            -------
            int
                The number of axis the joystick has.
            '''
            self.ensure_init()
            
            return self.input.axis_count(joystick)
            
        
        @public #P
        def joy_daxis(self, axis_index, direction, joystick=None):
            '''
            Returns wether the joystick axis is held is a given direction.  
            #potentially rename function to be clearer
            Parameters
            ----------
            axis_index: int
                The index of the axis to read.
            direction: int
                The direction the axis is pointing in, positve or negative.
            joystick: str
                The name of the joystick to get the axis direction of.  Defaults to the
                first joystick returned by joysticks().
                
            Returns
            -------
            int
                The number of frames the axis has been held in the given direction.
            '''
            self.ensure_init()
            
            axis_index = self.check_param('axis_index', axis_index, integer)
            direction  = self.check_param('direction', direction, integer)
            
            # TODO
            return self.input.get_daxis(axis_index, (1 if direction >= 0 else 0), joystick)
        
        
        @public #P
        def joy_axis(self, axis_index, joystick=None):
            '''
            Gets the position of a joystick axis.  
            
            Parameters
            ----------
            axis_index: int
                The index of the axis to read.
            joystick: str
                The name of the joystick to get the axis position of.  Defaults to the
                first joystick returned by joysticks().
                
            Returns
            -------
            float #potentially add a vec2 type and return this as vec2
                The position (-1.0 - 1.0) of the axis.
            '''
            self.ensure_init()
            
            axis_index = self.check_param('axis_index', axis_index, integer)
            
            return self.input.get_axis(axis_index, joystick)
            
        
        @public #P
        def joy_button_count(self, joystick=None):
            '''
            Gets the number of buttons a joystick has.

            Parameters
            ----------
            joystick: str
                The name of the joystick to get the button count of.  Defaults to the
                first joystick returned by joysticks().
            '''
            self.ensure_init()
            
            return self.input.button_count(joystick)
            
        
        @public #P
        def joy_button(self, button_index, joystick=None):
            '''
            Gets the state of a joystick button.

            Parameters
            ----------
            button_index: int
                The index of the button to read.
                #potentially replace or optionally have this as a string of the button name
            joystick: str
                The name of the joystick to get the button state of.  Defaults to the
                first joystick returned by joysticks().
                
            Returns
            -------
            int
                The number of frames the button has been held down for.
            '''
            self.ensure_init()
            
            button_index = self.check_param('button_index', button_index, integer)
            
            return self.input.get_button(button_index, joystick)
            
            
        @public #P
        def fps(self):
            '''
            Gets the current frames per second as timed between calls to update().
            
            Returns
            -------
            int
                The current frames per second.
            '''
            
            self.ensure_init()
            
            self.frames.update()
            return self.frames.rate
            
        
        def create_renderer(self):
            scores = []
            
            for c_index in range(SDL_GetNumRenderDrivers()):
                info = SDL_RendererInfo()
                SDL_GetRenderDriverInfo(c_index, byref(info))
                
                if info.flags & SDL_RENDERER_TARGETTEXTURE:
                    c_score = 0
                    c_accel = 0
                    if not(info.flags & SDL_RENDERER_ACCELERATED):
                        c_score += 1
                        c_accel = SDL_RENDERER_ACCELERATED
                    
                    scores.append((c_score, info))
            
            
            scores.sort(key=lambda t: (t[0], t[1].name), reverse=True)
            
            index    = 0
            renderer = None
            while not renderer and index < len(scores):
                score, info = scores[index]
                renderer = SDL_CreateRenderer(
                    self.window, index, 
                    info.flags & (SDL_RENDERER_ACCELERATED | 
                                  SDL_RENDERER_SOFTWARE | 
                                  SDL_RENDERER_TARGETTEXTURE))

                index += 1

            return renderer
            
        
        @public #P
        def resolution(self, width=None, height=None):
            '''
            Gets and optionally sets the screen resolution.
            
            Parameters
            ----------
            width: int (greater than zero)
                The width to set the screen resolution to.
            height: int (greater than zero)
                The height to set the screen resolution to.
            
            Returns
            -------
            int #potentially add a vec2 type and return this as vec2. would allow things like vec2.width to work same as vec2.x
                The current width of screen resolution.
            int
                The current height of the screen resolution.
            '''
            self.ensure_init()
            
            width  = self.check_param('width', width, integer, greater_than_zero, ignore_none=True)
            height = self.check_param('height', height, integer, greater_than_zero, ignore_none=True)
            
            set = width or height
            
            width  = int(width if width is not None else self.width)
            height = int(height if height is not None else self.height)
            
            if width < 1 or width > 2048:
                raise ValueError('width must be between 1 and 2048')
            if height < 1 or height > 2048:
                raise ValueError('height must be between 1 and 2048')    
            
            if set:
                if self.backbuffer:
                    SDL_DestroyTexture(self.backbuffer)
                    
                self.backbuffer = SDL_CreateTexture(
                        self.renderer, SDL_PIXELFORMAT_RGB888,
                        SDL_TEXTUREACCESS_TARGET, width, height)
                if not self.backbuffer:
                    self.dispose()
                    raise RuntimeError('Unable to create backbuffer')
            
                self.width  = width
                self.height = height
                
                window_w = c_int()
                window_h = c_int()
                SDL_GetWindowSize(self.window, byref(window_w), byref(window_h))
                window_w = window_w.value
                window_h = window_h.value
                
                if self.width > window_w or self.height > window_h:
                    SDL_SetWindowSize(self.window, self.width, self.height)
            
            return width, height
        

        @public #P
        def resolution_width(self, width=None):
            '''
            Gets and optionally sets the width of the screen resolution.
            
            Parameters
            ----------
            width: int (greater than zero)
                The width to set the screen resolution to.
            
            Returns
            -------
            int
                The current width of screen resolution.
            '''
            #function needs implementing

            return resolution(width)[0]
        
        @public #P
        def resolution_height(self, height=None):
            '''
            Gets and optionally sets the height of the screen resolution.
            
            Parameters
            ----------
            height: int (greater than zero)
                The height to set the screen resolution to.
            
            Returns
            -------
            int
                The current height of screen resolution.
            '''
            #function needs implementing

            return resolution(height=height)[1]
        
        
        @public #P
        def title(self, title=None):
            '''
            Gets and optionally sets the title of the graphics window.
            
            This is the text at the top of the graphics window, in the window managers
            title bar.
            
            Parameters
            ----------
            title: str
                The title to display in the title-bar of the graphics window.
            
            Returns
            -------
            str:
                The currently displayed title.
            '''
            self.ensure_init()
            
            if title is not None:
                SDL_SetWindowTitle(self.window, str(title).encode())
            
            return SDL_GetWindowTitle(self.window).decode()
        
        
        @public #P
        def fullscreen(self, fullscreen=None):
            '''
            Gets and optionally sets weather the graphics window is in fullscreen mode.
            #potentially replace with two functions. toggle_fullscreen, and is_fullscreen.
            Parameters
            ----------
            fullscreen: bool
                When specified, set the graphics windows fullscreen state.
            
            Returns
            -------
            bool
                True if the graphics window is fullscreen
            '''
            self.ensure_init()
            
            if fullscreen is not None:
                fullscreen = bool(fullscreen)
                if fullscreen != self._fullscreen:
                    SDL_SetWindowFullscreen(self.window, SDL_WINDOW_FULLSCREEN_DESKTOP if fullscreen else 0)
                    SDL_ShowCursor(1 if not fullscreen else 0)
                    self._fullscreen = fullscreen
        
            return self._fullscreen
        
        
        #@public #g
        def poll(self):
            self.ensure_init()

            event = SDL_Event()
            while SDL_PollEvent(event):
                if event.type == SDL_QUIT:
                    self._running = False
                elif event.type == SDL_WINDOWEVENT:
                    if event.window.event == SDL_WINDOWEVENT_RESIZED:
                        SDL_SetRenderTarget(self.renderer, None)
                        SDL_RenderSetViewport(self.renderer, None)
                        
                        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
                        
                        SDL_RenderClear(self.renderer)
                        self._update()
                        SDL_RenderPresent(self.renderer)
                        
                        SDL_RenderClear(self.renderer)
                        self._update()
                        SDL_RenderPresent(self.renderer)
                        
                        SDL_SetRenderTarget(self.renderer, self.backbuffer)
                elif event.type == SDL_KEYDOWN:
                    if event.key.keysym.sym == SDLK_ESCAPE:
                        self._running = False
                    elif event.key.keysym.sym == SDLK_F11 and not event.key.repeat:
                        self.fullscreen(not self.fullscreen())
                        
                self.input.process(event)

            return self._running


        def _update(self):
            screen = SDL_Rect()
            SDL_RenderGetViewport(self.renderer, byref(screen))
            
            scale  = min(screen.w / self.width, screen.h / self.height)
            width  = int(self.width * scale)
            height = int(self.height * scale)
            rect   = SDL_Rect((screen.w - width) // 2, (screen.h - height) // 2, width, height)
            SDL_RenderCopy(self.renderer, self.backbuffer, None, rect)
            
        #potentially make this a parameter
        @public #P
        def running(self, running=None):
            '''
            Gets and optionally sets weather the game loop should continue running.
            
            Returns False when the escape key is pressed or the close button is pressed
            on the graphics window.
            
            Parameters
            ----------
            running: bool
                The running state to set.
            
            Returns
            -------
            bool
                Weather the game should continue running.
            '''
            self.ensure_init()
            
            if running is not None:
                self._running = bool(running)
            
            return self._running


        @public #P
        def play_sound(self, name, volume=1.0):
            '''
            Plays the named sound effect.
            
            Parameters
            ----------
            name: str (resource name)
                The name of the sound to play.
            volume: float #potentially allow input of percentage volumes, probably detect this if it's above 1
                The volume (0.0 - 1.0) to play the sound at.
            '''
            self.ensure_init()
            #no check param for name
            
            volume = self.check_param('volume', volume, floating_point)
            volume = int(max(0, min(MIX_MAX_VOLUME, (MIX_MAX_VOLUME * float(volume)))))
            
            chunk = self.resources.get_sound(name)
            channel = Mix_PlayChannel(-1, chunk, 0)
            if channel != -1:
                Mix_Volume(channel, volume)
            
            
        @public #P
        def play_music(self, name, volume=1.0):
            '''
            Plays the named background music.
            
            Parameters
            ----------
            name: str
                The name of the background music to play.
            volume: float #potentially allow input of percentage volumes, probably detect this if it's above 1
                The volume (0.0 - 1.0) to play the music at.
            '''
            self.ensure_init()
            #no check param for name
            volume = self.check_param('volume', volume, floating_point)
            volume = int(max(0, min(MIX_MAX_VOLUME, (MIX_MAX_VOLUME * float(volume)))))
            
            music = self.resources.get_music(name)
            Mix_PlayMusic(music, -1)
            Mix_VolumeMusic(volume)
            
        
        @public
        def stop_music(self):
            '''
            Stops the currently playing background music.
            '''
            self.ensure_init()
            
            Mix_HaltMusic()
            Mix_RewindMusic()

        
    # Export the API into the module's global name-space.
    MicroPyApi().export()
    
    # Clean-up the module's global name-space.
    del globals()['__init__']
    del globals()['MicroPyApi']


__init__()

