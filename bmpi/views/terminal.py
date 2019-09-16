from flask import Blueprint, render_template, Response, make_response
import serial
from time import sleep
from flask import current_app as app
from flask import g
from bmpi import input_queue, output_queue, wifiServer

terminal_bp = Blueprint('terminal', __name__)

#sudo apt install libtiff5
#sudo apt-get install libopenjp2-7-dev
## index.html, vs.txt, temp.bmp, start.bmp, 
#bm.txt = X20:41XCX101X-10000X999.5X3600X29122X0X0X0X0XEMSRXphX000X0wwwwww}`


def checkQueue():
#    global output_queue
#    while True:
#        if not output_queue.empty():
#            message = output_queue.get()
#
#            #formate messge for wifiServer
#            message = byteUnstuff(message)
#            message = remove_null_bytes(message)
#            message = message.splitlines()[0]
#            wifiServer.chooseCommand(message)()
#            
#            #format the mesage for for SSE
#            #dont send data to terminal. only ascii
#            if b'at+rsi_snd=1,0,0,0,' not in message:
#                message format_for_sse(message)
#            else:
#                yield message
#        else:
#            yield ("Output queue empty")
#        sleep(1)

    global output_queue
    while True:
        if not output_queue.empty():
            payload = output_queue.get()
            #if response is data
            if b'at+rsi_snd=1,0,0,0,' in payload:
                payload = byteUnstuff(payload)
                try:
                    payload = payload.decode().split('at+rsi_snd=1,0,0,0,')[1]
                    print(payload)
                except Exception:
                    print("exception")
                    payload = "data: "+payload.decode()+"\n\n"
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
    #x = payload.replace(b'\xdb\xdc', b'\r\n')
    #x = payload.replace(b'\xdb\xdd', b'\xdb')
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