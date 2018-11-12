import os
os.system('mkdir /tmp/vira')
class Data:
    pass
data = Data()
data.amount = 0
class Empty:
    def __init__(self,name=None):
        self.name = str(data.amount)
        if name == None:
            self.str = str(data.amount)
        else:
            self.str = name
        data.amount += 1
        os.system('mkdir /tmp/vira/%s'%self.name)
        self.len = 1
    def export(self, file='out.mp4'):
        os.system('ffmpeg -i /tmp/vira/%s/frame%%d.png %s'%(self.name, file))
    def __iadd__(self,video):
        for num in range(video.len-1):
            frame = open('/tmp/vira/%s/frame%d.png'%(video.name,num+1),'rb').read()
            file = open('/tmp/vira/%s/frame%d.png'%(self.name, self.len), 'wb')
            file.write(frame)
            file.close()
            self.len += 1
        return self
    def __isub__(self, frames):
        for frame in range(frames):
            os.system('rm /tmp/vira/%s/frame%d.png'%(self.name, self.len-1))
            self.len -= 1
        return self
    def __imul__(self, times):
        for x in range(times-2):
            self += self
        return self
class Video(Empty):
    def __init__(self,path,name=None):
        Empty.__init__(self,name)
        self.path = path
        os.system('ffmpeg -r 25 -i %s /tmp/vira/%s/frame%%d.png'%(self.path,self.name))
        num = 0
        while True:
            num += 1
            try:
                open('/tmp/vira/%s/frame%d.png'%(self.name, num))
            except:
                self.len = num
                break
