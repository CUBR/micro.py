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

from   ctypes import c_int, byref, addressof
import re

from .sdl2 import *


class Joystick:
    def __init__(self, sdl_joystick):
        self.sdl_joystick = sdl_joystick
        self.buttons = [0] * SDL_JoystickNumButtons(sdl_joystick)
        self.axis = [0.0] * SDL_JoystickNumAxes(sdl_joystick)
        self.daxis = [0] * (SDL_JoystickNumAxes(sdl_joystick) * 2)
        
    
    def dispose(self):
        SDL_JoystickClose(self.sdl_joystick)
    
    
    def update(self):
        joystick = self.sdl_joystick
        
        for button in range(SDL_JoystickNumButtons(joystick)):
            state = SDL_JoystickGetButton(joystick, button)
            if state:
                self.buttons[button] += 1
            else:
                self.buttons[button]  = 0
        
        
        for axis in range(SDL_JoystickNumAxes(joystick)):
            value = SDL_JoystickGetAxis(joystick, axis)
            if value > 0:
                value /= 32767.0
            else:   
                value /= 32768.0
            
            if axis == 1: 
                value = -value
                if value == 0: value = 0.0
            
            if value < -0.333:
                self.daxis[axis * 2 + 0] += 1
            else:
                self.daxis[axis * 2 + 0]  = 0
                
            if value >  0.333:
                self.daxis[axis * 2 + 1] += 1
            else:
                self.daxis[axis * 2 + 1]  = 0
            
            self.axis[axis] = value
                

class InputHandler:
    def __init__(self, api):
        self.api = api
    
        self.keys = {}
        self.joysticks = {}
        
        self.mouse = (0, 0)
        self.mouse_prev = None
        self.mouse_rel  = (0, 0)
        self.mouse_buttons = {'left': 0, 'middle': 0, 'right': 0}
        
        SDL_JoystickUpdate()
        
        self.default_joystick = None
        for i in range(SDL_NumJoysticks()):
            sdl_joystick = SDL_JoystickOpen(i)
            if sdl_joystick:
                base_name = '_'.join(re.sub(r'[^0-9a-z]', '', SDL_JoystickName(sdl_joystick).decode().lower()).split())
                candidate = base_name
                index = 2
                while candidate in self.joysticks:
                    candidate = '%s%d' % (base_name, index)
                    index += 1
                name = candidate
                
                joystick = Joystick(sdl_joystick)
                self.joysticks[name] = joystick
                if self.default_joystick is None:
                    self.default_joystick = joystick
        
    
    def get_joystick(self, joystick_name):
        if joystick_name is not None:
            try:
                return self.joysticks[str(joystick_name).lower().strip()]
            except KeyError:
                raise KeyError('no joystick named %r' % joystick_name)
        elif self.default_joystick:
            return self.default_joystick
        else:
            return None
    
    
    def axis_count(self, joystick_name):
        joystick = self.get_joystick(joystick_name)
        
        if not joystick:
            return 0
        
        return len(joystick.axis)
    
    
    def get_axis(self, index, joystick_name=None):
        joystick = self.get_joystick(joystick_name)
        
        if not joystick:
            return 0.0
        
        if index >= 0 and index < len(joystick.axis):
            return joystick.axis[index]
        
        return 0
    
    
    def get_daxis(self, index, dir, joystick_name=None):
        joystick = self.get_joystick(joystick_name)
        
        if not joystick:
            return 0
        
        if index >= 0 and index < len(joystick.axis):
            return joystick.daxis[index * 2 + dir]
        
        return 0
    
    
    def button_count(self, joystick_name):
        joystick = self.get_joystick(joystick_name)
        
        if not joystick:
            return 0
            
        return len(joystick.buttons)
    
    
    def get_button(self, index, joystick_name=None):
        joystick = self.get_joystick(joystick_name)
        
        if not joystick:
            return 0
        
        if index >= 0 and index < len(joystick.buttons):
            return joystick.buttons[index]
        
        return 0
    
    
    def key(self, key_name):
        return self.keys.get(str(key_name).strip().lower(), 0)
    
    
    def dispose(self):
        for joystick in self.joysticks.values():
            joystick.dispose()
        
        self.joysticks = {}
    
    
    @staticmethod
    def key_name(id):
        name = SDL_GetKeyName(id).decode().lower()
        
        name = re.sub(r'\s|\\|\.|,|/|\#|\'|;|\[|\]|`|\-|\=|\+|\*', 
            lambda match: {
                ' ':  '_',             '\\': 'backslash',
                '.':  'period',        ',':  'comma',
                '/':  'slash',         '#':  'hash',
                "'":  'quote',         ';':  'semicolon',
                '[':  'open_bracket',  ']':  'close_bracket',
                '=':  'equals',        '-':  'minus',
                '+':  'plus',          '*':  'asterisk',
                '`':  'backtick',
            }[match.group(0)], name)
        
        return name
    
        
    def update(self):
        for key in self.keys:
            self.keys[key] += 1
            
        for joystick in self.joysticks.values():
            joystick.update()
        
        x = c_int()
        y = c_int()
        button_bits = SDL_GetMouseState(byref(x), byref(y))
        x = x.value
        y = y.value
        
        if button_bits & 0x1:
            self.mouse_buttons['left'] += 1
        else:
            self.mouse_buttons['left'] = 0
        
        if button_bits & 0x2:
            self.mouse_buttons['middle'] += 1
        else:
            self.mouse_buttons['middle'] = 0
        
        if button_bits & 0x4:
            self.mouse_buttons['right'] += 1
        else:
            self.mouse_buttons['right'] = 0
        
        w = c_int()
        h = c_int()
        SDL_GetWindowSize(self.api.window, byref(w), byref(h))
        w = w.value
        h = h.value
        
        scale    = min(w / self.api.width, h / self.api.height)
        width    = int(self.api.width * scale)
        height   = int(self.api.height * scale)
        corner_x = (w - width) // 2
        corner_y = (h - height) // 2
        
        x = int((x - corner_x) / scale) 
        y = int((y - corner_y) / scale) 
        
        x -= self.api.width // 2
        y  = self.api.height // 2 - y
        
        self.mouse = (x, y)
        
        if self.mouse_prev is None:
            self.mouse_prev = self.mouse
        
        px, py = self.mouse_prev
        self.mouse_rel = (x - px, y - py)
        
        self.mouse_prev = self.mouse
        
        
    def process(self, event):
        if event.type == SDL_KEYDOWN:
            if not event.key.repeat:
                self.keys[self.key_name(event.key.keysym.sym)] = 1
        elif event.type == SDL_KEYUP:
            del self.keys[self.key_name(event.key.keysym.sym)]
