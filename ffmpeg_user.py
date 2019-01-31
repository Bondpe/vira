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
        os.system('ffmpeg -r 25 -i /tmp/vira/%s/frame%%d.png %s'%(self.name, file))
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
    #1, 10 - 5
    def __sub__(self, frames):
        new = Empty()
        for frame in range(self.len-frames):
            os.system('cp /tmp/vira/%s/frame%d.png /tmp/vira/%s/frame%d.png'%(self.name, frame+frames+1, new.name, frame+1))
            new.len += 1
        return new
    def __imul__(self, times):
        OLen = self.len-1
        for x in range(times-1):
            for num in range(OLen):
                frame = open('/tmp/vira/%s/frame%d.png'%(self.name,num+1),'rb').read()
                file = open('/tmp/vira/%s/frame%d.png'%(self.name, self.len), 'wb')
                file.write(frame)
                file.close()
                self.len += 1
        return self
    def __truediv__(self, times):
        v = Empty()
        done = times
        n = 0
        while done <= self.len-1:
            n += 1
            os.system('cp /tmp/vira/%s/frame%d.png /tmp/vira/%d/frame%d.png'%(self.name, int(done)+1, data.amount-1, n))
            done += times
        v.len = int((self.len-1) / times)+1
        return v
    def rm(self):
        os.system('rm -r /tmp/vira/%s'%self.name)
        self.len = 0
        self.name = ''
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

class Frame(Empty):
    def __init__(self,path,name=None):
        Empty.__init__(self,name)
        self.path = path
        os.system('cp %s /tmp/vira/%s/frame1.png'%(self.path,self.name))
        self.len = 2
