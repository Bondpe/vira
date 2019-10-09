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

        for plugin in constants.get_plugin_list():
            exec('from plugins import %s' % plugin)
            exec(
                'plugin_data = %s.main(input, structure, constants)' % plugin +
                '\nstructure.avaliable += plugin_data["structure_avaliable"]')

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

        if self.tk is not None:
            self.tk.destroy()
        self.tk = Tk()
        self.tk.title('vira')
        self.selected = system_data['selected']
        self.play = False
        self.time = system_data['time']
        self.parts = []
        ip = constants.icon_path
        self.images = {'export': PhotoImage(
            file=ip+'export.gif'), 'resort': PhotoImage(file=ip+'resort.gif')}

        areas = system_data['areas']

        for area, kwargs in areas:
            area(self, **kwargs)

        self.update_data()

    def new(self):
        if self.tk is not None:
            self.tk.destroy()
        self.tk = Tk()
        self.tk.title('vira')
        self.composition = self.root_comp = []
        self.selected = 0
        datamanagement.data = {}
        self.path = None
        self.play = False
        self.time = 1
        self.parts = []
        ip = constants.icon_path
        self.images = {'export': PhotoImage(
            file=ip+'export.gif'), 'resort': PhotoImage(file=ip+'resort.gif')}

        self.update_data(False)

        Preview(self, 'left')
        Composition(self, 'bottom')
        InheritTree(self)
        EditorMenu(self)


class EditorMenu:
    def __init__(self, editor, side='top'):
        self.editor = editor
        self.tk = self.editor.tk
        self.editor.parts.append(self)
        self.editor.system_data['areas'].append(
            [self.__class__, {'side': side}])

        menu = Menu(self.tk)
        menu.add_command(label='New', command=self.new)
        menu.add_command(label='Open', command=self.open)
        menu.add_command(label='Save', command=self.save)
        menu.add_command(label='Save as', command=self.save_as)
        menu.add_command(label='Export', command=self.export)
        win_menu = Menu(menu, tearoff=0)
        win_menu.add_command(label='Preview', command=lambda: Preview(
            self.editor, 'top', *input.Resolution.get().r))
        win_menu.add_command(label='Composition',
                             command=lambda: Composition(self.editor))
        win_menu.add_command(
            label='Tree', command=lambda: InheritTree(self.editor))
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
    def __init__(self, editor, side='top', width=500, height=250):
        self.editor = editor
        self.tk = self.editor.tk
        self.editor.system_data['areas'].append(
            [self.__class__, {'side': side, 'width': width, 'height': height}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.frame = Frame(self.tk)
        self.frame.pack(side=side)
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill='red')
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.pack(side='right')
        self.editor.parts.append(self)
        self.width, self.height = width, height
        self.canvas = Canvas(self.frame, width=self.width,
                             height=self.height+50)
        self.canvas.pack(side='bottom')
        self.canvas.bind('<Button-1>', self.click)

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]

    def click(self, evt):
        if evt.y < self.height:
            return
        if evt.x < 50:
            self.editor.play = not self.editor.play
        elif evt.x < 100:
            self.export()

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
                10, self.height+10, 20, self.height+40, fill='yellow')
            self.canvas.create_rectangle(
                30, self.height+10, 40, self.height+40, fill='yellow')
        else:
            self.canvas.create_polygon(10, self.height+10,
                                       10, self.height+40,
                                       40, self.height+25,
                                       fill='green')
        self.editor.lastRender = time.time()
        self.canvas.create_image(
            50, self.height, anchor='nw', image=self.editor.images['export'])
        d = None
        i = 0
        while len(self.editor.composition) > i:
            d = self.editor.composition[i][0].get(
                self.editor.time-self.editor.composition[i][1], d)
            i += 1
        if d is None:
            return
        img = Image.fromarray(np.uint8(d))
        img = img.resize((self.width, self.height), Image.ANTIALIAS)
        self.canvas.image = ImageTk.PhotoImage(img)
        self.canvas.create_image((0, 0), anchor='nw', image=self.canvas.image)


class Composition:
    def __init__(self, editor, side='top'):
        self.editor = editor
        self.tk = self.editor.tk
        self.frame = Frame(self.tk)
        self.frame.pack(side=side)
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill='red')
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.pack(side='right')
        self.editor.parts.append(self)
        self.editor.system_data['areas'].append(
            [self.__class__, {'side': side}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.canvas = Canvas(self.frame, width=1000, height=525)
        self.canvas.pack(side='bottom')
        self.pos = [0, 0]
        self.scale = 25
        self.selected = 0
        Button(self.frame, text='Add', command=self.add).pack(side='bottom')
        Button(self.frame, text='Go to root composition',
               command=self.root).pack(side='bottom')
        self._initialise_binds()

    def root(self):
        self.editor.composition = self.editor.root_comp

    def _initialise_binds(self):
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Motion>', self._move)
        self.canvas.bind('<ButtonPress-2>', self._startdrag)
        self.canvas.bind('<ButtonRelease-2>', self._stopdrag)
        self.canvas.bind('<ButtonPress-3>', self._startzoom)
        self.canvas.bind('<ButtonRelease-3>', self._stopzoom)
        self._d_moving = False
        self._z_moving = False

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

    def click(self, evt):
        if evt.x > 950:
            if evt.y < 50 and len(self.editor.composition) > self.selected:
                del self.editor.composition[self.selected]
            elif evt.y < 100 and len(self.editor.composition) > self.selected:
                t = self.editor.composition[self.selected]
                del self.editor.composition[self.selected]
                self.selected -= 1
                self.editor.composition.insert(self.selected, t)
            return
        self.selected = (evt.y-self.pos[1])//20
        self.editor.time = (evt.x-self.pos[0])/self.scale

    def add(self):
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
            c.create_rectangle(0, 0, 500, 500, fill='#778')
            categoryId = 0
            for t in types:
                c.create_rectangle(10, pos1+2+categoryId*20,
                                   490, pos1+18+categoryId*20, fill='#777')
                c.create_text(30, pos1+10+categoryId*20, anchor='w', text=t)
                if categoryId == categ:
                    c.create_polygon(15, pos1+10+categoryId*20,
                                     25, pos1+10 + categoryId*20,
                                     20, pos1+15+categoryId*20, fill='black')
                else:
                    c.create_polygon(20, pos1+5+categoryId*20,
                                     20, pos1+15 + categoryId*20,
                                     25, pos1+10+categoryId*20, fill='black')
                categoryId += 1
            # stream types
            c.create_rectangle(500, 0, 1000, 500, fill='#787')
            n = 0
            shown = []
            for t in structure.avaliable:
                if t.category == types[categ]:
                    shown.append(t)
                    c.create_rectangle(510, pos2+2+n*20, 990,
                                       pos2+18+n*20, fill='#777')
                    c.create_text(515, pos2+10+n*20, anchor='w', text=t.Tname)
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
                        del self.editor.composition[self.selected]
                    else:
                        append.args[k] = v.get(
                            composition=self.editor.composition, name=k)
                append.setup()
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
        for i in self.editor.composition:
            self.canvas.create_rectangle(
                0, n*20+self.pos[1], 1000, n*20+20+self.pos[1], fill='black')
            startEnd = i[0].getStartEnd()
            if startEnd is not None:
                self.canvas.create_rectangle(startEnd[0]*self.scale+self.pos[0],
                                             n*20+self.pos[1],
                                             startEnd[1] * self.scale+self.pos[0],
                                             n*20+20+self.pos[1],
                                             fill='green' if self.selected == n else 'yellow')
            self.canvas.create_text(500, n*20+10+self.pos[1],
                                    fill='blue' if self.selected == n else 'lightblue',
                                    text=i[0].get_name())
            self.canvas.create_line(i[1]*self.scale+self.pos[0], n*20+self.pos[1],
                                    i[1]*self.scale+self.pos[0], n*20+20+self.pos[1],
                                    fill='red')
            n += 1
        self.canvas.create_rectangle(0, 500, 1000, 525, fill='white')
        for x in range(10):
            self.canvas.create_line(x*100, 500, x*100, 505, fill='blue')
            self.canvas.create_text(
                x*100, 515,
                text=str((x*100-self.pos[0])/self.scale)[:6])
        self.canvas.create_rectangle(950, 0, 1000, 525, fill='white')
        self.canvas.create_text(
            975, 25, text='X', fill='red', font=('Ariel', 25))
        self.canvas.create_image(
            950, 50, anchor='nw',
            image=self.editor.images['resort'])
        self.editor.selected = self.selected
        self.canvas.create_line(
            self.editor.time*self.scale + self.pos[0], 0,
            self.editor.time*self.scale+self.pos[0], 500,
            fill='green')
        self.canvas.create_rectangle(
            self.editor.time*self.scale+self.pos[0]-50, 500,
            self.editor.time*self.scale+self.pos[0]+50, 520,
            fill='white')

        def rn(n, digits): return round(n, digits-len(str(int(n))))
        self.canvas.create_text(self.editor.time*self.scale+self.pos[0], 510,
                                text=rn(self.editor.time, 7))


class InheritTree:
    def __init__(self, editor, side='bottom'):
        self.editor = editor

        self.tk = self.editor.tk
        self.frame = Frame(self.tk)
        self.frame.pack(side=side)
        self.editor.system_data['areas'].append(
            [self.__class__, {'side': side}])
        self.system_data_self_id = len(self.editor.system_data['areas'])-1
        self.button_close = Canvas(self.frame, width=10, height=10)
        self.button_close.create_rectangle(0, 0, 10, 10, fill='red')
        self.button_close.create_line(0, 0, 10, 10)
        self.button_close.create_line(0, 10, 10, 0)
        self.button_close.bind('<Button-1>', self.close)
        self.button_close.pack(side='right')
        self.editor.parts.append(self)
        self.canvas = Canvas(self.frame, width=1000, height=100)
        self.canvas.pack(side='bottom')
        self.pos = 0
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Button-3>', self.rclick)

    def close(self, evt):
        self.frame.destroy()
        self.editor.parts.remove(self)
        del self.editor.system_data['areas'][self.system_data_self_id]

    def click(self, evt):
        try:
            n = (evt.x-self.pos)//100-1
            if n == -1:
                self.editor.composition[self.editor.selected][0] = self.editor.composition[self.editor.selected][0].args['child']
            item = self.editor.composition[self.editor.selected][0]
            for x in range(n):
                item = item.args['child']
            item.args['child'] = item.args['child'].args['child']
        except IndexError:
            return False
        except KeyError:
            return False

    def rclick(self, evt):
        try:
            n = (evt.x-self.pos)//100
            if n == -1:
                self.editor.composition[self.editor.selected][0] = self.editor.composition[self.editor.selected][0].args['child']
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
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, 1000, 100, fill='#aaf')
        if self.editor.selected >= len(self.editor.composition):
            return
        item = self.editor.composition[self.editor.selected][0]
        i = 0
        while item.is_box():
            self.canvas.create_rectangle(
                self.pos+i*100, 0, self.pos+i*100+100, 100, fill='white')
            self.canvas.create_text(self.pos+i*100+50, 50, text=item.name)
            item = item.args['child']
            i += 1


if __name__ == '__main__':
    e = Editor()
    while True:
        e.update()
