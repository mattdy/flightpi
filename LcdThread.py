"""
LcdThread.py
Accepts details of a flight to display, and outputs them to an LCD

Inspiration taken from https://www.raspberrypi-spy.co.uk/2015/05/using-an-i2c-enabled-lcd-screen-with-the-raspberry-pi/

Matt Dyson
13/02/18

Part of FlightPi - http://github.com/mattdy/flightpi
"""
import threading
import logging
import time
import smbus
from FlightDetails import FlightDetails

log = logging.getLogger('root')

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT_ON  = 0x08  # On
LCD_BACKLIGHT_OFF = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

class LcdThread(threading.Thread):
    def __init__(self, address=0x20, width=20):
        threading.Thread.__init__(self)
        self.stopping = False

        self.display = None
        self.backlight = LCD_BACKLIGHT_OFF

        self.bus = smbus.SMBus(1) #I2C interface

        self.address = address
        self.width = width

        self.data = FlightDetails()

    def processFlight(self, flight):
        """ Take the given flight details, translate it into what we want to show on the LCD """
        lines = {
            LCD_LINE_1: "",
            LCD_LINE_2: "",
            LCD_LINE_3: "",
            LCD_LINE_4: "",
        }

        if(flight is not None):
            type = self.data.getType(flight['icao24'])
            if type is None: type=""

            speed = flight['groundSpeed']
            if speed is None:
                speed = ""
            else:
                speed += "kts"

            altLine = self.getLevel(flight['altitude'])
            # Pad out line with appropriate number of spaces
            altLine = altLine.ljust(self.width - len(speed))
            altLine += speed

            lines = {
                LCD_LINE_1: '{}'.format(flight['callsign'].center(self.width)),
                LCD_LINE_2: altLine,
                LCD_LINE_3: '{}'.format(type.center(self.width)),
                LCD_LINE_4: '{}'.format(flight['squawk'].center(self.width))
            }
            self.backlight = LCD_BACKLIGHT_ON
        else:
            self.backlight = LCD_BACKLIGHT_OFF

        for i in lines:
            self.__lcd_line(lines[i], i)

    def getLevel(self, level):
        """ Turn a given level into an altitude or flight level display accordingly """
        if level<6000: # Transition level
            return "A{}".format(int(level)/100)
        else:
            return "FL{}".format(int(level)/100)

    def __lcd_write(self, bits, mode):
        """ Send byte to data pins on the LCD """
    
        # bits = the data
        # mode = 1 for data
        #        0 for command
        bits_high = mode | (bits & 0xF0) | self.backlight
        bits_low = mode | ((bits<<4) & 0xF0) | self.backlight

        # High bits
        self.bus.write_byte(self.address, bits_high)
        self.__lcd_toggle(bits_high)

        # Low bits
        self.bus.write_byte(self.address, bits_low)
        self.__lcd_toggle(bits_low)

    def __lcd_toggle(self, bits):
        """ Toggle enable off and on to force update """
        time.sleep(E_DELAY)
        self.bus.write_byte(self.address, (bits | ENABLE))
        time.sleep(E_PULSE)
        self.bus.write_byte(self.address, (bits & ~ENABLE))
        time.sleep(E_DELAY)

    def __lcd_line(self, message, line):
        """ Send message to display on given line """
        message = message.ljust(self.width," ")

        self.__lcd_write(line, LCD_CMD)

        for i in range(self.width):
            self.__lcd_write(ord(message[i]),LCD_CHR)

    def stop(self):
        self.stopping = True

    def run(self):
        log.info("LcdThread starting")

        # Initialise display
        self.__lcd_write(0x33, LCD_CMD) # 110011 Initialise
        self.__lcd_write(0x32, LCD_CMD) # 110010 Initialise
        self.__lcd_write(0x06, LCD_CMD) # 000110 Cursor move direction
        self.__lcd_write(0x0C, LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.__lcd_write(0x28, LCD_CMD) # 101000 Data length, number of lines, font size
        self.__lcd_write(0x01, LCD_CMD) # 000001 Clear display
        time.sleep(E_DELAY)

        while not self.stopping:
            # Updating logic done through processMessage, so nothing to do here
            time.sleep(1)

        self.__lcd_write(0x01, LCD_CMD)
        log.info("LcdThread shut down")
