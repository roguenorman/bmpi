#!/usr/bin/python3
import io
import serial
import queue
import threading
from bmpi import wifiServer
from time import time

## Change this to match your local settings
SERIAL_PORT = '/dev/ttyAMA0'

class SerialThread(threading.Thread):
 
    def __init__(self, wifiServer, i_queue, o_queue):
        threading.Thread.__init__(self)
        self.i_queue = i_queue
        self.o_queue = o_queue
        self.sp = None        
        self.stop_event = threading.Event()
        self.wifiServer = wifiServer
 
    def close(self):
        self.sp.close()
        self.stop_event.set()
 
    def run(self):
        self.stop_event.clear()
        if self.sp:
            print("serial port already open, closing..")
            self.sp.close()
        self.sp = serial.Serial(SERIAL_PORT, 115200, parity='N', stopbits=1, bytesize=8, rtscts=0, dsrdtr=0)
        self.sp.flushInput()
        self.sp.flushOutput()
        while not self.stop_event.is_set():
            while True:
                try:

                    # look for incoming serial data
                    if (self.sp.inWaiting() > 0):
                        data = self.sp.readline()
                        # send it back to flask
                        self.o_queue.put(data)
                    # look for incoming flask request
                    if not self.i_queue.empty():
                        data = self.i_queue.get()
                        # send it to the serial device
                        self.sp.write(data)
                    # look for incoming serial data

                except (IOError, OSError, serial.SerialException) as e:
                    if self.sp:
                        self.sp.close()
                        #self.sp = None


    def read_message(self):
        self.exit_on_fatal_error()
        try:
            return self.messages.get_nowait()
        except queue.Empty:
            return None