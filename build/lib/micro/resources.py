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

from   base64 import b64decode
from   configparser import ConfigParser, NoOptionError, NoSectionError
import re, os

from .sdl2 import *
from .sdl2.sdlimage import *
from .sdl2.sdlmixer import *
from .sdl2.sdlttf import *

from .colors import color_from_name


FONT_EXTS  = ['fon', 'ttf']
AUDIO_EXTS = ['aif', 'aiff', 'flac', 'mp3', 'ogg', 'wav']
IMAGE_EXTS = ['bmp', 'gif', 'jpg', 'jpeg', 'png', 'tga', 'tif', 'tiff']


INTERNAL_IMAGES = {
    '.white': {
        'image_b64': '''R0lGODlhAQABAIAAAP7//wAAACH5BAAAAAAALAAAAAAB
                        AAEAAAICRAEAOw=='''
    }
}


def find_resource(name, types, roots):
    rule = re.compile('%s.(%s)' % (name, '|'.join(types)), re.I)

    for root in roots:
        for candidate in os.listdir(root):
            if rule.match(candidate):
                return os.path.join(root, candidate)


def load_tile_desc(width, height, filename):
    config = ConfigParser()
    config.read(filename)
    
    def getint(section, property, default, min, max):
        error = False
         
        try:
            value = config.get(section, property)
        except NoSectionError:
            raise IOError('No section [%s], in file %r' % (section, filename))
        except NoOptionError:
            value = default
        
        try:
            i = int(value)
        except ValueError:
            error = True
        
        if error or i < min or i > max:
            raise IOError('invalid value %r, in file %r, for property %r, of section %r.  Valid values should be integers between %s and %s' % (value, filename, property, section, min, max))
        
        return i
 
    animations = {}
 
    tiles_name = '.tiles'
    for name in config.sections():
        key = name.lower().strip()
        
        if key != '.meta':
            if not re.match(r'[a-z][0-9a-z]+', key):
                raise IOError('invalid animation name %r, in file %r' % (name, filename))
            
            try:
                rate   = config[name].getfloat('rate', 0.0)
            except ValueError:
                raise IOError('invalid frame rate for animation %r, in file %r' % (name, filename))
            
            loop = str(config[name].get('loop', 'loop')).lower()
            if loop not in ('none', 'loop'):
                raise IOError('invalid loop setting for animation %r, in file %r' % (name, filename))
            
            frames = []
            frames_str = str(config[name].get('frames')).split(',')
            for frame in frames_str:
                try:
                    frame = int(frame.strip())
                except ValueError:
                    frame = -1
                
                if frame < 0:
                    raise IOError('invalid frame index for animation %r, in file %r' % (name, filename))
                
                frames.append(frame)
            
            if not frames:
                raise IOError('invalid frame sequence for animation %r, in file %r' % (name, filename))
            
            animations[key] = Animation(rate, loop, *frames)
        else:
            tiles_name = name
                    
        
    shortest    = min(width, height)
    margin      = getint(tiles_name, 'tile_margin', 0, 0, shortest // 2 - (1 - shortest % 2))
    tile_width  = getint(tiles_name, 'tile_width',  width,  1, width - margin * 2)
    tile_height = getint(tiles_name, 'tile_height', height, 1, height - margin * 2)
    spacing     = getint(tiles_name, 'tile_spacing', 0, 0, width - margin * 2 - tile_width)
    colorkey    = config[tiles_name].get('colorkey', None)
    
    if colorkey is not None:
        colorkey = color_from_name(colorkey)

    tile_desc = {
        'tile_margin':  margin,
        'tile_width':   tile_width,
        'tile_height':  tile_height,
        'tile_spacing': spacing,
        'animations':   animations,
        'colorkey':     colorkey
    }
    
    return tile_desc


class AbstractResourceManager:
    def __init__(self, api, resource_type, file_types, meta_file_types=[]):
        self.api = api
        
        self.resource_type   = resource_type
        self.file_types      = file_types
        self.meta_file_types = meta_file_types
        
        self.cache = {}
        
        self.trace = False
    
    
    def load_internal_resource(self, key):
        pass
    
    
    def load_resource(self, key, filename, meta_filename):
        pass
        
        
    def free_resource(self, resource):
        pass
    
    
    def get(self, name, *more_key, internal=False):
        name = name.strip()
        key  = name.lower()
        
        if not internal and not re.match(r'[a-z][0-9a-z]*', key):
            raise ValueError('invalid %s name %r' % (self.resource_type, name))
        
        id  = key
        key = (key,) + more_key
        
        if key in self.cache:
            return self.cache[key]
        elif internal:
            if self.trace: log('loading internal resource %r' % repr(key))
            resource = self.load_internal_resource(key)
           
            if resource:
                self.cache[key] = resource
                return resource
            else:
                raise IOError('failed to load %s named %r' % (self.reosurce_type, name))
        else:
            filename = find_resource(id, self.file_types, self.api.resources_dirs)
            meta_filename = None
            if self.meta_file_types:
                meta_filename = find_resource(id, self.meta_file_types, self.api.resources_dirs)
            
            if filename:
                if self.trace: log('loading resource %r' % repr(key))
                resource = self.load_resource(key, filename, meta_filename)
                if resource:
                    self.cache[key] = resource
                    return resource
                else:
                    raise IOError('failed to load %s named %r' % (self.reosurce_type, name))
        
        raise KeyError('no %s named %r' % (self.resource_type, name))
    
    
    def dispose(self):
        for key, resource in self.cache.items():
            if self.trace: log('freeing resource %r' % repr(key))
            self.free_resource(resource)
            
        self.cache = {}


class FontManager(AbstractResourceManager):
    def __init__(self, api):
        AbstractResourceManager.__init__(self, api, 'font', FONT_EXTS)
    
    
    def load_resource(self, key, filename, meta_filename):
        font = TTF_OpenFont(filename.encode(), key[1])
        return font
        
    
    def free_resource(self, resource):
        TTF_CloseFont(resource)


class ImageManager(AbstractResourceManager):
    def __init__(self, api):
        AbstractResourceManager.__init__(self, api, 'image', IMAGE_EXTS, ['ini'])
        
    
    def load_internal_resource(self, key):
        image     = INTERNAL_IMAGES[key[0]].get('image_b64')
        tile_desc = INTERNAL_IMAGES[key[0]].get('tile_desc', {})
        
        buffer  = b64decode(image.encode())
        rwops   = SDL_RWFromConstMem(buffer, len(buffer))
        surface = IMG_Load_RW(rwops, 1)
        if not surface:
            raise IOError('unable to load image')
        width   = surface.contents.w
        height  = surface.contents.h
        texture = SDL_CreateTextureFromSurface(self.api.renderer, surface)
        SDL_FreeSurface(surface)
        if not texture:
            raise IOError('unable to create texture')
            
        return Image(texture, width, height, **tile_desc)
        
        
    def load_resource(self, key, filename, meta_filename):
        surface = IMG_Load(filename.encode())
        if not surface:
            raise IOError('file %r not found' % filename)
        width   = surface.contents.w
        height  = surface.contents.h
        
        tile_desc = {}
        if meta_filename:
            tile_desc = load_tile_desc(width, height, meta_filename)
            
        colorkey = tile_desc.get('colorkey')
        if colorkey is not None:
            r, g, b, a = colorkey
            SDL_SetColorKey(surface, SDL_TRUE, SDL_MapRGB(surface.contents.format, r, g, b))
        
        texture = SDL_CreateTextureFromSurface(self.api.renderer, surface)
        SDL_FreeSurface(surface)
        if not texture:
            raise IOError('unable to create texture')
            
        return Image(texture, width, height, **tile_desc)
    
    
    def free_resource(self, resource):
        resource.dispose()
        
        
class MusicManager(AbstractResourceManager):
    def __init__(self, api):
        AbstractResourceManager.__init__(self, api, 'music', AUDIO_EXTS)
    
    
    def load_resource(self, key, filename, meta_filename):
        return Mix_LoadMUS(filename.encode())
    
    
    def free_resource(self, resource):
        Mix_FreeMusic(resource)
        
        
class SoundManager(AbstractResourceManager):
    def __init__(self, api):
        AbstractResourceManager.__init__(self, api, 'sound', AUDIO_EXTS)
    
    
    def load_resource(self, key, filename, meta_filename):
        return Mix_LoadWAV(filename.encode())
    
    
    def free_resource(self, resource):
        Mix_FreeChunk(resource)


class TileMapManager(AbstractResourceManager):
    def __init__(self, api):
        AbstractResourceManager.__init__(self, api, 'tile-map', ['txt'])
        
        
    def load_resource(self, key, filename, config):
        tiles_read = False
        width = 0
        rows  = []
        
        with open(filename, 'r') as f:
            for line in f:
                original_line = line.rstrip('\n')
                line = ''.join(re.sub(r'[#;].*', '', line.lower()).split())
                if line:
                    if tiles_read:
                        row = []
                        for tile in line.split(','):
                            if tile and not re.match(r'\d+|[a-z][a-z0-9]*(\*\d+)?', tile):
                                raise IOError('Invalid tile description %r, in %r' % (tile, filename))
                            
                            if not tile: tile = '0'
                            
                            match = re.match(r'(.*?)\*(\d+)', tile)
                            if match:
                                tile  = match.group(1)
                                count = int(match.group(2))
                            else:
                                count = 1
                                
                            for i in range(count):
                                row.append(tile)
                            
                        width = max(width, len(row))
                        rows.append(row)
                    else:
                        if line[:6] in ('tiles:', 'tiles='):
                            tileset = re.split(r'[:=]', line, 1)[1]
                            self.api.resources.get_image(tileset)
                            tiles_read = True
                        else:
                            raise IOError('Expecting tiles: directive but found %r, in %r' % (original_line, filename))
        
        height = len(rows)
        return TileMap(tileset, width, height, rows)
        
        
class ResourceManager:
    def __init__(self, api):
        self.fonts    = FontManager(api)
        self.images   = ImageManager(api)
        self.sounds   = SoundManager(api)
        self.music    = MusicManager(api)
        self.tilemaps = TileMapManager(api)
    
    
    def get_font(self, font, size):
        return self.fonts.get(font, size)
    
    def get_image(self, image, internal=False):
        return self.images.get(image, internal=internal)
    
    def get_sound(self, sound):
        return self.sounds.get(sound)
    
    def get_music(self, music):
        return self.music.get(music)
    
    def get_tilemap(self, tilemap):
        return self.tilemaps.get(tilemap)
    
    
    def dispose(self):
        self.fonts.dispose()
        self.images.dispose()
        self.sounds.dispose()
        self.music.dispose()
        self.tilemaps.dispose()


class Animation:
    def __init__(self, rate, loop, *frames):
        self.rate   = rate
        self.loop   = loop
        self.frames = frames
    
    
    def get_frame(self, time=0.0):
        index = int(time * self.rate)
        
        if self.loop == 'none':
            index = min(index, len(self.frames))
        elif self.loop == 'loop':
            index = index % len(self.frames)
        
        return index + 1
    
    
    def __repr__(self):
        return 'Animation(rate=%r, loop=%r, frames=%r)' % (self.rate, self.loop, self.frames)
            
            
class Image:
    def __init__(self, texture, width, height, **tile_desc):
        self.texture = texture
        self.width   = width
        self.height  = height

        self.tile_width   = tile_desc.get('tile_width',   width)
        self.tile_height  = tile_desc.get('tile_height',  height)
        self.tile_margin  = tile_desc.get('tile_margin',  0)
        self.tile_spacing = tile_desc.get('tile_spacing', 0)

        self.animations = tile_desc.get('animations', {})


    def get_source_rect(self, animation, time=0.0):
        try:
            frame = int(animation)
            if frame == 0:
                return SDL_Rect(0, 0, self.width, self.height)
            else:
                frame -= 1
                
                margin = self.tile_margin
                tile_w = self.tile_width
                tile_h = self.tile_height
                cell_w = tile_w + self.tile_spacing
                cell_h = tile_h + self.tile_spacing
                cols   = (self.width - margin * 2) // tile_w
                
                rect = SDL_Rect()
                rect.x = margin + (frame  % cols) * cell_w
                rect.y = margin + (frame // cols) * cell_h
                rect.w = tile_w
                rect.h = tile_h
                
                return rect
        except ValueError:
            animation = animation.strip()
            key = animation.lower()
            if not re.match(r'[a-z][0-9a-z]+', key):
                raise ValueError('invalid animation name %r' % animation)
            
            try:
                return self.get_source_rect(self.animations[key].get_frame(time))
            except KeyError:
                raise KeyError('no animation called %r' % animation)
        

    def dispose(self):
        SDL_DestroyTexture(self.texture)
        self.texture = None


class TileMap:
    def __init__(self, tileset, width, height, rows):
        self.tileset = tileset
        self.width   = width
        self.height  = height
        self.rows    = rows
    
    
    def get(self, x, y):
        x = x % self.width
        y = y % self.height
        
        row = self.rows[y]
        if x >= len(row):
            return '0'
        else:
            return row[x]
            
