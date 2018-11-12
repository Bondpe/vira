#!/usr/env/python3
from tkinter import *

class Events:
    def __init__(self):
        self.history = []
        self.checked = True
    def was(self):
        return not self.checked
    def read(self):
        self.checked = True
        return history[-1]
    def __getitem__(self, i):
        return self.history[0-i]
    def append(self, event):
        self.history.append(event)
        self.checked = False
class Window:
    def __init__(self, w=700, h=400):
        self.tk = Tk()
        self.c = Canvas(self.tk, height=h, width=w)
        self.c.pack()
        self.c.create_text(w/2,h/2,text='loading...')
        self.mouseL = Events()
        self.mouseM = Events()
        self.mouseR = Events()
        self.c.create_rectangle(0, 0, w, h, fill='white')
        self.c.bind_all('<Button-1>', self._pressL)
        self.c.bind_all('<Button-2>', self._pressM)
        self.c.bind_all('<Button-3>', self._pressR)
        self.c.bind_all('<Motion>', self._onmove)
        self.c.bind_all('<Leave>', self._onleave)
        self.fieldsR = []
        self.fieldsM = []
        self.fieldsL = []
        self.oco = str#onClickOut
        self.load()
        self.update()
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
    def _onleave(self, evt):
        pass
    def load(self):
        pass
    def _pressL(self, evt):
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
    def update(self):
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
        self._update()
if __name__ == '__main__':
    win = MenuBtn()
    def foo(evt):
        print('foo')
    def bar(evt):
        print('bar')
    def ispum(evt):
        print('ispum')
    win.addMenu(0, 0, 30, 15, ['foo', 'bar', 'lorem ispum'], 'File', [foo, bar, ispum])
    win.addMenu(30, 0, 60, 15, ['b1', 'b2', 'b3'], 'Edit', [bar, foo, ispum])
    while True:
        win.update()
