#!/usr/env/python3
from PIL import Image
import numpy as np
import os

effects = []


class Effect:
    """basic effect, you may base yours on this"""
    def __init__(self, stream=1, start=0, duration=-1, **kwargs):
        self.stream = stream
        self.start = start
        self.duration = duration
        self.data = kwargs

    def modify_image(self, path, frame):
        pass

    def apply(self, path, stream=-1, frame=1):
        if stream == -1 or stream == self.stream:
            if frame > self.start:
                if self.duration == -1 or self.duration+self.start >= frame:
                    self.modify_image(path, frame)
    vals = []
    vt = []


class HSVcorrection(Effect):
    """basic HSV curves modifier"""
    def modify_image(self, path, frame):
        file = Image.open(path)
        hsv = file.convert('HSV')
        pixels = hsv.load()
        x_size, y_size = hsv.size
        for x in range(x_size):
            for y in range(y_size):
                h, s, v = pixels[x, y]
                h += self.data['hue']
                s = 256*(s/256)**(1/self.data['saturate'])
                v = 256*(v/256)**(1/self.data['brighten'])
                h = int(h)
                s = int(s)
                v = int(v)
                pixels[x, y] = (h, s, v)
        out = hsv.convert('RGB')
        out.save(path)
    vals = ['hue', 'saturate', 'brighten']
    vt = ['float', 'float', 'float']


class RGBcorrection(Effect):
    """basic RGB curves modifier"""
    def modify_image(self, path, frame):
        file = Image.open(path)
        rgb = file.convert('RGB')
        pixels = rgb.load()
        x_size, y_size = rgb.size
        for x in range(x_size):
            for y in range(y_size):
                r, g, b = pixels[x, y]
                r = 256*(r/256)**(1/self.data['r'])
                g = 256*(g/256)**(1/self.data['g'])
                b = 256*(b/256)**(1/self.data['b'])
                r = int(r)
                g = int(g)
                b = int(b)
                pixels[x, y] = (r, g, b)
        rgb.save(path)
    vals = ['r', 'g', 'b']
    vt = ['float', 'float', 'float']


class BrightnessCorrection(Effect):
    """basic brightness curves modifier"""
    def modify_image(self, path, frame):
        I = np.asarray(Image.open(path).convert('RGB'))
        I1 = I/265
        I2 = I1**(1/self.data['brighten'])
        Io = I2 * 256
        im = Image.fromarray(np.uint8(Io))
        im.save(path)
    vals = ['brighten']
    vt = ['float']


supported_effects = {'hsv curves':HSVcorrection, 'RGB curves':RGBcorrection, 'brighten':BrightnessCorrection}


def add_imagemagick(name, arg):
    simpledName=name[0].upper()+name[1:].lower().replace('-', '_')
    exec('''
global %s
class %s(Effect):
    """imagemagick %s modifier"""
    def modify_image(self, path, frame):
        os.system('convert %%s -%s %%s %%s'%%(path, self.data['%s'], path))
    vals = ['%s']
    vt = ['str']
supported_effects['%s'] = %s
'''%(simpledName, simpledName, simpledName, name, arg, arg, name, simpledName))

def add_imagemagick_keyframed(name, arg):
    simpledName=name[0].upper()+name[1:].lower().replace('-', '_')
    exec('''
global %s_keyframed
class %s_keyframed(Effect):
    """imagemagick keyframed %s modifier"""
    def modify_image(self, path, frame):
        deg = self.data['%s']
        frame_distance = abs(self.data['frame of max value']-frame)
        if frame_distance < self.data['slowness']:
            amplifier = deg/self.data['slowness']*(self.data['slowness']-frame_distance)
            os.system('convert %%s -%s %%f %%s'%%(path, amplifier, path))
    vals = ['%s', 'frame of max value', 'slowness']
    vt = ['float', 'float', 'float']
supported_effects['%s (keyframed)'] = %s_keyframed
'''%(simpledName, simpledName, simpledName, arg, name, arg, name, simpledName))


imagemagick_effects = ['charcoal radius', 'implode radius', 'rotate degrees', 'blue-shift factor', 'blur geometry', 'hough-lines geometry', 'gaussian-blur geometry', 'gamma value', 'extract geometry', 'extend geometry', 'emboss radius', 'edge radius', 'deskew threshold', 'cycle amount', 'contrast-stretch geometry', 'canny geometry', 'black-threshold value', 'brightness-contrast geometry', 'mean-shift geometry', 'median geometry', 'mode geometry', 'modulate value', 'motion-blur geometry', 'noise geometry', 'paint radius', 'perceptible epsilon', 'polaroid angle', 'posterize levels', 'radial-blur angle', 'raise value', 'segment values', 'sepia-tone threshold', 'shade degrees', 'shadow geometry', 'sharpen geometry', 'shave geometry', 'shear geometry', 'sketch geometry', 'solarize threshold', 'spread amount', 'swirl degrees', 'draw string', 'crop siseXxsizeY']
imagemagick_keyframing = ['charcoal radius', 'implode radius', 'rotate degrees', 'blue-shift factor', 'gamma value', 'emboss radius', 'edge radius', 'black-threshold value', 'modulate value', 'paint radius', 'perceptible epsilon', 'polaroid angle', 'radial-blur angle', 'raise value', 'segment values', 'sepia-tone threshold', 'shade degrees', 'solarize threshold', 'swirl degrees']

for names in imagemagick_effects:
    name, arg = names.split(' ')
    add_imagemagick(name, arg)
for names in imagemagick_keyframing:
    name, arg = names.split(' ')
    add_imagemagick_keyframed(name, arg)

applied_effects = []

names = []
for n in supported_effects:
    names.append(n)
names.sort()
def apply(n):
    global applied_effects
    applied_effects.append(supported_effects[n]())
