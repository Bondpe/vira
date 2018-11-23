#!/usr/env/python3
from tkinter import *

class Events:
    def __init__(self):
        self.history = []
        self.last = []
        self.checked = True
    def was(self):
        return not self.checked
    def read(self):
        self.checked = True
        c = self.last
        self.last = []
        return c
    def __getitem__(self, i):
        return self.history[0-i]
    def append(self, event):
        self.history.append(event)
        self.last.append(event)
        self.checked = False
class Window:
    def __init__(self, w=700, h=400):
        self.tk = Tk()
        self.c = Canvas(self.tk, height=h, width=w)
        self.c.pack()
        self.c.create_text(w/2,h/2,text='loading...')
        self._update()
        self.c.create_rectangle(0, 0, w, h, fill='white')
        self.c.bind_all('<Button-2>', self._pressM)
        self.c.bind_all('<Button-3>', self._pressR)
        self.c.bind_all('<Motion>', self._onmove)
        self.c.bind_all('<Leave>', self._onleave)
        def press(evt):
            self._pressL(evt)
            self._onMouseRelease(evt)
        self.c.bind_all('<ButtonRelease-1>', press)
        self.c.bind_all('<ButtonPress-1>', self._onMouseHold)
        self.fieldsR = []
        self.fieldsM = []
        self.fieldsL = []
        self.lastclick = [-1,-1]
        self.lastclickR = [-1,-1]
        self.lastclickM = [-1,-1]
        self.oco = str#onClickOut
        self.load()
        self._update()
    def _beforeclick(self, evt):
        pass
    def _afterclick(self, evt):
        pass
    def _update(self):
        self.tk.update()
        self.tk.update_idletasks()
        self.c.update()
    def _onmove(self, evt):
        pass
    def _onMouseRelease(self, evt):
        pass
    def _onMouseHold(self, evt):
        pass
    def _onleave(self, evt):
        pass
    def load(self):
        pass
    def _pressL(self, evt):
        self.lastclick = [evt.x,evt.y]
        c = True
        self._beforeclick(evt)
        for area in self.fieldsL:
            x1, y1, x2, y2, fun, active = area
            if active:
                if evt.x > x1 and evt.x < x2:
                    if evt.y > y1 and evt.y < y2:
                        fun(evt)
                        c = False
        if c:
            self.oco(evt)
        self._afterclick(evt)
    def _pressM(self, evt):
        self.lastclickM = [evt.x,evt.y]
        self._beforeclick(evt)
        c = True
        for area in self.fieldsM:
            x1, y1, x2, y2, fun, active = area
            if active:
                if evt.x > x1 and evt.x < x2:
                    if evt.y > y1 and evt.y < y2:
                        fun(evt)
                        c = False
        if c:
            self.oco(evt)
        self._afterclick(evt)
    def _pressR(self, evt):
        self.lastclickM = [evt.x,evt.y]
        self._beforeclick(evt)
        c = True
        for area in self.fieldsR:
            x1, y1, x2, y2, fun, active = area
            if active:
                if evt.x > x1 and evt.x < x2:
                    if evt.y > y1 and evt.y < y2:
                        fun(evt)
                        c = False
        if c:
            self.oco(evt)
        self._afterclick(evt)
    def update(self):
        self._update()
    def addL(self, x1, y1, x2, y2, fun):
        self.fieldsL.append([x1, y1, x2, y2, fun, True])
        assert x1<x2
        assert y1<y2
        return len(self.fieldsL)-1
    def addM(self, x1, y1, x2, y2, fun):
        self.fieldsM.append([x1, y1, x2, y2, fun, True])
        assert x1<x2
        assert y1<y2
        return len(self.fieldsM)-1
    def addR(self, x1, y1, x2, y2, fun):
        self.fieldsR.append([x1, y1, x2, y2, fun, True])
        assert x1<x2
        assert y1<y2
        return len(self.fieldsR)-1
    def deL(self, id):
        self.fieldsL[id][5] = False
    def deM(self, id):
        self.fieldsM[id][5] = False
    def deR(self, id):
        self.fieldsR[id][5] = False
    def enL(self, id):
        self.fieldsL[id][5] = True
    def enM(self, id):
        self.fieldsM[id][5] = True
    def enR(self, id):
        self.fieldsR[id][5] = True




class MenuBtn(Window):
    def __init__(self, w=1000, h=500):
        self.size = (w,h)
        self.menus = []
        self.active = None
        self.dropped = False
        Window.__init__(self,w,h)
        self.activeBeforeThis = None
        self.mouseover = (-1,-1)
    def _beforeclick(self, evt):
        self.activeBeforeThis = self.active
        self.active = None
    def _afterclick(self, evt):
        self.activeBeforeThis = None
    def _onmove(self, evt):
        self.mouseover = (evt.x,evt.y)
    def _onlaeve(self, evt):
        self.mouseover = (-1,-1)
    def _overSquare(self, x1, y1, x2, y2):
        assert x1 < x2
        assert y1 < y2
        x,y = self.mouseover
        if x1 < x and x2 > x:
            if y1 < y and y2 > y:
                return True
        return False
    def addMenu(self, x1, y1, x2, y2, d=[], text='', funs=[]):
        self.menus.append([x1, y1, x2, y2, d, text, True])
        num = len(self.menus)-1
        def callMenu(evt):
            if self.activeBeforeThis != num:
                self.active = num
                for x in self.menus[-1][7]:
                    self.enL(x)
        self.addL(x1, y1, x2, y2, callMenu)
        ids = []
        for x in range(len(funs)):
            ids.append(self.addL(x1, y2+x*20, x1+100, y2+20+x*20, funs[x]))
        for idi in ids:
            self.deL(idi)
        self.menus[-1].append(ids)
        return num
    def removeMenu(self, id):
        self.menus[id][6] = False
    def recoverMenu(self, id):
        self.menus[id][6] = True
    def isActiveMenu(self, id):
        if self.active == id:
            return True
        return False
    def update(self, full=True):
        self.c.delete('all')
        self.c.create_rectangle(0, 0, self.size[0], self.size[1], fill='white')
        for menu in self.menus:
            x1, y1, x2, y2, d, text, working, funs = menu
            if working:
                self.c.create_rectangle(x1, y1, x2, y2, fill=('lightgray' if self._overSquare(x1, y1, x2, y2) else 'white'))
                self.c.create_text((x1+x2)/2, (y1+y2)/2, text=text)
        if self.active == None:
            if self.dropped:
                for menu in self.menus:
                    for id in menu[7]:
                        self.deL(id)
                self.dropped = False
        else:
            x1, y1, x2, y2, d, text, working, funs = self.menus[self.active]
            if working:
                self.c.create_rectangle(x1, y1, x2, y2, fill='grey')
                self.c.create_text((x1+x2)/2, (y1+y2)/2, text=text)
                for x in range(len(d)):
                    self.c.create_rectangle(x1, y2+x*20, x1+100, y2+20+x*20, fill=('lightgray' if self._overSquare(x1, y2+x*20, x1+100, y2+20+x*20) else 'white'))
                    self.c.create_text(x1+50, y2+10+x*20, text=d[x])
                self.dropped = True
        if full:
           self._update()

class DrawItems(MenuBtn):
    def __init__(self, w=1000, h=500):
        self.items = []
        MenuBtn.__init__(self, w, h)
        self.items = []
        self.keys = []
        self.keydepend = []
        self.keyexecuted = []
        self.c.bind_all('<KeyPress>', self._keypress)
        self.c.bind_all('<KeyRelease>', self._keyrelease)
    def bind(self, keys, fun):
        self.keydepend.append([keys, fun])
    def _keypress(self, evt):
        self.keys.append(evt.keycode)
    def _keyrelease(self, evt):
        self.keys.remove(evt.keycode)
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        self.items.append(['rectangle', x1, y1, x2, y2, kwargs])
        return len(self.items)-1
    def create_text(self, x, y, text):
        self.items.append(['text', x, y, text, 0, 0])
        return len(self.items)-1
    def create_oval(self, x1, y1, x2, y2, **kwargs):
        self.items.append(['oval', x1, y1, x2, y2, kwargs])
        return len(self.items)-1
    def create_button(self, x1, y1, x2, y2, fun, **kwargs):
        kwargs['fun'] = fun
        self.items.append(['button', x1, y1, x2, y2, kwargs])
        return len(self.items)-1
    def update(self, full=True):
        MenuBtn.update(self, False)
        for type,x1,y1,x2,y2,kwargs in self.items:
            if type == 'rectangle':
                self.c.create_rectangle(x1, y1, x2, y2, **kwargs)
            if type == 'text':
                self.c.create_rectangle(x1-4*len(x2), y1+6, x1+4*len(x2), y1-6, fill='white')
                self.c.create_text(x1, y1, text=x2)
            elif type == 'oval':
                self.c.create_oval(x1, y1, x2, y2, **kwargs)
            elif type == 'button':
                self.c.create_rectangle(x1, y1, x2, y2, fill=('lightgray' if self._overSquare(x1, y1, x2, y2) else 'white'))
                self.c.create_text((x1+x2)/2, (y1+y2)/2, text=kwargs['text'])
                x,y = self.lastclick
                if x > x1 and x < x2 and y > y1 and y < y2:
                    kwargs['fun']((x,y))
        self.lastclick = [-1,-1]
        self.lastclickR = [-1,-1]
        self.lastclickM = [-1,-1]
        for dep in self.keydepend:
            if len(dep[0]) == len(self.keys):
                i = True
                for key in dep[0]:
                    if not key in self.keys:
                        i = False
                        if dep in self.keyexecuted:
                            self.keyexecuted.remove(dep)
                        break
                if i and not dep in self.keyexecuted:
                    self.keyexecuted.append(dep)
                    dep[1](self.keys)
            elif dep in self.keyexecuted:
                self.keyexecuted.remove(dep)
        if full:
            self._update()

class Scrollbars(DrawItems):
    def __init__(self, w=1000,h=1000):
        DrawItems.__init__(self,w,h)
        self.scrollbars = []
        self.mousepressed = False
        self.barpressed = None
    def add_scrollbar(self, x1,y1,x2,y2, percentage, size=25):
        self.scrollbars.append([(x1,y1),(x2,y2),percentage, size])
        return len(self.scrollbars)-1
    def recieve_scrollbar(self, id):
        return self.scrollbars[id][-2]
    def _onMouseHold(self, evt):
        self.mousepressed = True
        for n in range(len(self.scrollbars)):
            pos1,pos2,perc,size = self.scrollbars[n]
            x1,y1,x2,y2=pos1+pos2
            if self._overSquare(x1, y1, x2, y2):
                self.barpressed = n
    def _onMouseRelease(self, evt):
        self.mousepressed = False
        self.barpressed = None
    def update(self):
        DrawItems.update(self, False)
        for n in range(len(self.scrollbars)):
            pos1,pos2,perc,size = self.scrollbars[n]
            x1,y1,x2,y2=pos1+pos2
            ps = size*(y2-y1)/200
            p1, p2 = y1+ps,y2-size*(y2-y1)/200
            if n == self.barpressed:
                y = (self.mouseover[1]-p1)*100/(p2-p1)
                if y > 100:
                    y = 100
                elif y < 0:
                    y = 0
                perc = y
                self.scrollbars[n] = [pos1,pos2,perc,size]
            pointer = p1+(p2-p1)*perc/100
            self.c.create_rectangle(x1,y1,x2,y2)
            self.c.create_rectangle(x1, pointer-ps, x2, pointer+ps,
                                    fill=('#555555' if n == self.barpressed else ('lightgrey' if self._overSquare(x1, pointer-size*(y2-y1)/200, x2, pointer+size*(y2-y1)/200) else 'grey')),
                                    outline=('#aaaaaa' if n == self.barpressed else '#222222'),
                                    width=(3 if n == self.barpressed else 2))
            self.c.create_line(x1+(x2-x1)//10, pointer, x2-(x2-x1)//10, pointer)
            self.c.create_line(x1+(x2-x1)//5, pointer-ps//10, x2-(x2-x1)//5, pointer-ps//10)
            self.c.create_line(x1+(x2-x1)//5, pointer+ps//10, x2-(x2-x1)//5, pointer+ps//10)
        self._update()
if __name__ == '__main__':
    win = Scrollbars()
    def foo(evt):
        print('foo')
    def bar(evt):
        print('bar')
    def ispum(evt):
        print('ispum')
    win.addMenu(0, 0, 30, 15, ['foo', 'bar', 'lorem ispum'], 'File', [foo, bar, ispum])
    win.addMenu(30, 0, 60, 15, ['b1', 'b2', 'b3'], 'Edit', [bar, foo, ispum])
    win.create_rectangle(375, 125, 600, 375)
    win.create_oval(375, 125, 600, 375, fill='red')
    win.create_button(375, 375, 600, 400, foo, text='Hello')
    win.bind([37, 24], foo)#Crtl_L-Q
    bar = win.add_scrollbar(100, 100, 150, 500, 0)
    text = win.create_text(500, 500, '0')
    while True:
        win.items[text][3] = hex(int(win.recieve_scrollbar(bar)))
        win.update()
