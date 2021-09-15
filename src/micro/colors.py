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

from colorsys import hls_to_rgb
import re


def rgba(r, g, b, a=1.0):
    if r < 0 and r > 255:
        raise ValueError('red component of rgb/rgba color must be between 0 - 255')
    if g < 0 and g > 255:
        raise ValueError('green component of rgb/rgba color must be between 0 - 255')
    if b < 0 and b > 255:
        raise ValueError('blue component of rgb/rgba color must be between 0 - 255')
    if a < 0 and a > 1:
        raise ValueError('alpha component of rgb/rgba color must be between 0.0 - 1.0')
    
    return r, g, b, int(a * 255)

#potentially add mirror function to allow for hsv
def hsla(h, s, l, a=1.0):
    if h < 0 and h > 360:
        raise ValueError('hue component of hsl/hsla color must be between 0 - 360')
    if s < 0 and s > 100:
        raise ValueError('saturation component of hsl/hsla color must be between 0% - 100%')
    if l < 0 and l > 100:
        raise ValueError('lightness component of hsl/hsla color must be between 0% - 100%')
    if a < 0 and a > 1:
        raise ValueError('alpha component of hsl/hsla color must be between 0.0 - 1.0')
    
    h /= 360.0
    s /= 100.0
    l /= 100.0
    
    r, g, b = hls_to_rgb(h, l, s)
    
    return int(r * 255), int(g * 255), int(b * 255), int(a * 255)


#potentially add capability to add own named colours.
#potnetially change spelling from color to colour, maybe find a way to use both
def color_from_name(name):      
    if isinstance(name, str):
        key = name.lower().strip()

        try:
            if key == '':
                return 0, 0, 0, 0
            elif key[0] == '#' and len(key) == 4:
                return (int(name[1] * 2, 16),
                        int(name[2] * 2, 16),
                        int(name[3] * 2, 16),
                        255)
            elif key[0] == '#' and len(key) == 5:
                return (int(name[1] * 2, 16),
                        int(name[2] * 2, 16),
                        int(name[3] * 2, 16),
                        int(name[4] * 2, 16))
            elif key[0] == '#' and len(key) == 7:
                return (int(name[1:3], 16),
                        int(name[3:5], 16),
                        int(name[3:7], 16),
                        255)
            elif key[0] == '#' and len(key) == 9:
                return (int(name[1:3], 16),
                        int(name[3:5], 16),
                        int(name[5:7], 16),
                        int(name[7:9], 16))
            else:
                match = re.match(r'''rgb\(
                    \s*(\d+)\s*,
                    \s*(\d+)\s*,
                    \s*(\d+)\s*\)''', name, re.X)
                if match:
                    return rgba(int(match.group(1)), 
                                int(match.group(2)), 
                                int(match.group(3)))
                match = re.match(r'''rgba\(
                    \s*(\d+)\s*,
                    \s*(\d+)\s*,
                    \s*(\d+)\s*,
                    \s*(\d+\.\d+|\d+\.|\.\d+|\d+)\s*\)''', name, re.X)
                if match:
                    return rgba(int(match.group(1)), 
                                int(match.group(2)), 
                                int(match.group(3)), 
                                float(match.group(4)))
                match = re.match(r'''hsl\(
                    \s*(\d+\.\d+|\d+\.|\.\d+|\d+)\s*,
                    \s*(\d+\.\d+%|\d+\.%|\.\d+%|\d+%|0)\s*,
                    \s*(\d+\.\d+%|\d+\.%|\.\d+%|\d+%|0)\s*\)''', name, re.X)
                if match:
                    return hsla(float(match.group(1)), 
                                float(match.group(2).rstrip('%')), 
                                float(match.group(3).rstrip('%')))
                match = re.match(r'''hsla\(\s*
                    (\d+\.\d+|\d+\.|\.\d+|\d+)
                    \s*,\s*
                    (\d+\.\d+%|\d+\.%|\.\d+%|\d+%|0)
                    \s*,\s*
                    (\d+\.\d+%|\d+\.%|\.\d+%|\d+%|0)
                    \s*,\s*
                    (\d+\.\d+|\d+\.|\.\d+|\d+)
                    \s*\)''', name, re.X)
                if match:
                    return hsla(float(match.group(1)), 
                                float(match.group(2).rstrip('%')), 
                                float(match.group(3).rstrip('%')), 
                                float(match.group(4)))
                
                if not match:
                    return {'aliceblue':            (240, 248, 255), 'antiquewhite':         (250, 235, 215),
                            'aqua':                 (  0, 255, 255), 'aquamarine':           (127, 255, 212),
                            'azure':                (240, 255, 255), 'beige':                (245, 245, 220),
                            'bisque':               (255, 228, 196), 'black':                (  0,   0,   0),
                            'blanchedalmond':       (255, 235, 205), 'blue':                 (  0,   0, 255),
                            'blueviolet':           (138,  43, 226), 'brown':                (165,  42,  42),
                            'burlywood':            (222, 184, 135), 'cadetblue':            ( 95, 158, 160),
                            'chartreuse':           (127, 255,   0), 'chocolate':            (210, 105,  30),
                            'coral':                (255, 127,  80), 'cornflowerblue':       (100, 149, 237),
                            'cornsilk':             (255, 248, 220), 'crimson':              (220,  20,  60),
                            'cyan':                 (  0, 255, 255), 'darkblue':             (  0,   0, 139),
                            'darkcyan':             (  0, 139, 139), 'darkgoldenrod':        (184, 134,  11),
                            'darkgray':             (169, 169, 169), 'darkgreen':            (  0, 100,   0),
                            'darkkhaki':            (189, 183, 107), 'darkmagenta':          (139,   0, 139),
                            'darkolivegreen':       ( 85, 107,  47), 'darkorange':           (255, 140,   0),
                            'darkorchid':           (153,  50, 204), 'darkred':              (139,   0,   0),
                            'darksalmon':           (233, 150, 122), 'darkseagreen':         (143, 188, 143),
                            'darkslateblue':        ( 72,  61, 139), 'darkslategray':        ( 47,  79,  79),
                            'darkturquoise':        (  0, 206, 209), 'darkviolet':           (148,   0, 211),
                            'deeppink':             (255,  20, 147), 'deepskyblue':          (  0, 191, 255),
                            'dimgray':              (105, 105, 105), 'dodgerblue':           ( 30, 144, 255),
                            'firebrick':            (178,  34,  34), 'floralwhite':          (255, 250, 240),
                            'forestgreen':          ( 34, 139,  34), 'fuchsia':              (255,   0, 255),
                            'gainsboro':            (220, 220, 220), 'ghostwhite':           (248, 248, 255),
                            'gold':                 (255, 215,   0), 'goldenrod':            (218, 165,  32),
                            'gray':                 (128, 128, 128), 'green':                (  0, 128,   0),
                            'greenyellow':          (173, 255,  47), 'honeydew':             (240, 255, 240),
                            'hotpink':              (255, 105, 180), 'indianred':            (205,  92,  92),
                            'indigo':               ( 75,   0, 130), 'ivory':                (255, 255, 240),
                            'khaki':                (240, 230, 140), 'lavender':             (230, 230, 250),
                            'lavenderblush':        (255, 240, 245), 'lawngreen':            (124, 252,   0),
                            'lemonchiffon':         (255, 250, 205), 'lightblue':            (173, 216, 230),
                            'lightcoral':           (240, 128, 128), 'lightcyan':            (224, 255, 255),
                            'lightgoldenrodyellow': (250, 250, 210), 'lightgray':            (211, 211, 211),
                            'lightgreen':           (144, 238, 144), 'lightpink':            (255, 182, 193),
                            'lightsalmon':          (255, 160, 122), 'lightseagreen':        ( 32, 178, 170),
                            'lightskyblue':         (135, 206, 250), 'lightslategray':       (119, 136, 153),
                            'lightsteelblue':       (176, 196, 222), 'lightyellow':          (255, 255, 224),
                            'lime':                 (  0, 255,   0), 'limegreen':            ( 50, 205,  50),
                            'linen':                (250, 240, 230), 'magenta':              (255,   0, 255),
                            'maroon':               (128,   0,   0), 'mediumaquamarine':     (102, 205, 170),
                            'mediumblue':           (  0,   0, 205), 'mediumorchid':         (186,  85, 211),
                            'mediumpurple':         (147, 112, 219), 'mediumseagreen':       ( 60, 179, 113),
                            'mediumslateblue':      (123, 104, 238), 'mediumspringgreen':    (  0, 250, 154),
                            'mediumturquoise':      ( 72, 209, 204), 'mediumvioletred':      (199,  21, 133),
                            'midnightblue':         ( 25,  25, 112), 'mintcream':            (245, 255, 250),
                            'mistyrose':            (255, 228, 225), 'moccasin':             (255, 228, 181),
                            'navajowhite':          (255, 222, 173), 'navy':                 (  0,   0, 128),
                            'oldlace':              (253, 245, 230), 'olive':                (128, 128,   0),
                            'olivedrab':            (107, 142,  35), 'orange':               (255, 165,   0),
                            'orangered':            (255,  69,   0), 'orchid':               (218, 112, 214),
                            'palegoldenrod':        (238, 232, 170), 'palegreen':            (152, 251, 152),
                            'paleturquoise':        (175, 238, 238), 'palevioletred':        (219, 112, 147),
                            'papayawhip':           (255, 239, 213), 'peachpuff':            (255, 218, 185),
                            'peru':                 (205, 133,  63), 'pink':                 (255, 192, 203),
                            'plum':                 (221, 160, 221), 'powderblue':           (176, 224, 230),
                            'purple':               (128,   0, 128), 'red':                  (255,   0,   0),
                            'rosybrown':            (188, 143, 143), 'royalblue':            ( 65, 105, 225),
                            'saddlebrown':          (139,  69,  19), 'salmon':               (250, 128, 114),
                            'sandybrown':           (244, 164,  96), 'seagreen':             ( 46, 139,  87),
                            'seashell':             (255, 245, 238), 'sienna':               (160,  82,  45),
                            'silver':               (192, 192, 192), 'skyblue':              (135, 206, 235),
                            'slateblue':            (106,  90, 205), 'slategray':            (112, 128, 144),
                            'snow':                 (255, 250, 250), 'springgreen':          (  0, 255, 127),
                            'steelblue':            ( 70, 130, 180), 'tan':                  (210, 180, 140),
                            'teal':                 (  0, 128, 128), 'thistle':              (216, 191, 216),
                            'tomato':               (255,  99,  71), 'turquoise':            ( 64, 224, 208),
                            'violet':               (238, 130, 238), 'wheat':                (245, 222, 179),
                            'white':                (255, 255, 255), 'whitesmoke':           (245, 245, 245),
                            'yellow':               (255, 255,   0), 'yellowgreen':          (154, 205,  50)}[key] + (255,)
        except (KeyError, ValueError):
            raise ValueError('Invalid color %r' % name)
    else:
        raise TypeError('color values must be strings')
