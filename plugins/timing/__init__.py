import structure
import input as inputs
import numpy as np

class Cycle(structure.Basic):
    category = 'Time.modifiers'
    Tname = 'cycle'
    argnames = {'time':None, 'child':None}
    argtype = {'time':inputs.TimeSegment, 'child':'c'}
    def get(self, time, b):
        s,e = self.args['time'].time
        while time < s:
            time+=e-s
        time-=s
        time%=e-s
        time+=s
        return self.args['child'].get(time, b)
class LinearSpeed(structure.Basic):
    category = 'Time.modifiers'
    Tname = 'linear change speed'
    argnames = {'multiplier':None, 'child':None}
    argtype = {'multiplier':inputs.Float, 'child':'c'}
    def get(self, time, b):
        mult = self.args['multiplier'].float
        return self.args['child'].get(time*mult, b)
    def getStartEnd(self):
        s,e = self.args['child'].getStartEnd()
        s/=self.args['multiplier'].float
        e/=self.args['multiplier'].float
        return (s, e)
    def sound(self, time, b):
        mult = self.args['multiplier'].float
        return self.args['child'].sound(time*mult, b)
data = {'structure_avaliable':[Cycle, LinearSpeed]}
