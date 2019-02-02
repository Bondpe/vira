from tkinter import Canvas, Tk
class Window:
    'basic window class'
    def __init__(self, width=1000, height=1000, fill='#fff'):
        self.tk = Tk()
        self.canvas = Canvas(self.tk, width=width, height=height)
        self.canvas.pack()
        self.width, self.height = width, height
        self.fill = fill
        #shapes
        self.shapes = []
        #menus
        self.menus = []
        # mouse
        self.mouse = 0, 0
        self.canvas.bind_all('<Motion>', self._move)
        self.canvas.bind_all('<ButtonPress-1>', self._click)
    def _move(self, evt):
        'mouse motion reactor'
        self.mouse = evt.x, evt.y
    def _click(self, evt):
        for shape, data, display in self.shapes:
            if display == True and shape == 'clicker':
                x1, y1, x2, y2, function = data
                if function == None or evt.x < x1 or evt.x > x2 or evt.y < y1 or evt.y > y2:
                    continue
                function()
            if display == True and shape == 'button':
                x1, y1, x2, y2, function, text = data
                if function != None and self.mouse[0] < x2 and self.mouse[0] > x1 and self.mouse[1] < y2 and self.mouse[1] > y1:
                    function()
    #  ~~  ~~    ~~  ~~  ~~  ~~  ~~  ~~  different shape objects
    def create_rectangle(self, x1, y1, x2, y2, fill='#000'):
        'create rectangle; returns shapeId'
        self.shapes.append(['rectangle', [x1, y1, x2, y2, fill], True])
        return len(self.shapes)-1
    def create_oval(self, x1, y1, x2, y2, fill='#000'):
        'create oval; returns shapeId'
        self.shapes.append(['oval', [x1, y1, x2, y2, fill], True])
        return len(self.shapes)-1
    def create_text(self, x, y, text, font='Ariel', size=25, fill='#000'):
        'create text; returns shapeId'
        self.shapes.append(['text', [x, y, text, (font, size), fill], True])
        return len(self.shapes)-1
    def create_clicker(self, x1, y1, x2, y2, function=None):
        'create area for clicking; returns shapeId'
        self.shapes.append(['clicker', [x1, y1, x2, y2, function], True])
        return len(self.shapes)-1
    def create_button(self, x1, y1, x2, y2, function=None, text=''):
        'create button; returns shapeId'
        self.shapes.append(['button', [x1, y1, x2, y2, function, text], True])
        return len(self.shapes)-1
    #  ~~  ~~    ~~  ~~  ~~  ~~  ~~  ~~  shape at all
    def del_object(self, shapeId):
        'deletes shape'
        self.shapes[shapeId][-1] = False
    def change_object(self, shapeId, data):
        'changes shape data'
        self.shapes[shapeId][1] = data
    def rec_object(self, shapeId):
        'recovers shape'
        self.shapes[shapeId][-1] = True
    #  ~~  ~~    ~~  ~~  ~~  ~~  ~~  ~~  end of shapes
    #  ~~  ~~    ~~  ~~  ~~  ~~  ~~  ~~  more complex structures
    def create_down_menu(self, x1, y1, x2, y2, text, names, functions):
        ids = []
        for n in range(len(names)):
            ids.append(self.create_button(x1, y2+n*25, x1+100, y2+n*25+25, functions[n], names[n]))
            self.del_object(ids[-1])
        def hide():
            for ID in ids:
                self.del_object(ID)
        self.create_clicker(0, 0, self.width, self.height, hide)
        def show():
            for ID in ids:
                self.rec_object(ID)
        self.create_button(x1, y1, x2, y2, show, text)
    def update(self):
        #updating
        self.canvas.update()
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.fill)
        #drawing
        for shape, data, display in self.shapes:
            if display:
                if shape == 'rectangle':
                    x1, y1, x2, y2, fill = data
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
                elif shape == 'oval':
                    x1, y1, x2, y2, fill = data
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fill)
                elif shape == 'text':
                    x, y, text, font, fill = data
                    self.canvas.create_text(x, y, fill=fill, font=font, text=text)
                elif shape == 'button':
                    x1, y1, x2, y2, function, text = data
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='#eee')
                    if self.mouse[0] < x2 and self.mouse[0] > x1 and self.mouse[1] < y2 and self.mouse[1] > y1:
                        self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill='#ccc', outline='#ccc')
                    else:
                        self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill='#ddd', outline='#ddd')
                    self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text)
