import os
amount = 0
class Video:
    def __init__(self,path,name=None):
        self.path = path
        if name == None:
            self.name = str(amount)
            amount += 1
        else:
            self.name = name
        os.system(‘mkdir /tmp/%s’%self.name)
        os.system(‘ffmpeg -i %s /tmp/%s/frame%%d.gif /tmp/%s/audio.aac’%(self.path,self.name,self.name))


