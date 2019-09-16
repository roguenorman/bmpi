#!/usr/bin/python3
import serial
import io
import serial
import queue
import threading

## Change this to match your local settings
SERIAL_PORT = '/dev/ttyAMA0'

class SerialThread(threading.Thread):
 
    def __init__(self, input_queue, output_queue):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = None        
        #self.sp = serial.Serial(SERIAL_PORT, 115200, parity='N', stopbits=1, bytesize=8, rtscts=0, dsrdtr=0)
        self.stop_event = threading.Event()
 
    def close(self):
        self.sp.close()
        self.stop_event.set()
 
    def writeSerial(self, data):
        self.sp.write(data)
        
    def readSerial(self):
        #return self.sp.readline().replace("\n", "")
        return self.sp.readline()
 
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
                    # look for incoming flask request
                    if not self.input_queue.empty():
                        data = self.input_queue.get()
                        # send it to the serial device
                        self.writeSerial(data)
                        #print("writing to serial:")
                        print (data)
                    # look for incoming serial data
                    if (self.sp.inWaiting() > 0):
                        data = self.readSerial()
                        #print("reading from serial:")
                        #print (data)
                        # send it back to flask
                        self.output_queue.put(data)
                except (IOError, OSError, serial.SerialException) as e:
                    if self.sp:
                        self.sp.close()
                        #self.sp = None



