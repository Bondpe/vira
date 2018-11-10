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
        os.system(‘mkdir /tmp/vira/%s’%self.name)
        os.system(‘ffmpeg -i %s /tmp/vira/%s/frame%%d.png /tmp/%s/audio.aac’%(self.path,self.name,self.name))
        num = 0
        while True:
            num += 1
            try:
                open('/tmp/vira/%s/frame%d.png'%num)
            except:
                self.len = num
                break
    def _iadd_(self,video):
        for num in range(video.len):
            frame = open('/tmp/vira/%s/frame%d.png'%(video.name,num),'rb').read()
            self.len += 1
            file = open('/tmp/vira/%s/frame%d.png'%(self.name, self.len), 'wb')
            file.write(frame)
            file.close()
            




