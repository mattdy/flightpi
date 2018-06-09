"""
SbsThread.py
Reads SBS information from specified remote host, parses, and passes on to interested parties

Matt Dyson
24/01/18

Part of FlightPi - http://github.com/mattdy/flightpi
"""
import threading
import SbsMessage
import socket
import logging
import time

log = logging.getLogger('root')

class SbsThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)

        self.host = host
        self.port = port
        self.socket = None

        self.stopping = False

        self.receivers = [ ] # Array of functions to pass our received SbsMessage to

    def connect(self):
        """ Set up a socket for reading from our remote host """

        log.info("Connecting to host %s on port %s" % (self.host, self.port))
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5) # Timeout after 5s to avoid blocking for a long time if no messages
            self.socket.connect((self.host, self.port))

            self.socket.send("")

            log.info("Connection complete")
        except Exception as e:
            log.error("Error connecting", e)
            self.socket = None

    def addReceiver(self, func):
        """ Add a callback function that will be passed every SbsMessage we parse """

        log.debug("Added new SbsMessage receiver - %s" % (func))
        self.receivers.append(func)

    def processLine(self, line):
        """ Attempt to turn a received line into a SbsMessage, and then pass on to the callbacks """

        try:
            msg = SbsMessage.SbsMessage(line)

            for rec in self.receivers:
                try:
                    rec(msg)
                except:
                    log.error("Error processing message [%s] through function [%s]" % (msg,rec))
        except ValueError:
            log.debug("Error processing line [%s]" % (line))

    def stop(self):
        self.stopping = True

    def run(self):
        log.info("SbsThread starting")
        while not self.stopping:
            if self.socket == None:
                self.connect()
                time.sleep(1)
                continue

            self.buff = ""
            data = "\n"

            while not data in self.buff:
                try:
                    recv = self.socket.recv(1024)
                    if not recv:
                        log.error("Socket has been closed, will attempt reconnecting")
                        self.socket = None
                        break
                    self.buff += recv
                except socket.timeout as t:
                    continue
                except Exception as e:
                    log.error("Error receiving data, will attempt reconnecting", e)
                    self.socket = None
                    break

            if not data in self.buff:
                # This seems odd, but it'll happen if we 'break' out of the loop above due to an error
                # In this case, we go back to the start of the main thread loop and reconnect
                log.debug("Incomplete line, restarting loop")
                continue
  
            pos = self.buff.find(data)
            rval = self.buff[:pos + len(data)]
            self.buff = self.buff[pos + len(data):]

            msg = rval.strip()
            if(msg is not None and msg is not ""):
                self.processLine(msg)

        log.info("SbsThread shutting down")        
        self.socket.close()
        log.info("SbsThread shut down")
