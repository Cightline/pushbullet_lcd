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

        logging.basicConfig(format='%(asctime)s %(message)s', 
                            datefmt='%m/%d/%Y %I:%M:%S',
                            filename=self.get_setting('log_path'), 
                            level=logging.DEBUG)
        self.update_interval = float(self.get_setting('update_interval'))
        self.pause_interval  = float(self.get_setting('pause_interval'))
        self.update_time     = None
        self.api             = pb.PushBullet(self.get_setting('api_key'))


        # autoscroll off
        self.write_cmd([0x52])
        #self.ser.write(b'\xfe\x52')

        # go home
        self.write_cmd([0x48])
        #self.ser.write(b'\xfe\x48')
        
        # auto newline off
        self.write_cmd([0x44])
        #self.ser.write(b'\xfe\x44')

        # set contrast
        self.write_cmd([0x50, int(self.get_setting('contrast'))])
        
        self.set_color(int(self.get_setting('red')),
                       int(self.get_setting('green')),
                       int(self.get_setting('blue')))

    def write_cmd(self, commands):
        #https://github.com/adafruit/Adafruit-USB-Serial-RGB-Character-Backpack/blob/master/matrixtest.py
        commands.insert(0, 0xFE)

        for i in range(0, len(commands)):
            self.ser.write(chr(commands[i]))
            time.sleep(0.005)


    def get_setting(self, setting):
        return self.config.get('settings', setting)


    def clear_lcd(self):
        self.ser.write(b'\xfe\x58')


    def msg_lcd(self, message):
        print(message)
        self.ser.write(bytes(message))


    def set_color(self, r, g, b):

        self.write_cmd([0xD0, r, g, b])

        #self.ser.write(b'\xfe\xd0' + hex(r) + hex(g) + hex(b))
        #self.ser.write(b'\xfe\xd0\x255\x255\x255')


    def write_message_buffer(self):
        print(self.lcd_buffer)
        self.clear_lcd()
        self.msg_lcd('\n'.join(self.lcd_buffer))

   
    def scroll_buffer(self, message, row):
        front = 0
        end   = self.lcd_columns

        # If the message is short enough to display w/o scrolling
        if len(message) <= self.lcd_columns:
            diff = (self.lcd_columns - len(self.lcd_buffer[row])) + self.lcd_columns
            self.lcd_buffer[row] = message.ljust(diff)
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
        self.did_update = False
        
        try:
            for push in self.api.pushes():
                print(push)
                self.pushes.append(push)

            self.did_update = True

        except RuntimeError as e:
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

            
            elif len(self.pushes) and self.did_update == True:
                for push in self.pushes:
                    if push.body == '' or push.type != 'note':
                        continue

                    self.lcd_buffer[1] = str(datetime.datetime.fromtimestamp(push.created))[0:self.lcd_columns]
                    self.scroll_buffer(push.body, row=0)

                    time.sleep(self.pause_interval)


            if datetime.datetime.now() >= self.update_time:
                self.set_update_time()
                self.update_pushes()



if __name__ == "__main__":
    pb_lcd = Pushbullet_LCD()
    pb_lcd.update_pushes()
    pb_lcd.display_messages()

