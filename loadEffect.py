from PIL import Image
import effects
import numpy as np
versions = ['0.0.1', '0.0.2']
alphabet = 'abcdefghijklmnopqrstuvwxyz'


class Loaded(effects.Effect):
    def __init__(self, stream=1, start=0, duration=-1, **kwargs):
        effects.Effect.__init__(self, stream=1, start=0, duration=-1, **kwargs)
        self.path = self.filedialog.Open(self.editor.tk).show()
        self.text = open(self.path).read()
        self.commands = self.text.split('\n')
        if not self.commands[0].startswith('#viraeffect:'):
            raise ImportError("Can't import effect, maybe check for vira update or select another file")
        supported_version = False
        for version in versions:
            if self.commands[0].endswith(version):
                supported_version = True
        if not supported_version:
            raise ImportError("Can't import effect, maybe check for vira update or select another file")
        self.head = self.commands[1].split('\\')[1:]
        self.name = self.head[0]
        self.className = ''
        for char in range(len(self.head[0])):
            if not self.head[0][char] in alphabet and \
               not self.head[0][char] in alphabet.upper():
                self.className += '_'
            else:
                self.className += self.head[0][char]
        self.__class__.__name__ = self.className
        self.__doc__ = self.head[1]
        vals = self.commands[2]
        if not vals.startswith('var '):
            raise ValueError("Can't find vars")
        vals = vals[4:]
        vals = vals.split(',')
        self.vals = []
        self.vt = []
        for val in vals:
            typeName,name = val.split(':')
            self.vals.append(name)
            self.vt.append(typeName)
            for char in name:
                if not char in alphabet and char != '_':
                    raise SyntaxError('unsupported character "%s" in value name'%char)
        self.exec = self.commands[3:]
    def modify_image(self, path, frame):
        if self.exec[0] == '|all|':
            ImageArray = np.asarray(Image.open(path).convert('RGB'))
            for x in range(len(self.exec)):
                if self.exec[x] == '|/all|':
                    end = x
            variables = {}
            cond = True
            for command in self.exec[1:end]:
                if command.startswith('    ') and cond:
                    command = command[4:]
                if command[0] == '#':
                    pass
                elif command[0] == '[':
                    val1 = ''
                    val2 = ''
                    crossed = False
                    operation = ''
                    for char in command[1:-1]:
                        if char in alphabet or char in alphabet.upper() or char in '1234567890_':
                            if crossed:
                                val2 += char
                            else:
                                val1 += char
                        else:
                            operation += char
                            crossed = True
                    try:
                        val1 = float(val1)
                    except:
                        if val1 in self.data:
                            val1 = self.data[val1]
                        elif val1 == 'FRAME':
                            val1 = frame
                        else:
                            val1 = variables[val1]
                    try:
                        val2 = float(val2)
                    except:
                        if val2 in self.data:
                            val2 = self.data[val2]
                        elif val2 == 'FRAME':
                            val2 = frame
                        else:
                            val2 = variables[val2]
                    if operation == '<':
                        if val1 < val2:
                            cond = True
                        else:
                            cond = False
                    if operation == '>':
                        if val1 > val2:
                            cond = True
                        else:
                            cond = False
                    if operation == '=':
                        if val1 == val2:
                            cond = True
                        else:
                            cond = False
                    if operation == '>=':
                        if val1 >= val2:
                            cond = True
                        else:
                            cond = False
                    if operation == '<=':
                        if val1 <= val2:
                            cond = True
                        else:
                            cond = False
                elif command[0] == '>':
                    expr = command[1:]
                    try:
                        expr = float(expr)
                    except:
                        if expr in self.data:
                            expr = self.data[expr]
                        elif expr == 'FRAME':
                            expr = frame
                        else:
                            expr = variables[expr]
                    print(expr)
                elif command[0] == ' ':
                    pass
                else:
                    valname, expr = command.split('=')
                    if valname.startswith('PIXELS'):
                        try:
                            expr = float(expr)
                        except:
                            if expr in self.data:
                                expr = self.data[expr]
                            else:
                                expr = variables[expr]
                        if valname[-1] == '*':
                            ImageArray = ImageArray*expr
                        if valname[-1] == '/':
                            ImageArray = ImageArray/expr
                        if valname[-2:-1] == '**':
                            ImageArray = ImageArray**expr
                    else:
                        for char in valname:
                            if not char in alphabet and char != '_':
                                SyntaxError('unsupported character "%s" in value name "%s"'%(char, valname))
                        val1 = ''
                        val2 = ''
                        crossed = False
                        operation = ''
                        for char in expr:
                            if char in alphabet or char in alphabet.upper() or char in '1234567890_':
                                if crossed:
                                    val2 += char
                                else:
                                    val1 += char
                            else:
                                operation += char
                                crossed = True
                        try:
                            val1 = float(val1)
                        except:
                            if val1 in self.data:
                                val1 = self.data[val1]
                            elif val1 == 'FRAME':
                                val1 = frame
                            else:
                                val1 = variables[val1]
                        try:
                            val2 = float(val2)
                        except:
                            if val2 in self.data:
                                val2 = self.data[val2]
                            elif val2 == 'FRAME':
                                val2 = frame
                            else:
                                val2 = variables[val2]
                        if operation == '+':
                            variables[valname] = val1+val2
                        if operation == '-':
                            variables[valname] = val1-val2
                        if operation == '*':
                            variables[valname] = val1*val2
                        if operation == '/':
                            variables[valname] = val1/val2
                        if operation == '**':
                            variables[valname] = val1**val2
                        if operation == '^':
                            variables[valname] = val1**val2
                        if operation == '%':
                            variables[valname] = val1%val2
            im = Image.fromarray(np.uint8(ImageArray))
            im.save(path)
        if self.exec[0] == '|RGB|':
            image = Image.open(path).convert('RGB')
            x_size, y_size = image.size
            RGB = image.load()
            for x in range(len(self.exec)):
                if self.exec[x] == '|/RGB|':
                    end = x
            for pixel_x in range(x_size):
                for pixel_y in range(y_size):
                    variables = {'X':pixel_x,'Y':pixel_y,'R':RGB[pixel_x,pixel_y][0],'G':RGB[pixel_x,pixel_y][1],'B':RGB[pixel_x,pixel_y][2]}
                    cond = True
                    for command in self.exec[1:end]:
                        if command.startswith('    ') and cond:
                            command = command[4:]
                        if command[0] == '#':
                            pass
                        elif command[0] == '[':
                            val1 = ''
                            val2 = ''
                            crossed = False
                            operation = ''
                            for char in command[1:-1]:
                                if char in alphabet or char in alphabet.upper() or char in '1234567890_':
                                    if crossed:
                                        val2 += char
                                    else:
                                        val1 += char
                                else:
                                    operation += char
                                    crossed = True
                            try:
                                val1 = float(val1)
                            except:
                                if val1 in self.data:
                                    val1 = self.data[val1]
                                elif val1 == 'FRAME':
                                    val1 = frame
                                else:
                                    val1 = variables[val1]
                            try:
                                val2 = float(val2)
                            except:
                                if val2 in self.data:
                                    val2 = self.data[val2]
                                elif val2 == 'FRAME':
                                    val2 = frame
                                else:
                                    val2 = variables[val2]
                            if operation == '<':
                                if val1 < val2:
                                    cond = True
                                else:
                                    cond = False
                            if operation == '>':
                                if val1 > val2:
                                    cond = True
                                else:
                                    cond = False
                            if operation == '=':
                                if val1 == val2:
                                    cond = True
                                else:
                                    cond = False
                            if operation == '>=':
                                if val1 >= val2:
                                    cond = True
                                else:
                                    cond = False
                            if operation == '<=':
                                if val1 <= val2:
                                    cond = True
                                else:
                                    cond = False
                        elif command[0] == '>':
                            expr = command[1:]
                            try:
                                expr = float(expr)
                            except:
                                if expr in self.data:
                                    expr = self.data[expr]
                                elif expr == 'FRAME':
                                    expr = frame
                                elif expr in variables:
                                    expr = variables[expr]
                            print(expr)
                        elif command[0] == ' ':
                            pass
                        else:
                            valname, expr = command.split('=')
                            for char in valname:
                                if not char in alphabet and char != '_':
                                    SyntaxError('unsupported character "%s" in value name "%s"'%(char, valname))
                            val1 = ''
                            val2 = ''
                            crossed = False
                            operation = ''
                            for char in expr:
                                if char in alphabet or char in alphabet.upper() or char in '1234567890_':
                                    if crossed:
                                        val2 += char
                                    else:
                                        val1 += char
                                else:
                                    operation += char
                                    crossed = True
                            try:
                                val1 = float(val1)
                            except:
                                if val1 in self.data:
                                    val1 = self.data[val1]
                                elif val1 == 'FRAME':
                                    val1 = frame
                                else:
                                    val1 = variables[val1]
                            try:
                                val2 = float(val2)
                            except:
                                if val2 in self.data:
                                    val2 = self.data[val2]
                                elif val2 == 'FRAME':
                                    val2 = frame
                                else:
                                    val2 = variables[val2]
                            if operation == '+':
                                variables[valname] = val1+val2
                            if operation == '-':
                                variables[valname] = val1-val2
                            if operation == '*':
                                variables[valname] = val1*val2
                            if operation == '/':
                                variables[valname] = val1/val2
                            if operation == '**':
                                variables[valname] = val1**val2
                            if operation == '^':
                                variables[valname] = val1**val2
                            if operation == '%':
                                variables[valname] = val1%val2
                    RGB[pixel_x,pixel_y] = (int(variables['R']),int(variables['G']),int(variables['B']))
            image.save(path)

def main(effectsI, editor, dialog):
    effectsI.supported_effects['load'] = Loaded
    effectsI.supported_effects['load'].editor = editor
    effectsI.supported_effects['load'].filedialog = dialog
    effectsI.names.append('load')
