import os
os.system('mkdir /tmp/vira')
class Data:
    pass
data = Data()
data.amount = 0
class Video:
    def __init__(self,path,name=None):
        self.path = path
        if name == None:
            self.name = str(data.amount)
            data.amount += 1
        else:
            self.name = name
        os.system('mkdir /tmp/vira/%s'%self.name)
        with open('/tmp/vira/%s/audio.aac'%self.name, 'w') as file:
            file.write('')
            file.close()
        os.system('ffmpeg -r 25 -i %s /tmp/vira/%s/frame%%d.png'%(self.path,self.name))
        num = 0
        while True:
            num += 1
            try:
                open('/tmp/vira/%s/frame%d.png'%(self.name, num))
            except:
                self.len = num
                break
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
