#!/usr/env/python3
from PIL import Image
import numpy as np

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


class BrightnessCorrection(Effect):
    """basic brightness curves modifier"""
    def modify_image(self, path, frame):
        I = np.asarray(Image.open(path))
        I1 = I/265
        I2 = I1**(1/self.data['brighten'])
        Io = I2 * 256
        im = Image.fromarray(np.uint8(Io))
        im.save(path)
    vals = ['brighten']


supported_effects = {'hsv curves':HSVcorrection, 'RGB curves':RGBcorrection, 'brighten':BrightnessCorrection}

applied_effects = []

names = []
for n in supported_effects:
    names.append(n)
def apply(n):
    global applied_effects
    applied_effects.append(supported_effects[n]())

