from tkinter import *
from tkinter import simpledialog, filedialog
import tkinter

import numpy as np
from PIL import Image, ImageTk

import datamanagement
import structure
import input
import constants
import fileoperation

import time
import ffmpeg
import os
from scipy.io.wavfile import write as wavWrite


class Editor:
    def __init__(self):
        self.tk = None
        self.new()

        self.plugins = []
        for plugin in constants.get_plugin_list():
            self.plugins.append(__import__('plugins.'+plugin,fromlist=['object']))
            plugin_data = self.plugins[-1].data
            structure.avaliable += plugin_data["structure_avaliable"]

    def update(self):
        for part in self.parts:
            part.update()
        self.tk.update()

    def update_data(self, old=True):
        if old:
            self.system_data['time'] = self.time
            self.system_data['selected'] = self.selected
        else:
            self.system_data = {'areas': [], 'time': 1, 'selected': 0}

    def save(self, path):
        self.update_data()
        file = open(path, 'wb')
        file.write(fileoperation.to_bytes(self.root_comp,
                                          datamanagement.pack_data(),
                                          self.system_data))
        file.close()
        self.path = path

    def open(self, path):
        self.update_data(False)
        self.composition, system_data = fileoperation.from_bytes(
            open(path, 'rb').read(), datamanagement.load_data)
        self.root_comp = self.composition
        self.path = path

        self.setup()

        self.selected = system_data['selected']
        self.play = False
        self.time = system_data['time']

        areas = system_data['areas']

        for area, kwargs in areas:
            area(self, **kwargs)

        self.update_data()

    def new(self):
        self.setup()

        self.composition = self.root_comp = []
        self.selected = 0
        datamanagement.data = {}
        self.path = None
        self.play = False
        self.time = 1
        self.parts = []

        self.update_data(False)

        InheritTree(self)
        AddMenu(self)
        Preview(self)
        Composition(self)
        EditorMenu(self)
    def setup(self):
        if self.tk is not None:
            for i in self.tk.winfo_children():
                i.destroy()
        else:
            self.tk = Tk()
            self.tk.title('vira')
            self.tk.config(bg=constants.theme['fbg'])
            self.tk.minsize(1900,1000)

        self.parts = []

        ip = constants.icon_path
        self.images = {'export': PhotoImage(
            file=ip+'export.gif'), 'resort': PhotoImage(file=ip+'resort.gif'),
                       'skipToBeginning': PhotoImage(file=ip+'skipToBeginning.gif'),
                       '0': PhotoImage(file=ip+'0.gif')}


class EditorMenu:
    def __init__(self, editor, side='top'):
        self.editor = editor
        self.tk = self.editor.tk
        self.editor.parts.append(self)
        self.editor.system_data['areas'].append(
            [self.__class__, {'side': side}])

        menu = Menu(self.tk)
        menu.add_command(label='New', command=self.new)
        self.tk.bind('<Control-n>', lambda a:self.new())
        menu.add_command(label='Open', command=self.open)
        self.tk.bind('<Control-o>', lambda a:self.open())
        menu.add_command(label='Save', command=self.save)
        self.tk.bind('<Control-s>', lambda a:self.save())
        menu.add_command(label='Save as', command=self.save_as)
        self.tk.bind('<Control-S>', lambda a:self.save_as())
        menu.add_command(label='Export', command=self.export)
        self.tk.bind('<Control-e>', lambda a:self.export())
        win_menu = Menu(menu, tearoff=0)
        win_menu.add_command(label='Preview', command=lambda: Preview(
            self.editor, 'top', *input.Resolution.get().r))
        win_menu.add_command(label='Composition',
                             command=lambda: Composition(self.editor))
        win_menu.add_command(
            label='Tree', command=lambda: InheritTree(self.editor))
        win_menu.add_command(
            label='Effects', command=lambda: AddMenu(self.editor))
        menu.add_cascade(label='Add area', menu=win_menu)
        self.tk.config(menu=menu)

    def update(self):
        pass

    def new(self):
        self.editor.new()

    def open(self):
        path = filedialog.Open(self.tk).show()
        if isinstance(path, str) and len(path) > 0:
            self.editor.open(path)

    def save_as(self):
        path = filedialog.SaveAs(self.tk).show()
        if isinstance(path, str) and len(path) > 0:
            self.editor.save(path)

    def save(self):
        if self.editor.path is None:
            self.save_as()
        else:
            self.editor.save(self.editor.path)

    def export(self):
        start, end = input.TimeSegment.get().time
        width, height = input.Resolution.get().r
        fps = simpledialog.askinteger('fps', 'render FPS')
        freq_sound = simpledialog.askinteger('fps', 'sound freq')
        path = filedialog.SaveAs(self.tk).show()
        if not isinstance(path, str) or len(path) == 0:
            path = 'out.mp4'
        if not path.endswith('.mp4'):
            path += '.mp4'
        array = constants.get_temp_path()
        os.mkdir(array)
        exportWindow = Tk()
        exportWindow.title('Exporting progress...')
        exportCanvas = Canvas(exportWindow, width=400,height=300)
        exportCanvas.pack()
        for frame in range(int(start*fps), int(end*fps)):
            percent = (frame-int(start*fps))/(int(end*fps)-int(start*fps))*100
            exportCanvas.delete('all')
            exportCanvas.create_rectangle(0, 0, 400, 300, fill='green')

            exportCanvas.create_text(200, 25, text='Video:')
            exportCanvas.create_rectangle(100,60,300,90,fill='blue')
            exportCanvas.create_rectangle(100,60,100+2*percent,90,fill='yellow')

            exportCanvas.create_text(200, 125, text='Audio:')
            exportCanvas.create_rectangle(100,160,300,190,fill='red')
            exportCanvas.create_text(200, 175, text='Not started yet')
            exportCanvas.update()

            time = frame/fps
            d = None
            i = 0
            while len(self.editor.root_comp) > i:
                d = self.editor.root_comp[i][0].get(
                    time-self.editor.root_comp[i][1], d)
                i += 1
            if d is not None:
                img = Image.fromarray(np.uint8(d))
                img = img.resize((width, height), Image.ANTIALIAS)
                img.save(array+'/frame%03d.png' % (frame-int(start*fps)+1))
        sound = []
        for beat in range(int(start*freq_sound), int(end*freq_sound)):
            percent = (beat-int(start*freq_sound))/(int(end*freq_sound)-int(start*freq_sound))*100
            exportCanvas.delete('all')
            exportCanvas.create_rectangle(0, 0, 400, 300, fill='green')

            exportCanvas.create_text(200, 25, text='Audio:')
            exportCanvas.create_rectangle(100,60,300,90,fill='blue')
            exportCanvas.create_rectangle(100,60,100+2*percent,90,fill='yellow')

            exportCanvas.create_text(200, 125, text='Video:')
            exportCanvas.create_rectangle(100,160,300,190,fill='white')
            exportCanvas.create_text(200, 175, text='Successfully finished')
            exportCanvas.update()

            time = beat/freq_sound
            d = 0
            i = 0
            while len(self.editor.root_comp) > i:
                d = self.editor.root_comp[i][0].sound(
                    time-self.editor.root_comp[i][1], d)
                i += 1
            sound.append(d)
        exportCanvas.create_text(200, 250, text='Packing...')
        exportCanvas.update()
        wavWrite(array+'/audio.wav', freq_sound, np.array(sound))
        video = ffmpeg.input(array+'/frame*.png',
                             pattern_type='glob', framerate=fps)
        audio = ffmpeg.input(array+'/audio.wav')
        out = ffmpeg.output(video, audio, path)
        out.run()
        exportWindow.destroy()


class Preview:
    def __init__(self, editor, x=740, y=0, width=16*35, height=9*35):
        self.editor = editor
        self.tk = self.editor.tk
        self.editor.system_data['areas'].append(
            [self.__class__, {'x':x,'y':y, 'width': width, 'height': height}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.frame = Frame(self.tk, bg=constants.theme['bg'])
        self.frame.bind('<Button1-Motion>', self.move)
#        self.frame.pack()
        self.frame.place(x=x,y=y)
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill='red')
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.grid(row=1,column=2)
        self.editor.parts.append(self)
        self.width, self.height = width, height
        self.canvas = Canvas(self.frame, width=self.width,
                             height=self.height+25, bg=constants.theme['bg'])
        self.canvas.grid(row=2, column=1)
        self.canvas.bind('<Button-1>', self.click)

        self.text=''
        self.lastDisplayed=False
    def move(self, evt):
        x=self.tk.winfo_pointerx()-self.tk.winfo_x()
        y=self.tk.winfo_pointery()-self.tk.winfo_y()
        self.frame.place(x=x, y=y)
        self.editor.system_data['areas'][self.system_data_self_id][1]['x']=x
        self.editor.system_data['areas'][self.system_data_self_id][1]['y']=y

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]

    def click(self, evt):
        if evt.y < self.height:
            self.text = 'x:%d,y:%d,color:%s DISPLAYED (may differ in the final render)'%(evt.x,evt.y,(str(self.last_frame[evt.x,evt.y]) if self.lastDisplayed else 'None'))
        if evt.x < 25:
            self.editor.play = not self.editor.play
        elif evt.x < 50:
            self.export()
        elif evt.x < 75:
            self.editor.time = 0

    def export(self):
        start, end = input.TimeSegment.get().time
        width, height = input.Resolution.get().r
        fps = simpledialog.askinteger('fps', 'render FPS')
        path = filedialog.SaveAs(self.tk).show()
        if not isinstance(path, str) or len(path) == 0:
            path = 'out.mp4'
        if not path.endswith('.mp4'):
            path += '.mp4'
        array = constants.get_temp_path()
        os.mkdir(array)
        for frame in range(int(start*fps), int(end*fps)):
            time = frame/fps
            d = None
            i = 0
            while len(self.editor.composition) > i:
                d = self.editor.composition[i][0].get(
                    time-self.editor.composition[i][1], d)
                i += 1
            if d is not None:
                img = Image.fromarray(np.uint8(d))
                img = img.resize((width, height), Image.ANTIALIAS)
                img.save(array+'/frame%03d.png' % (frame-int(start*fps)+1))
        (ffmpeg
         .input(array+'/frame*.png', pattern_type='glob', framerate=fps)
         .output(path)
         .run()
         )

    def update(self):
        self.canvas.delete('all')
        # frame change, play button
        if self.editor.play:
            self.editor.time += time.time()-self.editor.lastRender
            self.canvas.create_rectangle(
                5, self.height+5, 10, self.height+20, fill='yellow')
            self.canvas.create_rectangle(
                15, self.height+5, 20, self.height+20, fill='yellow')
        else:
            self.canvas.create_polygon(5, self.height+5,
                                       5, self.height+20,
                                       20, self.height+12,
                                       fill='green')
        self.editor.lastRender = time.time()
        self.canvas.create_image(
            25, self.height, anchor='nw', image=self.editor.images['export'])
        self.canvas.create_image(
            50, self.height, anchor='nw', image=self.editor.images['skipToBeginning'])
        self.canvas.create_text(75,self.height+12,anchor='w',text=self.text, font=('Comfortaa', 5), fill=constants.theme['mark'])
        d = None
        i = 0
        while len(self.editor.composition) > i:
            d = self.editor.composition[i][0].get(
                self.editor.time-self.editor.composition[i][1], d)
            i += 1
        if d is None:
            self.lastDisplayed=False
            return
        img = Image.fromarray(np.uint8(d))
        img = img.resize((self.width, self.height), Image.ANTIALIAS)
        self.last_frame=img.load()
        self.canvas.image = ImageTk.PhotoImage(img)
        self.canvas.create_image((0, 0), anchor='nw', image=self.canvas.image)
        self.lastDisplayed=True


class Composition:
    def __init__(self, editor, x=515, y=400):
        self.editor = editor
        self.tk = self.editor.tk
        self.frame = Frame(self.tk, bg=constants.theme['bg'])
#        self.frame.pack()
        self.frame.place(x=x,y=y)
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill='red')
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.grid(row=1,column=2)
        self.editor.parts.append(self)
        self.editor.system_data['areas'].append(
            [self.__class__, {'x':x,'y':y}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.canvas = Canvas(self.frame, width=1000, height=525, bg=constants.theme['bg'])
        self.canvas.grid(row=2,column=1)
        self.pos = [0, 0]
        self.scale = 25
        self.selected = 0
        btnF = Frame(self.frame)
        btnF.grid(row=1,column=1)
        Button(btnF, text='Add', command=self.add, bg=constants.theme['bg']).pack(side='left')
        Button(btnF, text='Go to root composition',
               command=self.root, bg=constants.theme['bg']).pack(side='right')
        self._initialise_binds()
    def move(self, evt):
        x=self.tk.winfo_pointerx()-self.tk.winfo_x()
        y=self.tk.winfo_pointery()-self.tk.winfo_y()
        self.frame.place(x=x, y=y)
        self.editor.system_data['areas'][self.system_data_self_id][1]['x']=x
        self.editor.system_data['areas'][self.system_data_self_id][1]['y']=y

    def root(self):
        self.editor.composition = self.editor.root_comp

    def _initialise_binds(self):
        self.frame.bind('<Button1-Motion>', self.move)
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Motion>', self._move)
        self.canvas.bind('<ButtonPress-2>', self._startdrag)
        self.canvas.bind('<ButtonRelease-2>', self._stopdrag)
        self.canvas.bind('<ButtonPress-3>', self._startzoom)
        self.canvas.bind('<ButtonRelease-3>', self._stopzoom)
        self.canvas.bind('<ButtonPress-4>', self._zoomin)
        self.canvas.bind('<ButtonPress-5>', self._zoomout)
        self.canvas.bind('<Motion>', lambda e: self.canvas.focus_set())
        self.canvas.bind('<Delete>', lambda e: self.remove_selected_stream())
        self.canvas.bind('<BackSpace>', self.remove_hovered_stream)
        self._d_moving = False
        self._z_moving = False

    def _zoomin(self,evt):
        self.scale*=1.5
    def _zoomout(self,evt):
        self.scale/=1.5

    def _startdrag(self, evt):
        self._d_moving = True
        self._d_startpos = self.pos
        self._d_mouse = evt.x, evt.y

    def _stopdrag(self, evt):
        self._d_moving = False

    def _stopzoom(self, evt):
        self._z_moving = False

    def _startzoom(self, evt):
        self._z_moving = True
        self._z_pos = evt.y

    def _move(self, evt):
        if self._d_moving:
            self.pos = self._d_startpos
            self.pos[0] += (evt.x-self._d_mouse[0])
            self.pos[1] += (evt.y-self._d_mouse[1])
            if self.pos[1]>0: self.pos[1]=0
            self._d_startpos = self.pos
            self._d_mouse = evt.x, evt.y
        if self._z_moving:
            if evt.y > self._z_pos:
                self.scale /= (evt.y-self._z_pos)*1.25
            if evt.y < self._z_pos:
                self.scale *= (self._z_pos-evt.y)*1.25
            self._z_pos = evt.y

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]
    def remove_selected_stream(self):
        if len(self.editor.composition) > self.selected:
            del self.editor.composition[self.selected]
    def remove_hovered_stream(self, evt):
        if evt.x > 950:
            return
        selected = (evt.y-self.pos[1])//20
        if len(self.editor.composition) > selected:
            del self.editor.composition[selected]

    def click(self, evt):
        if evt.x > 950:
            if evt.y < 50:
                self.remove_selected_stream()
            elif evt.y < 100 and len(self.editor.composition) > self.selected:
                t = self.editor.composition[self.selected]
                del self.editor.composition[self.selected]
                self.selected -= 1
                self.editor.composition.insert(self.selected, t)
            elif evt.y < 150:
                self.scale=25
                self.pos=[0,0]
            return
        self.selected = (evt.y-self.pos[1])//20
        self.editor.time = (evt.x-self.pos[0])/self.scale

    def add(self): # now accessible as AddMenu
        menu = Tk()
        menu.title('choose what to add')
        c = Canvas(menu, width=1000, height=500)
        c.pack()
        types = []
        for t in structure.avaliable:
            if t.category not in types:
                types.append(t.category)
        categ = 0
        pos1 = 0
        pos2 = 0
        shown = []

        def update():
            nonlocal c, categ, pos1, pos2, types, shown
            c.delete('all')
            # categoties
            c.create_rectangle(0, 0, 500, 500, fill=constants.theme['bg'])
            categoryId = 0
            for t in types:
                c.create_rectangle(10, pos1+2+categoryId*20,
                                   490, pos1+18+categoryId*20, fill=constants.theme['bg'], outline=constants.theme['selected'])
                c.create_text(30, pos1+10+categoryId*20, anchor='w', text=t, fill=constants.theme['fg'])
                if categoryId == categ:
                    c.create_polygon(15, pos1+10+categoryId*20,
                                     25, pos1+10 + categoryId*20,
                                     20, pos1+15+categoryId*20, fill=constants.theme['fg'])
                else:
                    c.create_polygon(20, pos1+5+categoryId*20,
                                     20, pos1+15 + categoryId*20,
                                     25, pos1+10+categoryId*20, fill=constants.theme['fg'])
                categoryId += 1
            # stream types
            c.create_rectangle(500, 0, 1000, 500, fill=constants.theme['bg'])
            n = 0
            shown = []
            for t in structure.avaliable:
                if t.category == types[categ]:
                    shown.append(t)
                    c.create_rectangle(510, pos2+2+n*20, 990,
                                       pos2+18+n*20, fill=constants.theme['fbg'], outline=constants.theme['non-selected'])
                    c.create_text(515, pos2+10+n*20, anchor='w', text=t.Tname, fill=constants.theme['fg'])
                    n += 1
            c.update()

        def click(evt):
            nonlocal c, categ, pos1, pos2, types, shown
            if evt.x < 500:
                categ = min((evt.y-pos1)//20, len(types)-1)
            else:
                menu.destroy()
                n = (evt.y-pos2)//20
                append = shown[n if n < len(shown) else -1]()
                if 'c' in list(append.argtype.values()):
                    if len(self.editor.composition) <= self.selected:
                        return
                for k in append.argkeys:
                    v = append.argtype[k]
                    if v == 'c':
                        append.args[k] = self.editor.composition[self.selected][0]
                    else:
                        append.args[k] = v.get(
                            composition=self.editor.composition, name=k)
                append.setup()
                if 'c' in list(append.argtype.values()):
                    del self.editor.composition[self.selected]
                self.editor.composition.insert(self.selected, [append, 0])
        c.bind('<Button-1>', click)

        def up(evt):
            nonlocal pos1, pos2
            if evt.x < 500:
                pos1 += 5
                if pos1 > 0:
                    pos1 = 0
            else:
                pos2 += 5
                if pos2 > 0:
                    pos2 = 0

        def down(evt):
            nonlocal pos1, pos2
            if evt.x < 500:
                pos1 -= 5
            else:
                pos2 -= 5
        c.bind('<Button-4>', up)
        c.bind('<Button-5>', down)
        while True:
            try:
                update()
            except tkinter._tkinter.TclError:
                return  # finished, window closed

    def update(self):
        self.canvas.delete('all')
        n = 0
        for i in self.editor.composition: # display streams
            self.canvas.create_rectangle(
                0, n*20+self.pos[1], 1000, n*20+20+self.pos[1], fill=constants.theme['hbg'] if self.selected == n else constants.theme['fbg'])
            startEnd = i[0].getStartEnd()
            if startEnd is not None:
                self.canvas.create_rectangle(startEnd[0]*self.scale+self.pos[0],
                                             n*20+self.pos[1],
                                             startEnd[1] * self.scale+self.pos[0],
                                             n*20+20+self.pos[1],
                                             fill=constants.theme['selected'] if self.selected == n else constants.theme['non-selected'])
            self.canvas.create_text(500, n*20+10+self.pos[1],
                                    fill=constants.theme['sfg'] if self.selected == n else constants.theme['fg'],
                                    text=i[0].get_name())
            self.canvas.create_line(i[1]*self.scale+self.pos[0], n*20+self.pos[1],
                                    i[1]*self.scale+self.pos[0], n*20+20+self.pos[1],
                                    fill=constants.theme['mark'])
            n += 1
        # time cursor
        self.canvas.create_rectangle(0, 500, 1000, 525, fill=constants.theme['hbg'])
        for x in range(10):
            self.canvas.create_line(x*100, 500, x*100, 505, fill=constants.theme['mark'])
            self.canvas.create_text(
                x*100, 515,
                text=str((x*100-self.pos[0])/self.scale)[:6])
        self.canvas.create_line(
            self.editor.time*self.scale + self.pos[0], 0,
            self.editor.time*self.scale+self.pos[0], 500,
            fill=constants.theme['selected'])
        self.canvas.create_rectangle(
            self.editor.time*self.scale+self.pos[0]-50, 500,
            self.editor.time*self.scale+self.pos[0]+50, 520,
            fill=constants.theme['hbg'])
        def rn(n, digits): return round(n, digits-len(str(int(n))))
        self.canvas.create_text(self.editor.time*self.scale+self.pos[0], 510,
                                text=rn(self.editor.time, 7))

        # side panel
        self.canvas.create_rectangle(950, 0, 1000, 525, fill=constants.theme['hbg'])
        self.canvas.create_text(
            975, 25, text='X', fill=constants.theme['mark'], font=('Ariel', 25))
        self.canvas.create_image(
            950, 50, anchor='nw',
            image=self.editor.images['resort'])
        self.canvas.create_image(
            950, 100, anchor='nw',
            image=self.editor.images['0'])
        self.canvas.create_text(950,125,text='s-ted:%d,\npos:%s,\nscale:%f'%(self.selected,str(self.pos),self.scale),font=('Comfortaa',8),anchor='w', fill=constants.theme['selected'])
        self.editor.selected = self.selected
class AddMenu:
    def __init__(self, editor, x=1530,y=0):
        self.editor = editor

        self.tk = self.editor.tk
        self.frame = Frame(self.tk,bg=constants.theme['bg'])
#        self.frame.pack()
        self.frame.place(x=x,y=y)
        self.frame.bind('<Button1-Motion>', self.moveFrame)
        self.editor.system_data['areas'].append(
            [self.__class__, {'x':x,'y':y}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill=constants.theme['mark'])
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.grid(row=1,column=2)
        self.editor.parts.append(self)
        self.canvas = Canvas(self.frame, width=350, height=900, bg=constants.theme['bg'])
        self.canvas.grid(row=2,column=1)
        self.pos = 25
        self.shownCategs = []
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Button-4>', self.up)
        self.canvas.bind('<Button-5>', self.down)
        self.canvas.bind('<Motion>', self.move)

        self.hints = []
        self.hintsDisplay = []
    def moveFrame(self, evt):
        x=self.tk.winfo_pointerx()-self.tk.winfo_x()
        y=self.tk.winfo_pointery()-self.tk.winfo_y()
        self.frame.place(x=x, y=y)
        self.editor.system_data['areas'][self.system_data_self_id][1]['x']=x
        self.editor.system_data['areas'][self.system_data_self_id][1]['y']=y
    def up(self,evt):
        self.pos+=5
    def down(self,evt):
        self.pos-=5
    def move(self,evt):
        self.hintsDisplay = []
        for x1,y1,x2,y2,text in self.hints:
            if evt.x in range(x1,x2) and evt.y in range(y1,y2):
                self.hintsDisplay.append([evt.x,evt.y,text])

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]
    def update(self):
        self.hints = []
        if self.pos>25:
            self.pos=25
        self.canvas.delete('all')
        types = {}
        catg = []
        for t in structure.avaliable:
            if t.category not in types:
                types[t.category] = [t]
                catg.append(t.category)
            else:
                types[t.category].append(t)
        pos = self.pos
        self.btns = []
        for category in catg:
            self.canvas.create_rectangle(0,pos,350,pos+25,fill=constants.theme['fbg'],outline=constants.theme['hbg'])
            self.canvas.create_text(25,pos+12,text=category,anchor='w',fill=constants.theme['fg'])
            pos+=25
            if category in self.shownCategs:
                self.canvas.create_polygon(10,pos-20,15,pos-20,12,pos-15,fill=constants.theme['fg'])
                self.btns.append(['hide',category])
                for item in types[category]:
                    self.canvas.create_rectangle(0,pos,350,pos+25,fill=constants.theme['bg'])
                    self.canvas.create_text(50,pos+12,text=item.Tname,anchor='w',fill=constants.theme['fg'])
                    if 'c' in list(item.argtype.values()):
                        self.canvas.create_oval(5, pos+5, 20, pos+20, fill=constants.theme['selected'])
                        self.canvas.create_text(13, pos+12, fill=constants.theme['mark'], text='rc')
                        self.hints.append([5, pos+5, 20, pos+20, 'requires a child'])
                        if not item.saveDefault:
                            self.canvas.create_oval(20, pos+5, 35, pos+20, fill=constants.theme['selected'])
                            self.canvas.create_text(28, pos+12, fill=constants.theme['mark'], text='es')
                            self.hints.append([20, pos+5, 35, pos+20, 'extraordinary saving'])
                    elif not item.saveDefault:
                        self.canvas.create_oval(5, pos+5, 20, pos+20, fill=constants.theme['selected'])
                        self.canvas.create_text(13, pos+12, fill=constants.theme['mark'], text='es')
                        self.hints.append([5, pos+5, 20, pos+20, 'extraordinary saving'])
                    pos+=25
                    self.btns.append(['add',item])
            else:
                self.canvas.create_polygon(10,pos-15,10,pos-10,15,pos-12,fill=constants.theme['fg'])
                self.btns.append(['show',category])
        self.canvas.create_rectangle(0,0,350,25,fill=constants.theme['fbg'])
        self.canvas.create_text(10,12,text='fx',font=('Comfortaa',12),fill=constants.theme['hbg'],anchor='w')
        self.canvas.create_text(325,12,text='effects,streams,etc. library',font=('Comfortaa',10),fill=constants.theme['bg'],anchor='e')
        for x,y,text in self.hintsDisplay:
            if x>350/2:
                i=self.canvas.create_text(x,y,text=text,anchor='se', fill=constants.theme['fg'])
                r=self.canvas.create_rectangle(self.canvas.bbox(i), fill=constants.theme['hbg'])
                self.canvas.tag_lower(r,i)

            else:
                i=self.canvas.create_text(x, y,text=text,anchor='sw', fill=constants.theme['fg'])
                r=self.canvas.create_rectangle(self.canvas.bbox(i), fill=constants.theme['hbg'])
                self.canvas.tag_lower(r,i)
    def click(self, evt):
        action, data = self.btns[(evt.y-self.pos)//25]
        if action == 'hide':
            self.shownCategs.remove(data)
        elif action == 'show':
            self.shownCategs.append(data)
        else:
            append=data()
            if 'c' in list(append.argtype.values()):
                if len(self.editor.composition) <= self.editor.selected:
                    return
            for k in append.argkeys:
                v = append.argtype[k]
                if v == 'c':
                    append.args[k] = self.editor.composition[self.editor.selected][0]
                else:
                    append.args[k] = v.get(
                        composition=self.editor.composition, name=k)
            append.setup()
            if 'c' in list(append.argtype.values()):
                del self.editor.composition[self.editor.selected]
            self.editor.composition.insert(self.editor.selected, [append, 0])

class InheritTree:
    def __init__(self, editor, x=0, y=0):
        self.editor = editor

        self.tk = self.editor.tk
        self.frame = Frame(self.tk,bg=constants.theme['bg'])
#        self.frame.pack()
        self.frame.place(x=x,y=y)
        self.frame.bind('<Button1-Motion>', self.move)
        self.editor.system_data['areas'].append(
            [self.__class__, {'x':x,'y':y}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill=constants.theme['mark'])
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.grid(row=1,column=2)
        self.editor.parts.append(self)
        self.canvas = Canvas(self.frame, width=500, height=900, bg=constants.theme['bg'])
        self.canvas.grid(row=2,column=1)
        self.open = 0
        self.pos = 0
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Button-4>', self.up)
        self.canvas.bind('<Button-5>', self.down)
        self.canvas.bind('<Motion>', lambda e: self.canvas.focus_set())
        self.canvas.bind('<Key>', self.keyPress)
    def move(self, evt):
        x=self.tk.winfo_pointerx()-self.tk.winfo_x()
        y=self.tk.winfo_pointery()-self.tk.winfo_y()
        self.frame.place(x=x, y=y)
        self.editor.system_data['areas'][self.system_data_self_id][1]['x']=x
        self.editor.system_data['areas'][self.system_data_self_id][1]['y']=y
    def up(self,evt):
        self.pos+=10
    def down(self,evt):
        self.pos-=10

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]

    def click(self,evt):
        n = (evt.y-self.pos)//25-1
        item = self.editor.composition[self.editor.selected][0]
        pos = self.pos
        i = 0
        out = None
        while True:
            if evt.y in range(pos,pos+25):
                out = [0,i]
            pos+=25
            if i == self.open:
                args = []
                for a in item.args:
                    if a != 'child':
                        args.append(a)
                for arg in args:
                    try:
                        deltaP=max(25,item.args[arg].dialog({'action':'get dialog height'}))
                    except:
                        deltaP=25
                    if evt.y in range(pos,pos+deltaP):
                        out = [1,i,item,arg,evt.y-pos]
                    pos+=deltaP
            if item.is_box():
                item = item.args['child']
                i+=1
            else:
                break
        if out is None:
            self.edit(i)
            self.open=i
        if out[0] == 0:
            n = out[1]
            if evt.x > 480:
                self.delete(n-1)
            elif evt.x > 460:
                self.edit(n)
            else:
                self.open=n
            return
        item = out[2]
        name = out[-2]
        args = []
        for a in item.args:
            if a != 'child':
                args.append(a)
        try:
            clickdata = {'action':'click','x':500-evt.x,'y':out[-1]}
            assert False!=item.args[name].dialog(clickdata)
        except:
            arg = item.argtype[name].get(
                composition=self.editor.composition,
                name=name, old=item.args[name])
            if isinstance(arg, list) and arg[0] == 'composition':
                self.editor.composition = arg[1]
            else:
                item.args[name] = arg
            item.setup()

    def keyPress(self,evt):
        n = (evt.y-self.pos)//25-1
        try:
            item = self.editor.composition[self.editor.selected][0]
        except:
            return
        pos = self.pos
        i = 0
        out = None
        while True:
            if evt.y in range(pos,pos+25):
                out = [0,i]
            pos+=25
            if i == self.open:
                args = []
                for a in item.args:
                    if a != 'child':
                        args.append(a)
                for arg in args:
                    try:
                        delta=max(25,item.args[arg].dialog({'action':'get dialog height'}))
                    except:
                        delta=25
                    if evt.y in range(pos,pos+delta):
                        out = [1,i,item,arg,evt.y-pos]
                    pos+=delta
            if item.is_box():
                item = item.args['child']
                i+=1
            else:
                break
        if out is None or out[0] == 0:
            return
        item = out[2]
        name = out[-2]
        try:
            clickdata = {'action':'key','x':evt.x,'y':out[-1],'key':(evt.char,evt.keysym,evt.keycode)}
            item.args[name].dialog(clickdata)
        except:
            pass
#            print('%s - unsupported'%name)


    def delete(self, n):
        try:
            if n == -1:
                self.editor.composition[self.editor.selected][0] = self.editor.composition[self.editor.selected][0].args['child']
                return
            item = self.editor.composition[self.editor.selected][0]
            for x in range(n):
                item = item.args['child']
            item.args['child'] = item.args['child'].args['child']
        except IndexError:
            return False
        except KeyError:
            return False

    def edit(self, n):
        try:
            item = self.editor.composition[self.editor.selected][0]
            for x in range(n):
                if 'child' in item.args:
                    item = item.args['child']
            # select input
            args = []
            for a in item.args:
                if a != 'child':
                    args.append(a)
            tk = Tk()
            tk.title('Choose value to change')
            c = Canvas(tk, width=1000, height=len(args)*50)
            c.pack()
            n = 0
            for arg in args:
                c.create_text(250, 25+n*50, text=arg)
                c.create_text(750, 25+n*50, text=str(item.args[arg]))
                n += 1

            def select(evt):
                name = args[evt.y//50]
                arg = item.argtype[name].get(
                    composition=self.editor.composition,
                    name=name, old=item.args[name])
                if isinstance(arg, list) and arg[0] == 'composition':
                    self.editor.composition = arg[1]
                else:
                    item.args[name] = arg
                item.setup()
                tk.destroy()
            c.bind('<Button-1>', select)

            name_entry = Entry(tk)
            name_entry.insert(END, item.name)
            name_entry.pack(side='bottom')

            def new_name():
                item.name = name_entry.get()
                tk.destroy()
            Button(tk, text='save new name', command=new_name).pack()

            try:
                while True:
                    tk.update()
            except tkinter._tkinter.TclError:
                pass
        except IndexError:
            return False

    def update(self):
        if self.pos>0:
            self.pos=0
        self.canvas.delete('all')
        if self.editor.selected >= len(self.editor.composition):
            return
        item = self.editor.composition[self.editor.selected][0]
        pos = self.pos
        i = 0
        while True:
            self.canvas.create_rectangle(
                0, pos, 500, pos+25, fill=constants.theme['hbg'])
            self.canvas.create_text(10, pos, text=item.name, anchor='nw', fill='white')
            self.canvas.create_rectangle(480,pos,500,pos+25,fill=constants.theme['fg'])
            self.canvas.create_text(490,pos+12,fill=constants.theme['mark'],text='x')
            self.canvas.create_rectangle(460,pos,480,pos+25,fill=constants.theme['fg'])
            self.canvas.create_text(470,pos+12,fill=constants.theme['mark'],text='e')
            pos+=25
            if i == self.open:
                self.canvas.create_polygon(5,pos-20,5,pos-10,10,pos-15, fill=constants.theme['fg'])
                args = []
                for a in item.args:
                    if a != 'child':
                        args.append(a)
                for arg in args:
                    self.canvas.create_text(25,pos,text=arg,anchor='nw',fill=constants.theme['fg'])
                    try:
                        item.args[arg].dialog({'action':'display','canvas':self.canvas,'pos':(500,pos)})
                    except BaseException as e:
                        #print(e)
                        self.canvas.create_text(500,pos,text=str(item.args[arg]),anchor='ne',fill=constants.theme['sfg'])
                    try:
                        pos+=max(25,item.args[arg].dialog({'action':'get dialog height'}))
                    except:
                        pos+=25
            if item.is_box():
                item = item.args['child']
                i += 1
            else:
                break


if __name__ == '__main__':
    e = Editor()
    while True:
        e.update()
