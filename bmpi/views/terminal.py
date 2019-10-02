from flask import Blueprint, render_template, Response, make_response
import serial
from time import sleep
from flask import current_app as app
from flask import g


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
    pass

        
@terminal_bp.route('/terminal_stream')
def terminal_request():
    newresponse = Response(checkQueue(), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    newresponse.headers.add('Content-Type', 'text/event-stream')
    return newresponse


@terminal_bp.route('/terminal')
def terminal():
    return render_template('terminal.html', title='Terminal')