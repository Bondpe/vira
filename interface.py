#!/usr/env/python3
from tkinter import filedialog
#-------------------------------------------------------------------------------------------------Create window
from window import Window
editor = Window()
#-------------------------------------------------------------------------------------------------Video in editor has extra data and is different
class Video:
    def __init__(self, path, start=0, fromF=0, durationF=0):
        self.path = path
        self.start = start
        self.fromF = fromF
        self.len = durationF
videos = []

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
#============================ Edit
def Add():
    path = filedialog.Open(editor.tk).show()
    if path == ():
        return
    videos.append(Video(path))
    return
def export():
    print('exporting...')
def pack():
    print('packing...')
editor.create_down_menu(0, 0, 30, 15, 'File', ['New', 'Open', 'Save', 'Save as'], [newVideo, openVideo, saveVideo, saveAsVideo])
editor.create_down_menu(30, 0, 60, 15, 'Edit', ['Add', 'Export', 'Pack'], [Add, export, pack])
while True:
    editor.update()
