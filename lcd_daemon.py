import ConfigParser
import os
import time
import datetime

import daemon
import pushybullet as pb
import Adafruit_CharLCD as LCD



class Pushbullet_LCD():
    def __init__(self):

        self.lcd_columns = 16
        self.lcd_rows    = 2
        self.lcd         = LCD.Adafruit_RGBCharLCD(27, 22, 25, 24, 23, 18, 
                                               self.lcd_columns, self.lcd_rows, 4, 17, 7)


        

        self.lcd.set_color(0.2, 0.5, 1.0) 
        self.lcd_buffer = [ ' '* self.lcd_columns  ] * self.lcd_rows


        self.scroll_speed = .5

        self.pushes = []


        self.config = ConfigParser.ConfigParser()
        self.config_paths = ['%s/config' % (os.getcwd())]

        for path in self.config_paths:
            if os.path.exists(path):
                self.config.read(path)

        self.update_interval = float(self.config.get('settings', 'update_interval'))
        self.pause_interval  = float(self.config.get('settings', 'pause_interval'))
        self.update_time     = None
        self.api_key         = self.config.get('settings', 'api_key')
        self.api             = pb.PushBullet(self.api_key)


    def write_message_buffer(self):
        self.lcd.clear()
        self.lcd.message('\n'.join(self.lcd_buffer))

   
    def scroll_buffer(self, message, row):
        front = 0
        end   = self.lcd_columns



        if len(message) <= self.lcd_columns:
            self.lcd_buffer[row] = message
            self.write_message_buffer()
            time.sleep(10)


        else:
            for i in range(len(message)):
                self.lcd_buffer[row] = message[front:end]
                self.write_message_buffer()
                if front == 0:
                    # Pause so I can read the first part
                    time.sleep(self.pause_interval)

                time.sleep(self.scroll_speed)
                front += 1
                end   += 1
                self.lcd.clear()

      


    def update_pushes(self):
        self.set_message('updating...')

        # Delete previous messages
        self.pushes = []

        # Cache the messages
        for push in self.api.pushes():

            self.pushes.append(push)


        
    def set_message(self, message):
        self.lcd.clear()
        self.lcd.message(message)


    def set_update_time(self):
        self.update_time = datetime.datetime.now() + datetime.timedelta(0, self.update_interval)


    def display_messages(self):
        self.set_update_time()

        while True:

            if len(self.pushes) == 0:
                self.set_message('No pushes')
                time.sleep(self.update_interval)

            for push in self.pushes:
                if push.body == '':
                    continue

                self.lcd_buffer[1] = str(datetime.datetime.fromtimestamp(push.created))
                self.scroll_buffer(push.body, row=0)

                time.sleep(self.pause_interval)


            now = datetime.datetime.now()

            if now >= self.update_time:
                self.update_pushes()
                self.set_update_time()

if __name__ == "__main__":
    pb_lcd = Pushbullet_LCD()
    pb_lcd.update_pushes()
    pb_lcd.display_messages()

