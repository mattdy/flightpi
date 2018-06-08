"""
ArdunioThread
Accepts details of a flight to display, and outputs them to an Arduino for LED display

Matt Dyson
07/06/18

Part of FlightPi - http://github.com/mattdy/flightpi
"""
import threading
import logging
import time
import serial

log = logging.getLogger('root')

class ArduinoThread(threading.Thread):
    def __init__(self, address="/dev/ttyUSB0"):
        threading.Thread.__init__(self)
        self.stopping = False

        self.display = None

        self.address = address
        self.device = None

    def processFlight(self, flight):
        """ Take the given flight details, translate it into what we want to show on the LCD """
        log.debug("Received flight %s to display" % (flight))

        if(flight is None):
            self.device.write("C\n")
            self.device.flush()
        else:
            self.device.write("D%s\n" % (flight['track']))
            self.device.write("A%s\n" % (flight['altitude']))

    def stop(self):
        self.stopping = True

    def run(self):
        log.info("ArduinoThread starting")

        self.device = serial.Serial(self.address, 9600)

        while not self.stopping:
            time.sleep(1)

        self.device.write("C\n")
        self.device.close()

        log.info("ArduinoThread shut down")