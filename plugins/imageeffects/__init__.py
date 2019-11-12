import numpy as np
from PIL import Image
import structure
import input as inputs

class Posterize(structure.Basic):
    category = 'Image effects'
    Tname = 'limit palette'
    argnames = {'levels':None, 'child':None}
    argtype = {'levels':inputs.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        image = Image.fromarray(a)
        result = image.convert('P', palette=Image.ADAPTIVE, colors=self.args['levels'].num).convert('RGB')
        a = np.asarray(result)
        return a
data = {'structure_avaliable':[Posterize]}
