from tkinter import *
from tkinter import simpledialog, colorchooser
import numpy as np
import ffmpeg, random, scipy, scipy.interpolate
import constants
from PIL import Image, ImageTk


class MultiStream:
    def __init__(self, streams):
        self.streams = streams
    def get(*args, **kwargs):
        if kwargs.get('old',None) is not None:
            composition = kwargs.get('old').streams
            return ['composition', composition]
        comp = kwargs.get('composition', [])
        assert len(comp) > 0
        tk = Tk()
        tk.title('define streams to join')
        tk.resizable(False,False)
        chooser = Canvas(tk, width=1000,height=len(comp)*20)
        chooser.pack()
        streams = []
        def update():
            chooser.delete('all')
            for n in range(len(comp)):
                chooser.create_rectangle(0, n*20, 1000, n*20+20)
                chooser.create_text(20, n*20, anchor='nw', text=comp[n][0].name)
                if n in streams:
                    chooser.create_rectangle(5, n*20+5, 15, n*20+15)
            chooser.update()
        def click(evt):
            n = evt.y//20
            if n in streams:
                streams.remove(n)
            else:
                streams.append(n)
        chooser.bind('<Button-1>', click)
        while True:
            try:
                update()
            except BaseException as e:
                print(e)
                break
        sstreams = sorted(streams)
        out = []
        for sid in sstreams:
            out.append(comp[sid])
        sstreams.reverse()
        for sid in sstreams:
            del comp[sid]
        return MultiStream(out)
    def __str__(self):
        return 'Multi-stream sequence'

class Resolution:
    def __init__(self, *args):
        if len(args) == 0:
            x = 1920
            y = 1080
        elif len(args) == 1:
            x,y = args[0]
        elif len(args) == 2:
            x,y = args
        else:
            raise TypeError('unsupported arguments: '+str(args))
        self.r = (x,y)
        self.x = x
        self.y = y
    def get(*args, **kwargs):
        resol = Tk()
        resol.title('enter resolution')
        resol.resizable(False,False)
        Label(resol, text='width: ').pack()
        x = Entry(resol)
        x.pack()
        Label(resol, text='height: ').pack()
        y = Entry(resol)
        y.pack()
        ret = None
        def subm():
            nonlocal ret
            ret = Resolution(int(x.get()), int(y.get()))
            resol.destroy()
        Button(resol, command=subm, text='ok').pack()
        while True:
            try:
                resol.update()
            except:
                break
        assert ret is not None
        return ret
    def __str__(self):
        return 'Resolution'+str(self.r)

class Time:
    def __init__(self, time=0):
        self.time = time
    def get(*args, **kwargs):
        time = simpledialog.askfloat('enter time', 'keytime required')
        return Time(time)
    def __str__(self):
        return 'KeyTime(%f seconds)'%self.time
class Float:
    def __init__(self, i=0):
        self.float = i
    def get(*args, **kwargs):
        i = simpledialog.askfloat('enter %s'%kwargs.get('name', 'value'), 'enter %s'%kwargs.get('name', 'value'))
        return Float(i)
    def __str__(self):
        return str(self.float)
class AlphaPercent:
    def __init__(self, alpha=1):
        self.alpha = alpha
    def get(*args, **kwargs):
        alpha = simpledialog.askinteger('enter alpha', 'enter alpha percentage')
        return AlphaPercent(alpha/100)
    def __str__(self):
        return 'Alpha(%f)'%self.alpha
class Percent:
    def __init__(self, part=1):
        self.part = part
    def get(*args, **kwargs):
        part = simpledialog.askinteger('enter %s'%kwargs.get('name', 'value'), 'enter %s percentage'%kwargs.get('name', 'value'))
        return Percent(part/100)
    def __str__(self):
        return 'Part(%f)'%self.part
class Integer:
    def __init__(self, num=1):
        self.num = num
        self.pointer = 0
    def dialog(self,data):
        if data['action'] == 'get dialog height':
            return 25
        if data['action'] == 'display':
            a = list(str(self.num))
            a.insert(len(a)-self.pointer, '|')
            a = ''.join(a)
            cvs = data['canvas']
            x,y = data['pos']
            cvs.create_rectangle(x,y,x-50,y+25,fill='white')
            cvs.create_text(x-50,y+12,anchor='w',text=a,fill='blue')
            cvs.create_polygon(x-17,y+10,x-3,y+10,x-10,y+1, fill='black')
            cvs.create_polygon(x-17,y+15,x-3,y+15,x-10,y+24,fill='black')
        if data['action'] == 'click':
            if data['x'] < 20:
                if data['y']<=12:
                    self.num+=1
                else:
                    self.num-=1
            else:
                n = simpledialog.askinteger('reenter', 'reenter')
                if n is not None: self.num = n
        if data['action'] == 'key':
            try:
                a = list(str(self.num))
                a.insert(len(a)-self.pointer, str(int(data['key'][0])))
                self.num=int(''.join(a))
            except:
                if data['key'][2] == 113:
                    self.pointer+=1
                elif data['key'][2] == 114:
                    self.pointer-=1
                elif data['key'][2] == 22:
                    a = list(str(self.num))
                    del a[len(a)-self.pointer-1]
                    self.num=int(''.join(a))
    def get(*args, **kwargs):
        num = simpledialog.askinteger('enter %s'%kwargs.get('name', 'value'), 'enter %s'%kwargs.get('name', 'value'))
        return Integer(num)
    def __str__(self):
        return 'Integer(%d)'%self.num
class Bool:
    def __init__(self, bool=True):
        self.bool = bool
    def dialog(self,data):
        if data['action']=='click':
            self.bool=not self.bool
        elif data['action'] == 'display':
            cvs = data['canvas']
            x,y = data['pos']
            cvs.create_rectangle(x-10,y+10,x-15,y+15,fill='white')
            if self.bool:
                cvs.create_text(x-12,y+12,text='v',fill='green')
    def get(*args, **kwargs):
        return Bool()
    def __str__(self):
        return str(self.bool)
class MixModes:
    modes = {'alpha':(lambda a,b,h: a*h+b*(1-h)), 'add':(lambda a,b,h: a*h+b), 'substract':(lambda a,b,h:b-a*h), 'multiply':(lambda a,b,h: a**h*b**(1-h)), 'dissolve':(lambda a,b,h: random.choice([a]*int(h*100)+[b]*int((1-h)*100))), 'screen':(lambda a,b,h:1-((1-a)**h*(1-b)**(1-h))), 'overlay':(lambda a,b,h: ((a**h*b**(1-h))*(a<0.5)+(1-((1-a)**h*(1-b)**(1-h))))*(a>=0.5)), 'divide':(lambda a,b,h: (a**h)/(b**(1-h))), 'alpha_substract':(lambda a,b,h:a*h-b*(1-h)), 'difference':(lambda a,b,h:abs(a*h-b*(1-h)))}
    def __init__(self, mode='add'):
#        self.mode = self.modes[mode] # saving bug
        self.name = mode
    def get(*args, **kwargs):
        modes = {'alpha':(lambda a,b,h: a*h+b*(1-h)), 'add':(lambda a,b,h: a*h+b), 'substract':(lambda a,b,h:b-a*h), 'multiply':(lambda a,b,h: a**h*b**(1-h)), 'dissolve':(lambda a,b,h: random.choice([a]*int(h*100)+[b]*int((1-h)*100))), 'screen':(lambda a,b,h:1-((1-a)**h*(1-b)**(1-h))), 'overlay':(lambda a,b,h: ((a**h*b**(1-h))*(a<0.5)+(1-((1-a)**h*(1-b)**(1-h))))*(a>=0.5)), 'divide':(lambda a,b,h: (a**h)/(b**(1-h))), 'alpha_substract':(lambda a,b,h:a*h-b*(1-h)), 'difference':(lambda a,b,h:abs(a*h-b*(1-h)))}
        names = sorted(list(modes.keys()))
        tk = Tk()
        tk.title('mixing mode')
        tk.resizable(False,False)
        c = Canvas(tk, width=100, height=20*len(names))
        c.pack()
        name = None
        i = 0
        for n in names:
            c.create_rectangle(0, i*20, 100, i*20+20)
            c.create_text(50, i*20+10, text=n)
            i += 1
        def click(evt):
            nonlocal name
            name = names[evt.y//20]
        c.bind('<Button-1>', click)
        while name is None:
            c.update()
        tk.destroy()
        return MixModes(name)
    def run(self, a, b, h,t=0):
        random.seed(t)
        def apply(a,b,h):
            a = self.modes[self.name](a/256,b/256,h)
            if a > 1:
                a = 1
            if a < 0:
                a = 0
            return int(a*256)
        if self.name not in ['dissolve']:
            return self.modes[self.name](a/256,b/256,h)*256
        return np.vectorize(apply)(a,b,h)
    def __str__(self):
        return 'Mix%s()'%self.name.capitalize()
class LayerModes:
    modes = {'add':(lambda a,b: a+b), 'multiply':(lambda a,b: a*b), 'screen':(lambda a,b:1-((1-a)*(1-b))), 'overlay':(lambda a,b: ((a*b)*(a < 0.5)+(1-((1-a)*(1-b))))*(a <= 0.5)), 'divide':(lambda a,b: a/b), 'substract':(lambda a,b:a-b), 'difference':(lambda a,b:abs(a-b)), 'lighten only':(lambda a,b:np.maximum(a,b)), 'darken only':(lambda a,b:np.minimum(a,b))}
    def __init__(self, mode='add'):
#        self.mode = self.modes[mode] # saving bug
        self.name = mode
    def get(*args, **kwargs):
        modes = {'add':(lambda a,b: a+b), 'multiply':(lambda a,b: a*b), 'screen':(lambda a,b:1-((1-a)*(1-b))), 'overlay':(lambda a,b: ((a*b)*(a < 0.5)+(1-((1-a)*(1-b))))*(a <= 0.5)), 'divide':(lambda a,b: a/b), 'substract':(lambda a,b:a-b), 'difference':(lambda a,b:abs(a-b)), 'lighten only':(lambda a,b:np.maximum(a,b)), 'darken only':(lambda a,b:np.minimum(a,b))}
        names = sorted(list(modes.keys()))
        tk = Tk()
        tk.title('mixing mode')
        tk.resizable(False,False)
        c = Canvas(tk, width=100, height=20*len(names))
        c.pack()
        name = None
        i = 0
        for n in names:
            c.create_rectangle(0, i*20, 100, i*20+20)
            c.create_text(50, i*20+10, text=n)
            i += 1
        def click(evt):
            nonlocal name
            name = names[evt.y//20]
        c.bind('<Button-1>', click)
        while name is None:
            c.update()
        tk.destroy()
        return LayerModes(name)
    def run(self, a, b):
        return self.modes[self.name](a/256,b/256)*256
    def __str__(self):
        return 'Layer%s()'%self.name.capitalize()
class TimeSegment:
    def __init__(self, *args):
        if len(args) == 0:
            start = 0
            end = 1
        elif len(args) == 1:
            start,end = args[0]
        elif len(args) == 2:
            start,end = args
        else:
            raise TypeError('unsupported arguments: '+str(args))
        self.time = (start, end)
        self.start = start
        self.end = end
    def get(*args, **kwargs):
        time = Tk()
        time.title('enter time segment')
        time.resizable(False,False)
        Label(time, text='start: ').pack()
        x = Entry(time)
        x.pack()
        Label(time, text='end: ').pack()
        y = Entry(time)
        y.pack()
        ret = None
        def subm():
            nonlocal ret
            ret = TimeSegment(float(x.get()), float(y.get()))
            time.destroy()
        Button(time, command=subm, text='ok').pack()
        while True:
            try:
                time.update()
            except:
                break
        assert ret is not None
        return ret
    def __str__(self):
        return 'Time%s'%str(self.time)
class Color:
    def __init__(self, *args):
        if len(args) == 0:
            r,g,b = 0,0,0
        elif len(args) == 1:
            r,g,b = args[0]
        elif len(args) == 3:
            r,g,b = args
        else:
            raise TypeError('unsupported arguments: '+str(args))
        self.color = [r,g,b]
        self.r = r
        self.g = g
        self.b = b
    def display(self,cvs,x,y):
        r,g,b=self.color
        color = '#'+hex(r)[2:].zfill(2)+hex(g)[2:].zfill(2)+hex(b)[2:].zfill(2)
        cvs.create_rectangle(x,y,x-200,y+25,fill=color)
        cvs.create_text(x,y+12,anchor='e',text=color+'-'+str(self),fill='#'+hex(255-r)[2:].zfill(2)+hex(255-g)[2:].zfill(2)+hex(255-b)[2:].zfill(2))
    def get(*args, **kwargs):
        color = colorchooser.askcolor((0,0,0))[0]
        r,g,b = int(color[0]), int(color[1]), int(color[2])
        return Color(r,g,b)
    def __str__(self):
        return 'RGB(%d,%d,%d)'%(self.r,self.g,self.b)

class Point:
    def __init__(self, *args):
        if len(args) == 0:
            x = 1920
            y = 1080
        elif len(args) == 1:
            x,y = args[0]
        elif len(args) == 2:
            x,y = args
        else:
            raise TypeError('unsupported arguments: '+str(args))
        self.pos = (x,y)
        self.x = x
        self.y = y
    def get(*args, **kwargs):
        tk = Tk()
        tk.title('choose point')
        tk.resizable(False,False)
        canvas = Canvas(tk, width=1000, height=510)
        canvas.pack()
        time = 0
        composition = kwargs.get('composition', [])
        size = (0, 0)
        out = None
        def update():
            nonlocal canvas, composition, time, size, tk
            canvas.delete('all')
            canvas.create_line(0, 505, 1000, 505)
            canvas.create_line(time*25, 500, time*25, 510)
            d = None
            i = 0
            while len(composition) > i:
                d = composition[i][0].get(time-composition[i][1], d)
                i += 1
            if d is None:
                tk.update()
                return
            img = Image.fromarray(np.uint8(d))
            size = img.size
            img = img.resize((1000, 500), Image.ANTIALIAS)
            tk.image = ImageTk.PhotoImage(img, master=tk)
            canvas.create_image((0, 0), anchor='nw', image=tk.image)
            tk.update()
        def click(evt):
            nonlocal out, time
            if evt.y > 500:
                time = evt.x/25
            else:
                out = (evt.x, evt.y)
        canvas.bind('<Button-1>', click)
        while out is None:
            update()
        tk.destroy()
        w,h=size
        x,y=out
        return Point(int(x/1000*w), int(y/500*h))
    def __str__(self):
        return 'Point(%d,%d)'%(self.x,self.y)

class PointArray:
    def __init__(self, list):
        self.pos = list
    def get(*args, **kwargs):
        tk = Tk()
        tk.title('choose points')
        tk.resizable(False,False)
        canvas = Canvas(tk, width=1000, height=530)
        canvas.pack()
        time = 1
        composition = kwargs.get('composition', [])
        size = (0, 0)
        out = []
        display = []
        finished = False
        def update():
            nonlocal canvas, composition, time, size, tk, display
            canvas.delete('all')
            canvas.create_line(0, 505, 1000, 505)
            canvas.create_line(time*25, 500, time*25, 510)
            canvas.create_rectangle(0, 510, 1000, 530, fill='yellow')
            canvas.create_text(500, 520, text='finished')
            d = None
            i = 0
            while len(composition) > i:
                d = composition[i][0].get(time-composition[i][1], d)
                i += 1
            if d is None:
                for x,y in display:
                    canvas.create_oval(x-5,y-5,x+5,y+5)
                tk.update()
                return
            img = Image.fromarray(np.uint8(d))
            size = img.size
            img = img.resize((1000, 500), Image.ANTIALIAS)
            tk.image = ImageTk.PhotoImage(img, master=tk)
            canvas.create_image((0, 0), anchor='nw', image=tk.image)
            for x,y in display:
                canvas.create_oval(x-5,y-5,x+5,y+5)
            tk.update()
        def click(evt):
            nonlocal out, time, size, display, finished
            if evt.y > 510:
                finished = True
            elif evt.y > 500:
                time = evt.x/25
            else:
                display.append((evt.x, evt.y))
                out.append((int((evt.x/1000)*size[1]), int((evt.y/500)*size[0])))
        canvas.bind('<Button-1>', click)
        while not finished:
            update()
        tk.destroy()
        return PointArray(out)
    def __str__(self):
        return 'PointArray()'
