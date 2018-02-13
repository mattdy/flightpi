"""
SbsMessage.py
Parses SBS-1 ADS-B messages into a workable Python object

Inspiration from https://github.com/kanflo/ADS-B-funhouse/blob/master/sbs1.py

Matt Dyson
24/01/18

Part of FlightPi - http://github.com/mattdy/flightpi
"""
class SbsMessageType:
    ES_IDENT_AND_CATEGORY = 1
    ES_SURFACE_POS = 2
    ES_AIRBORNE_POS = 3
    ES_AIRBORNE_VEL = 4
    SURVEILLANCE_ALT = 5
    SURVEILLANCE_ID = 6
    AIR_TO_AIR = 7
    ALL_CALL_REPLY = 8

class SbsMessage:
    def __init__(self, input):
        self.parts = input.split(",")

        if self.parts[0] != "MSG":
           raise ValueError("Invalid message")

        self.transmissionType = self.getPart(1)
        self.sessionID = self.getPart(2)
        self.aircraftID = self.getPart(3)
        self.icao24 = self.getPart(4)
        self.flightID = self.getPart(5)
        self.callsign = self.getPart(10)
        self.altitude = self.getPart(11)
        self.groundSpeed = self.getPart(12)
        self.track = self.getPart(13)
        self.verticalRate = self.getPart(16)
        self.squawk = self.getPart(17)

    def getPart(self, index):
        fetch = self.parts[index].strip()
        if(fetch==''): return None
        return fetch
