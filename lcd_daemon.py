# pip2 install pyserial
# https://learn.adafruit.com/usb-plus-serial-backpack/command-reference

import ConfigParser
import os
import time
import datetime

import daemon
import pushybullet as pb
import serial


class Pushbullet_LCD():
    def __init__(self):

        self.lcd_columns = 16
        self.lcd_rows    = 2
        # If you aren't using the backpack, you will have to change this. 

        self.ser = serial.Serial('/dev/ttyACM0')

        self.set_color(0.2, 0.5, 1.0) 
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

        # autoscroll off
        self.ser.write(b'\xfe\x52')
        # go home
        self.ser.write(b'\xfe\x48')
        # auto newline off
        self.ser.write(b'\xfe\x44')

    def clear_lcd(self):
        self.ser.write(b'\xfe\x58')

    def msg_lcd(self, message):
        self.ser.write(bytes(message))

    def set_color(self, r, g, b):
        # FIX THIS
        #self.ser.write(b'\xfe\x99')
        self.ser.write(b'\xfe\xd0\x255\x255\x255')
        
    def write_message_buffer(self):
        print(self.lcd_buffer)
        self.clear_lcd()
        self.msg_lcd('\n'.join(self.lcd_buffer))

   
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
                self.clear_lcd()



    def update_pushes(self):
        self.set_message('updating...')
        self.pushes = []
        
        try:
            for push in self.api.pushes():
                self.pushes.append(push)

        except Exception as e:
            self.set_message(e)


        
    def set_message(self, message):
        self.clear_lcd()
        self.msg_lcd(message)


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

                self.lcd_buffer[1] = str(datetime.datetime.fromtimestamp(push.created))[0:self.lcd_columns]
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

