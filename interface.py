#!/usr/env/python3
from tkinter import filedialog, simpledialog, PhotoImage
from PIL import Image, ImageTk
#-------------------------------------------------------------------------------------------------Create window
from window import Window
editor = Window(1400, 800, '#000')
import interfaceBase as If
import os, sys
#-------------------------------------------------------------------------------------------------Initialise functions
#============================ File
projectPath = None
def newVideo():
    global projectPath
    If.new()
    projectPath = None
def openVideo():
    global projectPath
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    If.openF(path)
    projectPath = path
def saveAsVideo():
    global projectPath
    path = filedialog.SaveAs(editor.tk).show()
    If.save(path)
    projectPath = path
def saveVideo():
    global projectPath
    if projectPath == None:
        saveAsVideo()
    else:
        If.save(projectPath)
def exq():
    editor.tk.destroy()
    sys.exit()
editor.create_down_menu(0, 0, 30, 15, 'File', ['New', 'Open', 'Save', 'Save as', 'Quit'], [newVideo, openVideo, saveVideo, saveAsVideo, exq])
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
    path = filedialog.SaveAs(editor.tk).show()
    If.pack(path)
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
def change_d():
    stream = simpledialog.askinteger("Change stream data (start)", "stream #:", initialvalue=1)-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger("Change stream data (start)", "streams last frame\n(%s):"%If.videos[stream].path, initialvalue=0)-1
    If.videos[stream].durationF = start+If.videos[stream].start
editor.create_down_menu(60, 0, 110, 15, 'Stream', ['Change start', 'Cut start', 'Cut duration'], [change_s, change_f, change_d])
#########################################preview
previewImage = None
previewFrame = 0
oldPreviewFe = 0
streamerScale=1
streamerPos=0
def newPreview():
    global previewFrame, streamerScale
    previewFrame = (editor.mouse[0]-200)/streamerScale
editor.create_clicker(200, 600, 1200, 780, newPreview)
#########################################streams
#scale
def newScale():
    global streamerScale
    streamerScale = simpledialog.askinteger("Streamer", "New scale (%)")/100
editor.create_clicker(160, 780, 200, 800, newScale)
#pos
def newPos():
    global streamerPos
    streamerPos = simpledialog.askinteger("Streamer", "New segment")*8-8
editor.create_clicker(200, 780, 240, 800, newPos)
while True:
    editor.canvas.create_rectangle(200, 600, 1200, 800, fill='#eee')
    editor.canvas.create_rectangle(160, 600, 200, 800, fill='#aaa')
    p,n = 0,0
    for video in If.videos:
        n = p-streamerPos*20
        if n >= 0:
            editor.canvas.create_rectangle(200, 600+n, 1200, 620+n, fill='#ddd')
            editor.canvas.create_rectangle(200+(video.start-video.fromF)*streamerScale, 600+n, 200+(video.start-video.fromF+video.len)*streamerScale, 620+n, fill='#ffa')
            editor.canvas.create_rectangle(200+(video.start)*streamerScale, 600+n, 200+(video.start-video.fromF+video.durationF)*streamerScale, 620+n, fill='#aaf')
            editor.canvas.create_text(700, 610+n, text=video.path, font=('Ariel', 5))
            editor.canvas.create_rectangle(160, 600+n, 200, 620+n, fill='#aaa')
            editor.canvas.create_text(180, 610+n, text='#'+str(p//20+1), font=('Ariel', 10))
        p += 20
        if n > 140:
            break
    del n, p
    editor.canvas.create_text(180, 790, text='scale:%d%%'%(streamerScale*100), font=('Ariel', 5))
    editor.canvas.create_rectangle(200, 780, 240, 800, fill='#aaa')
    editor.canvas.create_text(220, 790, text='segm:%d'%(streamerPos//8+1), font=('Ariel', 5))
    if oldPreviewFe != previewFrame:
        if If.preview(previewFrame):
            img = Image.open('/tmp/vira/prew.gif')
            img = img.resize((1000, 500), Image.ANTIALIAS)
            editor.tk.image = previewImage = ImageTk.PhotoImage(img)
            del img
            oldPreviewFe = previewFrame
        else:
            previewImage = None
    if previewImage:
        editor.canvas.create_image((200, 100), anchor='nw', image=previewImage)
    else:
        editor.canvas.create_rectangle(200, 100, 1200, 600, fill='#aaa')
    editor.canvas.create_line(previewFrame*streamerScale+200, 600, previewFrame*streamerScale+200, 780, fill='red')
    editor.update()
