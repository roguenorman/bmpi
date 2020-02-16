from flask import Blueprint, render_template, Response, make_response
import serial
from time import sleep
from flask import current_app as app
from flask import g
from bmpi import serial_input_queue, serial_output_queue, wifiServer

terminal_bp = Blueprint('terminal', __name__)

#rz.txt = ;2
#bm.txt = ;1


# version date;
# serial number;
# 1
# X08:30 #time
# XC
# X2030 or X101
# X520 or X-100000
# X999.5
# X3600
# X12166X0X0X0X0XADUSXphX000X0X0wwwwww

#recipe = ;2
def checkQueue():
    global serial_output_queue
    while True:
        if not serial_output_queue.empty():
            payload = serial_output_queue.get()
            print('retreiving from queue')
            #if response is data
            if b'at+rsi_snd=1,0,0,0,' in payload:
                print('response is data')
                payload = byteUnstuff(payload)
                payload = payload.decode('iso-8859-1')
                payload = payload.replace('\x00', '')
                try:
                    payload = payload.split('at+rsi_snd=1,0,0,0,')[1]
                    print('Start of data')
                    print(payload)
                    print('End of data')
                except Exception:
                    #print("cannot decode data as utf8, trying iso")
                    #payload = payload.decode().split('at+rsi_snd=1,0,0,0,')[1]
                    #payload = "data: "+payload.decode('iso-8859-1')+"\n\n"
                    #print(payload)
                    pass
                #format for SSE
                payload = "data: "+payload+"\n\n"
                yield payload



            #else send to SSE as ascii without null bytes
            else:
                #remove line feed
                payload = payload.splitlines()[0]
                #remove null bytes
                payload = payload.decode().replace('\x00', '')
                #send to wifi server
                wifiServer.chooseCommand(payload)()               
                #format for SSE
                payload = "data: "+payload+"\n\n"      
                yield payload
        
#removes null bytes and formate for SSE from binary object
#returns string
def format_for_sse(payload):
    payload = payload.decode().replace('\x00', '')
    payload = "data: "+payload+"\n\n"
    return payload

#takes a string with escapebytes. if replaces the escape bytes with \r\n
def byteUnstuff(payload):
    return payload.replace(b'\xdb\xdc', b'\r\n')


@terminal_bp.route('/terminal_stream')
def terminal_request():
    newresponse = Response(checkQueue(), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    newresponse.headers.add('Content-Type', 'text/event-stream')
    return newresponse


@terminal_bp.route('/terminal')
def terminal():
    #res = make_response(render_template('terminal.html', title='Terminal'))
    #res.headers.set('Access-Control-Allow-Origin', '*')
    #res.headers.set('Cache-Control', 'no-cache')
    #return res
    return render_template('terminal.html', title='Terminal')