# pip2 install pyserial
# https://learn.adafruit.com/usb-plus-serial-backpack/command-reference

import ConfigParser
import os
import time
import datetime
import logging

import pushybullet as pb
import serial


class Pushbullet_LCD():
    def __init__(self):
        self.lcd_columns = 16
        self.lcd_rows    = 2


        self.lcd_buffer = [ ' '* self.lcd_columns  ] * self.lcd_rows


        self.scroll_speed = .5

        self.pushes = []
        self.did_update = False


        self.config = ConfigParser.ConfigParser()
        self.config_paths = ['%s/config' % (os.getcwd())]

        for path in self.config_paths:
            if os.path.exists(path):
                self.config.read(path)

        self.ser = serial.Serial(self.config.get('settings', 'device'))
        logging.basicConfig(filename=self.config.get('settings', 'log_path'), level=logging.DEBUG)
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
        
        self.set_color(0.2, 0.5, 1.0) 


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

        # If the message is short enough to display w/o scrolling
        if len(message) <= self.lcd_columns:
            self.lcd_buffer[row] = message
            self.write_message_buffer()
            time.sleep(10)

        # Otherwise scroll it
        else:
            for i in range(len(message)):
                
                if len(message[front:end]) < self.lcd_columns:
                    # ljust uses the length of the string, so you have to add it back 
                    # ie, x = '123'.ljust(5) will return '123  ' instead of '123     '
                    diff = (self.lcd_columns - len(self.lcd_buffer[row])) + self.lcd_columns
                    self.lcd_buffer[row] = message[front:end].ljust(diff)

                else:
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
        logging.debug('updating pushes')
        self.set_message('updating...')
        self.pushes = []
        
        try:
            for push in self.api.pushes():
                print(push)
                self.pushes.append(push)

        except Exception as e:
            logging.warning('exception: %s' % (e))
            self.set_message('%s' % (e))
            time.sleep(self.pause_interval)

            return False

        logging.debug('%s pushes' % (len(self.pushes)))
        
    def set_message(self, message):
        self.clear_lcd()
        self.msg_lcd(message)


    def set_update_time(self):
        self.update_time = datetime.datetime.now() + datetime.timedelta(0, self.update_interval)


    def display_messages(self):
        self.set_update_time()

        while True:

            if len(self.pushes) == 0 and self.did_update == True:
                self.set_message('No pushes')
                time.sleep(self.update_interval)


            for push in self.pushes:
                if push.body == '':
                    continue

                self.lcd_buffer[1] = str(datetime.datetime.fromtimestamp(push.created))[0:self.lcd_columns]
                self.scroll_buffer(push.body, row=0)

                time.sleep(self.pause_interval)


            now = datetime.datetime.now()

            if now >= self.update_time and self.update_pushes() == False:
                self.set_update_time()

if __name__ == "__main__":
    pb_lcd = Pushbullet_LCD()
    pb_lcd.update_pushes()
    pb_lcd.display_messages()

