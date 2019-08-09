from flask import Blueprint, render_template, Response
import serial
import io

terminal_bp = Blueprint('terminal', __name__)

def sendToSerial(data):
    print(data)
    ser.write(data.encode())

def serialEvent():
    ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, parity='N', stopbits=1, bytesize=8, rtscts=0, dsrdtr=0)
    ser_text = io.TextIOWrapper(ser, newline='\r\n')
    print(ser.name)
    data = ser_text.readline()
    while True:
        data = ser_text.readline()
        #if len(data) >= 1:
            #yield 'data: %s\n\n' % data

        if 'at+rsi_rssi?' in data.decode():
            rssi = b'OK\x1f\r\n' #iwlist scan
            sendToSerial(rssi)
        yield 'data: %s\n\n' % data

@terminal_bp.route('/terminal')
def terminal():
    #return render_template('terminal.html')
    newresponse = Response(serialEvent(), mimetype="text/event-stream")
    return newresponse