from scipy.interpolate import interp1d
import numpy as np
from tkinter import *
import structure
import input as inputs

def disp(cvs,fun,sx=0,sy=0):
    x = np.linspace(0,255,256)
    y = fun(x/256)*256
    cvs.create_rectangle(0+sx,256+sy,256+sx,0+sy,fill='white')
    for p in range(255):
        cvs.create_line(p+sx,256-y[p-1]+sy,p+1+sx,256-y[p]+sy)

class Curve_256x256:
    def __init__(self,fun,points,interp,name):
        self.fun=fun
        self.points=points
        self.interp=interp
        self.name = name
    def val(self,val):
        return self.fun(val/256)*256
    def __str__(self):
        return 'Curve(%s,%s)'%(repr(self.name),repr(self.interp))
    def get(*args, **kwargs):
        tk = Tk()
        tk.title(kwargs.get('name','curve'))
        kinds = ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']

        cvs = Canvas(tk,width=256,height=256)
        cvs.grid(row=1,column=1)
        if 'old' in kwargs:
            points=kwargs['old'].points
        else:
            points = [[0,0],[255,255]]
        fun = []

        chosen = StringVar(tk)
        chosen.set('linear')
        if 'old' in kwargs:
            chosen.set(kwargs['old'].interp)
        popupmenu = OptionMenu(tk,chosen,*kinds)
        Label(tk,text='Interpolation type:').grid(row=1,column=2)
        popupmenu.grid(row=2,column=2)
        def change_type(*args):
            x,y=[],[]
            for point in points:
                x.append(point[0])
                y.append(point[1])
            fun.append(interp1d(np.array(x)/256,np.array(y)/256,kind=chosen.get()))
        change_type()
        chosen.trace('w',change_type)

        def remove_points():
            nonlocal points
            points = [[0,0],[255,255]]
            change_type()
        def end():
            tk.destroy()
        Button(tk,text='clear',command=remove_points).grid(row=3,column=1)
        Button(tk,text='finish',command=end).grid(row=3,column=2)
            

        def cl(evt):
            points.append([evt.x,256-evt.y])
            x = []
            y = []
            for point in points:
                x.append(point[0])
                y.append(point[1])
            fun.append(interp1d(np.array(x)/256,np.array(y)/256,kind=chosen.get()))
        cvs.bind('<Button-1>',cl)
        try:
            while True:
                cvs.delete('all')
                disp(cvs,fun[-1])
                for x,y in points:
                    cvs.create_oval(x-3,253-y,x+3,259-y,fill='green')
                cvs.update()
        except:
            return Curve_256x256(fun[-1],points,chosen.get(),kwargs.get('name','curve'))
    def dialog(self,data):
        if data['action'] == 'get dialog height':
            return 256
        if data['action'] == 'display':
            cvs = data['canvas']
            x,y = data['pos']
            x-=256
            disp(cvs,self.fun,x,y)
            for xp,yp in self.points:
                px,py=xp+x,y-yp
                cvs.create_oval(px-3,253+py,px+3,259+py)
            cvs.create_rectangle(200,y,500-256,y+50,fill='white')
            cvs.create_text(210,y+25,text='clear',anchor='w')
            cvs.create_rectangle(200,y+100,500-256,y+50,fill='white')
            cvs.create_text(210,y+75,text='kind',anchor='w')
            cvs.create_text(210,y+90,text=self.interp,font=('Ariel',5))
        if data['action']=='click':
            if data['x'] > 256:
                if data['x'] < 300:
                    if data['y']<50:
                        self.points = [[0,0],[255,255]]
                    elif data['y']<100:
                        kinds = ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']
                        interp = kinds[kinds.index(self.interp)-1]
                        try:
                            x = []
                            y = []
                            for point in self.points:
                                x.append(point[0])
                                y.append(point[1])
                            self.fun=interp1d(np.array(x)/256,np.array(y)/256,kind=interp)
                            self.interp = interp
                            return
                        except:
                            pass
            else:
                self.points.append([256-data['x'],256-data['y']])
            x = []
            y = []
            for point in self.points:
                x.append(point[0])
                y.append(point[1])
            self.fun = interp1d(np.array(x)/256,np.array(y)/256,kind=self.interp)

class ColorGrade(structure.Basic):
    category='color manipulation'
    Tname='RGB ColorGrade'
    argnames = {'r':None,'g':None,'b':None,'child':None}
    argtype={'r':Curve_256x256,'g':Curve_256x256,'b':Curve_256x256,'child':'c'}
    def get(self, time, bg):
        a = self.args['child'].get(time, bg)
        r = a[:,:,0]
        g = a[:,:,1]
        b = a[:,:,2]

        r = self.args['r'].val(r)
        g = self.args['g'].val(g)
        b = self.args['b'].val(b)

        r = r.reshape(r.shape+(1,))
        g = g.reshape(g.shape+(1,))
        b = b.reshape(b.shape+(1,))

        return np.concatenate((r,g,b),2)
class Stretch(structure.Basic):
    category = 'color manipulation'
    Tname = 'stretch color space'
    argnames = {'child':None,'strength':None}
    argtype = {'child':'c','strength':inputs.Percent}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        return (a-np.amin(a))/np.amax(a-np.amin(a))*255*self.args['strength'].part+a*(1-self.args['strength'].part)
data = {'structure_avaliable':[ColorGrade,Stretch]}
