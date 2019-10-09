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
class AlphaPercent:
    def __init__(self, alpha=1):
        self.alpha = alpha
    def get(*args, **kwargs):
        alpha = simpledialog.askinteger('enter alpha', 'enter alpha percentage')
        return AlphaPercent(alpha/100)
    def __str__(self):
        return 'Alpha(%f)'%self.alpha
class Integer:
    def __init__(self, num=1):
        self.num = num
    def get(*args, **kwargs):
        num = simpledialog.askinteger('enter %s'%kwargs.get('name', 'value'), 'enter %s'%kwargs.get('name', 'value'))
        return Integer(num)
    def __str__(self):
        return 'Integer(%d)'%self.num
class MixModes:
    def __init__(self, mode='add'):
        self.modes = {'add':(lambda a,b,h: a*h+b*(1-h)), 'multiply':(lambda a,b,h: a**h*b**(1-h)), 'dissolve':(lambda a,b,h: random.choice([a]*int(h*100)+[b]*int((1-h)*100))), 'screen':(lambda a,b,h:1-((1-a)**h*(1-b)**(1-h))), 'overlay':(lambda a,b,h: ((a**h*b**(1-h)) if a < 0.5 else (1-((1-a)**h*(1-b)**(1-h))))), 'divide':(lambda a,b,h: (a*h)/(b*(1-h))), 'substract':(lambda a,b,h:a*h-b*(1-h)), 'difference':(lambda a,b,h:abs(a*h-b*(1-h)))}
        self.mode = self.modes[mode]
        self.name = mode
    def get(*args, **kwargs):
        modes = {'add':(lambda a,b,h: a*h+b*(1-h)), 'multiply':(lambda a,b,h: a**h*b**(1-h)), 'dissolve':(lambda a,b,h: random.choice([a]*int(h*100)+[b]*int((1-h)*100))), 'screen':(lambda a,b,h:1-((1-a)**h*(1-b)**(1-h))), 'overlay':(lambda a,b,h: ((a**h*b**(1-h)) if a < 0.5 else (1-((1-a)**h*(1-b)**(1-h))))), 'divide':(lambda a,b,h: (a*h)/(b*(1-h))), 'substract':(lambda a,b,h:a*h-b*(1-h)), 'difference':(lambda a,b,h:abs(a*h-b*(1-h)))}
        names = sorted(list(modes.keys()))
        tk = Tk()
        tk.title('mixing mode')
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
    def run(self, a, b, h):
        def apply(a,b,h):
            a = self.mode(a/256,b/256,h)
            if a > 1:
                a = 1
            if a < 0:
                a = 0
            return int(a*256)
        if self.name in ['add', 'multiply', 'screen', 'divide', 'substract', 'difference']:
            return self.mode(a/256,b/256,h)*256
        return np.vectorize(apply)(a,b,h)
    def __str__(self):
        return 'Mix%s()'%self.name.capitalise()
class LayerModes:
    def __init__(self, mode='add'):
        self.modes = {'add':(lambda a,b: a+b), 'multiply':(lambda a,b: a*b), 'screen':(lambda a,b:1-((1-a)*(1-b))), 'overlay':(lambda a,b: ((a*b) if a < 0.5 else (1-((1-a)*(1-b))))), 'divide':(lambda a,b: a/b), 'substract':(lambda a,b:a-b), 'difference':(lambda a,b:abs(a-b)), 'lighten only':(lambda a,b:np.maximum(a,b)), 'darken only':(lambda a,b:np.minimum(a,b))}
        self.mode = self.modes[mode]
        self.name = mode
    def get(*args, **kwargs):
        modes = {'add':(lambda a,b: a+b), 'multiply':(lambda a,b: a*b), 'screen':(lambda a,b:1-((1-a)*(1-b))), 'overlay':(lambda a,b: ((a*b) if a < 0.5 else (1-((1-a)*(1-b))))), 'divide':(lambda a,b: a/b), 'substract':(lambda a,b:a-b), 'difference':(lambda a,b:abs(a-b)), 'lighten only':(lambda a,b:np.maximum(a,b)), 'darken only':(lambda a,b:np.minimum(a,b))}
        names = sorted(list(modes.keys()))
        tk = Tk()
        tk.title('mixing mode')
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
        def apply(a,b):
            a = self.mode(a/256,b/256)
            if a > 1:
                a = 1
            if a < 0:
                a = 0
            return int(a*256)
        if self.name in ['add', 'multiply', 'screen', 'divide', 'substract', 'difference']:
            return self.mode(a/256,b/256)*256
        return np.vectorize(apply)(a,b)
    def __str__(self):
        return 'Layer%s()'%self.name.capitalise()
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
                out.append((int(evt.x/1000*size[0]), int(evt.y/500*size[1])))
        canvas.bind('<Button-1>', click)
        while not finished:
            update()
        tk.destroy()
        return PointArray(out)
    def __str__(self):
        return 'PointArray()'

class Curve:
    def __init__(self, x, y):
        self.fun = scipy.interpolate.interp1d(np.array(x),np.array(y),kind='cubic')
    def get(*args, **kwargs):
        tk = Tk()
        tk.title('Curve editor: %s'%kwargs.get('name', 'Untitled'))
        canvas = Canvas(width=255, height=255)
        canvas.pack()
        xd = [0,63,127,191,255]
        yd = [0,63,127,191,255]
        def update():
            fun = scipy.interpolate.interp1d(np.array(xd),np.array(yd),kind='cubic')
            canvas.delete('all')
            for x in range(255):
                y = int(fun(x))
                canvas.create_rectangle(x,y,x+1,y+1, outline=None, fill='#000')
            for i in range(len(xd)):
                canvas.create_rectangle(xd[i],yd[i],xd[i]+1,yd[i]+1, outline=None, fill='#f0f')
            canvas.update()
        def click(evt):
            xd.append(evt.x)
            yd.append(evt.y)
        canvas.bind('<Button-1>', click)
        while True:
            try:
                update()
            except:
                break
        return Curve(xd,yd)
    def __str__(self):
        pass
