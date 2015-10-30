import daemon
import pushybullet as pb




class Pushbullet_LCD():
    def __init__(self):
        self.api_key = ''
        self.api     = pb.PushBullet(self.api_key)



    
    def get_pushes(self):
        all_pushes = self.api.pushes()
        
        for push in all_pushes:
            print(push.body)
            
            


if __name__ == '__main__':
    pb_lcd = Pushbullet_LCD()
    pb_lcd.get_pushes()

#with daemon.DaemonContext():


