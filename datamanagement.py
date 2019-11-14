from tkinter import *
from tkinter import filedialog
import constants

data = {}

class File:
    def __init__(self, path, nameb=None):
        self.path = path
        if nameb is None:
            nameb = self.path.split('/')[-1]
        i = 0
        name = nameb
        while name in data:
            name = nameb+'.'+str(i)
            i += 1
        self.name = name
        data[name] = self
    def pack(self):
        return [open(self.path, 'rb').read(), self.name]

class Load:
    def __init__(self, d):
        self.path = constants.get_temp_path()
        f = open(self.path, 'wb')
        f.write(d[0])
        f.close()
        self.name = d[1]
        data[self.name] = self
    def pack(self):
        return [open(self.path, 'rb').read(), self.name]

def pack_data():
    out = {}
    for d in data:
        out[d] = data[d].pack()
    return out

def load_data(out):
    global data
    data = {}
    for d in out:
        data[d] = Load(out[d])

class Name:
    def __init__(self, name):
        self.name = name
    def get(*args, **kwargs):
        tk = Tk()
        tk.title('choose name')
        canvas = Canvas(tk, width=500, height=len(data)*30+30)
        canvas.pack()
        names = list(data.keys())
        i = 0
        for n in names:
            canvas.create_text(250, i*30+15, text=n)
            i += 1
        canvas.create_text(250, len(data)*30+15, text='new', fill='green')
        name = None
        def end(evt):
            nonlocal name
            if evt.y < len(data)*30:
                name = names[evt.y//30]
            else:
                name = File(filedialog.Open(tk).show()).name
            tk.destroy()
        canvas.bind('<Button-1>', end)
        while True:
            try:
                tk.update()
            except:
                return Name(name)
    def data(self):
        return data[self.name]
    def __str__(self):
        return 'File(%s)'%repr(self.name)
