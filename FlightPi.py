"""
FlightPi.py
Main execution flow. Creates all necessary inputs and outputs, and links them together

Matt Dyson
24/01/18

Part of FlightPi - http://github.com/mattdy/flightpi
"""
import logging
import sys

log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)8s %(module)15s: %(message)s')
stream.setFormatter(formatter)

log.addHandler(stream)

from SbsThread import SbsThread
import time

class FlightPi:
    def __init__(self):
        self.stopping = False


    def stop(self):
        self.stopping = True

    def execute(self):
        log.info("Starting up FlightPi")

        self.sbsThread = SbsThread("mercury",30003)
        self.sbsThread.addReceiver(self.callback)
        self.sbsThread.start()

        log.info("Starting loop")
        try:
            while(self.stopping is False):
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            log.warn("Interrupted, shutting down")


        self.sbsThread.stop()

    def callback(self,msg):
        log.debug("Callback on %s (%s)" % (msg.icao24, msg.callsign))

flightpi = FlightPi()
flightpi.execute()
