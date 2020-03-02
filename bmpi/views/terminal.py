from flask import Blueprint, render_template, Response, request, make_response, stream_with_context
from flask import current_app as app
from queue import Empty
from time import sleep
import serial


terminal_bp = Blueprint('terminal', __name__)

#removes null bytes and formats for SSE
#returns string
def format_for_sse(payload):
    payload = payload.replace('\x00', '')
    payload = "data: "+payload+"\n\n"
    return payload

#takes a string with escapebytes. if replaces the escape bytes with \r\n
def byteUnstuff(payload):
    return payload.replace(b'\xdb\xdc', b'\r\n')

def checkQueue():
    while True:
        if not app.wifi_srv.log_input_queue.empty():
            payload = app.wifi_srv.log_input_queue.get()
            #format for SSE
            payload = "data: "+payload+"\n\n"
            print("terminal payload is: " + payload)
            yield payload
    #try:  payload = app.wifi_srv.log_input_queue.get_nowait()
    #except Empty:
    #    pass
    #else:
    #    #format for SSE
    #    payload = "data: "+payload+"\n\n"
    #    yield payload

        
@terminal_bp.route('/terminal_stream')
def terminal_request():
    newresponse = Response(stream_with_context(checkQueue()), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    newresponse.headers.add('Content-Type', 'text/event-stream')
    return newresponse


@terminal_bp.route('/terminal')
def terminal():
    return render_template('terminal.html', title='Terminal')