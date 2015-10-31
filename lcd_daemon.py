import daemon
import time
import pushybullet as pb
import Adafruit_CharLCD as LCD


class Pushbullet_LCD():
    def __init__(self):
        self.api_key = 'YOUR_KEY'
        self.api     = pb.PushBullet(self.api_key)

        self.lcd_columns = 16
        self.lcd_rows    = 2
        self.lcd         = LCD.Adafruit_RGBCharLCD(27, 22, 25, 24, 23, 18, 
                                               self.lcd_columns, self.lcd_rows, 4, 17, 7)


        

        self.lcd.set_color(0.2, 0.5, 1.0) 
        self.msg_buffer = [ ' '* self.lcd_columns  ] * self.lcd_rows
        self.scroll_speed = .5

        self.messages = []


   
    def scroll_message(self, message):
        front = 0
        end   = 16

        self.lcd.clear()

        if len(message) <= 16:
            self.msg_buffer[0] = message
            self.lcd.message(self.msg_buffer[0])
            time.sleep(10)


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
        self.set_message('updating...')

        self.messages = []

        # Cache the messages
        for push in self.api.pushes():
            self.messages.append(push.body)


        
    def set_message(self, message):
        self.lcd.clear()
        self.lcd.message(message)

if __name__ == "__main__":
    update_seconds = 120
    pb_lcd = Pushbullet_LCD()
    pb_lcd.update_pushes()

    start_time = time.time()
    
    while True:
        count = 0


        if len(pb_lcd.messages) == 0:
            pb_lcd.set_message('No pushes')
            time.sleep(update_seconds)

        for message in pb_lcd.messages:
            if message == '':
                continue

            pb_lcd.scroll_message(message)
            time.sleep(5)
            count += 1


        now = time.time()
        if now - start_time >= update_seconds:
            pb_lcd.update_pushes()
            start_time = now

        print('end loop') 

