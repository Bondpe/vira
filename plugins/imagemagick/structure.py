import input, datamanagement, constants
import ffmpeg, copy, os, scipy
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def matchImageSize(a, b):
    s1 = a.shape
    s2 = b.shape
    s3 = []
    s3.append(max([s1[0], s2[0]]))
    s3.append(max([s1[1], s2[1]]))
    ia = Image.fromarray(np.uint8(a))
    ib = Image.fromarray(np.uint8(b))
    sa = ia.resize(s3)
    sb = ib.resize(s3)
    a = np.asarray(sa)
    b = np.asarray(sb)
    return (a,b)

class Basic:
    Tname = 'basic wrapper'
    argnames = {'child':None}
    argtype = {'child':'c'}
    category = 'Basic'
    argorder = None
    saveDefault = True
    def __init__(self, name=None):
        if name is None:
            name = self.Tname
        self.name = name
        self.args = copy.copy(self.argnames)
        if self.argorder is None:
            self.argkeys = sorted(list(self.args.keys()))
        else:
            self.argkeys = self.argorder
    def get(self, time, input):
        return self.args['child'].get(time, input)
    def sound(self, time, inval):
        return inval
    def setup(self):
        """this function is launched just after input data is completed"""
        pass
    def getStartEnd(self):
        """change this to return None or (StartTime, EndTime), for non-endless streams"""
        if 'child' in self.args:
            return self.args['child'].getStartEnd()
        return None
    def get_name(self):
        if 'child' in self.argtype and self.argtype['child'] == 'c':
            return self.args['child'].get_name()
        else:
            return self.name
    def is_box(self):
        return 'child' in self.argtype and self.argtype['child'] == 'c'
    def save(self, packer):
        return None
    def load(self, loader):
        return None

