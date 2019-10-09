import os
import numpy as np
from PIL import Image

def main(inputs, structure, constants):
    class Charcoal(structure.Basic):
        category = 'Imagemagick'
        Tname = 'charcoal'
        argnames = {'radius':None, 'child':None}
        argtype = {'radius':inputs.Integer, 'child':'c'}
        def get(self, time, b):
            a = self.args['child'].get(time, b)
            name = constants.get_temp_path()+'.png'
            Image.fromarray(a).save(name)
            os.system('convert %s -charcoal %d %s'%(name,self.args['radius'].num,name))
            return np.asarray(Image.open(name).convert('RGB'))
    class Implode(structure.Basic):
        category = 'Imagemagick'
        Tname = 'implode'
        argnames = {'radius':None, 'child':None}
        argtype = {'radius':inputs.Integer, 'child':'c'}
        def get(self, time, b):
            a = self.args['child'].get(time, b)
            name = constants.get_temp_path()+'.png'
            Image.fromarray(a).save(name)
            os.system('convert %s -implode %d %s'%(name,self.args['radius'].num,name))
            return np.asarray(Image.open(name).convert('RGB'))
    class Rotate(structure.Basic):
        category = 'Imagemagick'
        Tname = 'rotate'
        argnames = {'degrees':None, 'child':None}
        argtype = {'degrees':inputs.Integer, 'child':'c'}
        def get(self, time, b):
            a = self.args['child'].get(time, b)
            name = constants.get_temp_path()+'.png'
            Image.fromarray(a).save(name)
            os.system('convert %s -rotate %d %s'%(name,self.args['degrees'].num,name))
            return np.asarray(Image.open(name).convert('RGB'))
    class Swirl(structure.Basic):
        category = 'Imagemagick'
        Tname = 'swirl'
        argnames = {'degrees':None, 'child':None}
        argtype = {'degrees':inputs.Integer, 'child':'c'}
        def get(self, time, b):
            a = self.args['child'].get(time, b)
            name = constants.get_temp_path()+'.png'
            Image.fromarray(a).save(name)
            os.system('convert %s -swirl %d %s'%(name,self.args['degrees'].num,name))
            return np.asarray(Image.open(name).convert('RGB'))
    class Posterize(structure.Basic):
        category = 'Imagemagick'
        Tname = 'posterize'
        argnames = {'levels':None, 'child':None}
        argtype = {'levels':inputs.Integer, 'child':'c'}
        def get(self, time, b):
            a = self.args['child'].get(time, b)
            name = constants.get_temp_path()+'.png'
            Image.fromarray(a).save(name)
            os.system('convert %s -posterize %d %s'%(name,self.args['levels'].num,name))
            return np.asarray(Image.open(name).convert('RGB'))
    return {'structure_avaliable':[Charcoal, Implode, Rotate, Swirl, Posterize]}
