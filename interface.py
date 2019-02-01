#!/usr/env/python3
from tkinter import filedialog, simpledialog
#-------------------------------------------------------------------------------------------------Create window
from window import Window
editor = Window(1400, 800)
import interfaceBase as If

#-------------------------------------------------------------------------------------------------Initialise functions
#============================ File
def newVideo():
    print('new file dialog')
def openVideo():
    print('open file dialog')
def saveVideo():
    print('save file function')
def saveAsVideo():
    print('save file dialog')
editor.create_down_menu(0, 0, 30, 15, 'File', ['New', 'Open', 'Save', 'Save as'], [newVideo, openVideo, saveVideo, saveAsVideo])
#============================ Edit
def Add():
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    If.videos.append(If.Video(path))
    return
def export():
    path = filedialog.SaveAs(editor.tk).show()
    If.export(path)
def pack():
    print('packing...')
editor.create_down_menu(30, 0, 60, 15, 'Edit', ['Add', 'Export', 'Pack'], [Add, export, pack])
#============================ Stream
def change_s():
    stream = simpledialog.askinteger("Change stream data (start)", "stream #:", initialvalue=1)-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger("Change stream data (start)", "stream starts playing from environment frame\n(%s):"%If.videos[stream].path, initialvalue=0)-1
    If.videos[stream].start = start
def change_f():
    stream = simpledialog.askinteger("Change stream data (start)", "stream #:", initialvalue=1)-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger("Change stream data (start)", "stream start at self-frame\n(%s):"%If.videos[stream].path, initialvalue=0)-1
    If.videos[stream].fromF = start
editor.create_down_menu(60, 0, 110, 15, 'Stream', ['Change start', 'Cut start', 'Cut duration'], [change_s, change_f, pack])
while True:
    n = 0
    for video in If.videos:
        editor.canvas.create_rectangle(200, 600+n, 1200, 620+n, fill='#ddd')
        editor.canvas.create_rectangle(200+video.start-video.fromF, 600+n, 200+video.start-video.fromF+video.durationF, 620+n, fill='#ffa')
        editor.canvas.create_rectangle(200+video.start, 600+n, 200+video.start-video.fromF+video.durationF, 620+n, fill='#aaf')
        editor.canvas.create_text(200+video.start-video.fromF+video.durationF//2, 610+n, text=video.path, font=('Ariel', 5))
        editor.canvas.create_text(180, 610+n, text='#'+str(n//20+1), font=('Ariel', 10))
        n += 20
    del n
    editor.update()
