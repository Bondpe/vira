import os
import structure
import input as inputs
import numpy as np
from PIL import Image

class RP:
    def __init__(self):
        self.tmp='/tmp/vira/imagemagick'
        os.mkdir(self.tmp)
        self.id = 0
    def __call__(self):
        self.id+=1
        return self.tmp+'/'+str(self.id)
rp = RP()

class Charcoal(structure.Basic):
    category = 'Imagemagick'
    Tname = 'charcoal'
    argnames = {'radius':None, 'child':None}
    argtype = {'radius':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        name = rp()+'.png'
        out = rp()+'_.png'
        Image.fromarray(a).save(name)
        os.system('convert %s -charcoal %d %s'%(name,self.args['radius'].num,out))
        return np.asarray(Image.open(out).convert('RGB'))
class Implode(structure.Basic):
    category = 'Imagemagick'
    Tname = 'implode'
    argnames = {'radius':None, 'child':None}
    argtype = {'radius':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        name = rp()+'.png'
        out = rp()+'_.png'
        Image.fromarray(a).save(name)
        os.system('convert %s -implode %d %s'%(name,self.args['radius'].num,out))
        return np.asarray(Image.open(out).convert('RGB'))
class Rotate(structure.Basic):
    category = 'Imagemagick'
    Tname = 'rotate'
    argnames = {'degrees':None, 'child':None}
    argtype = {'degrees':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        name = rp()+'.png'
        out = rp()+'_.png'
        Image.fromarray(a).save(name)
        os.system('convert %s -rotate %d %s'%(name,self.args['degrees'].num,out))
        return np.asarray(Image.open(out).convert('RGB'))
class Swirl(structure.Basic):
    category = 'Imagemagick'
    Tname = 'swirl'
    argnames = {'degrees':None, 'child':None}
    argtype = {'degrees':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        name = rp()+'.png'
        out = rp()+'_.png'
        Image.fromarray(a).save(name)
        os.system('convert %s -swirl %d %s'%(name,self.args['degrees'].num,out))
        return np.asarray(Image.open(out).convert('RGB'))
class Posterize(structure.Basic):
    category = 'Imagemagick'
    Tname = 'posterize'
    argnames = {'levels':None, 'child':None}
    argtype = {'levels':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        name = rp()+'.png'
        out = rp()+'_.png'
        Image.fromarray(a).save(name)
        os.system('convert %s -posterize %d %s'%(name,self.args['levels'].num,out))
        return np.asarray(Image.open(out).convert('RGB'))
data = {'structure_avaliable':[Charcoal, Implode, Rotate, Swirl, Posterize]}
