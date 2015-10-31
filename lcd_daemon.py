import daemon
import time
import pushybullet as pb
import Adafruit_CharLCD as LCD


class Pushbullet_LCD():
    def __init__(self):
        self.api_key = ''
        self.api     = pb.PushBullet(self.api_key)

        self.lcd_columns = 16
        self.lcd_rows    = 2
        self.lcd         = LCD.Adafruit_RGBCharLCD(27, 22, 25, 24, 23, 18, 
                                               self.lcd_columns, self.lcd_rows, 4, 17, 7)


        

        self.lcd.set_color(0.2, 0.5, 1.0) 
        self.msg_buffer = [ ' '* self.lcd_columns  ] * self.lcd_rows
        self.scroll_speed = .5

        self.all_pushes = None


   
    def scroll_message(self, message):
        front = 0
        end   = 16

        self.lcd.clear()

        if len(message) <= 16:
            self.msg_buffer[0] = message
            self.lcd.message(self.msg_buffer[0])


        else:
            for i in range(len(message)):
                self.msg_buffer[0] = message[front:end]
                print(self.msg_buffer)
                self.lcd.message(self.msg_buffer[0])
                time.sleep(self.scroll_speed)
                front += 1
                end   += 1
                self.lcd.clear()

       

    def update_pushes(self):
        self.all_pushes = self.api.pushes()
        



with daemon.DaemonContext():
    pb_lcd = Pushbullet_LCD()
    pb_lcd.update_pushes()

    start_time = time.time()
    
    while True:
        for message in pb_lcd.all_pushes:
            pb_lcd.scroll_message(message.body)
            time.sleep(5)

        now = time.time()

        if now - start_time <= 120:
            pb_lcd.update_pushes()
            start_time = now

    

