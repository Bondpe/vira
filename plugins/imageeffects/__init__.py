import numpy as np
from PIL import Image,ImageFilter
import structure
import input as inputs

class Posterize(structure.Basic):
    category = 'Image effects'
    Tname = 'limit palette'
    argnames = {'levels':None, 'child':None}
    argtype = {'levels':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return None
        image = Image.fromarray(a)
        result = image.convert('P', palette=Image.ADAPTIVE, colors=self.args['levels'].num).convert('RGB')
        a = np.asarray(result)
        return a
class SetResolution(structure.Basic):
    category = 'Image effects'
    Tname = 'set resolution'
    argnames = {'resolution':None, 'child':None}
    argtype = {'resolution':inputs.Resolution, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return None
        image = Image.fromarray(a)
        ia = Image.fromarray(np.uint8(a))
        sa = ia.resize(self.args['resolution'].r)
        a = np.asarray(sa)
        return a
class GaussianBlur(structure.Basic):
    category = 'Image effects'
    Tname = 'guassian blur'
    argnames = {'radius':None, 'child':None}
    argtype = {'radius':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return None
        image=Image.fromarray(a).filter(ImageFilter.GaussianBlur(radius=self.args['radius'].num))
        a = np.asarray(image)
        return a
class Glow(structure.Basic):
    category = 'Image effects'
    Tname = 'glow'
    argnames = {'radius':None, 'child':None}
    argtype = {'radius':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return None
        image=Image.fromarray(np.uint8(a)).filter(ImageFilter.GaussianBlur(radius=self.args['radius'].num))
        b=np.array(image)
        a = np.maximum(b,a)
        return a
data = {'structure_avaliable':[Posterize,SetResolution,GaussianBlur,Glow]}
