from flask import Blueprint, render_template, Response, request, stream_with_context
from flask import current_app as app
from flask import Flask
from queue import Empty


ui_bp = Blueprint('ui', __name__)

def sendCommand(data_stream):
    value = b'AT+RSI_READ\x01\x27\x00GET '+ data_stream.encode('ascii') + b' HTTP/1.1 Host: 172.16.20.48\r\n'
    app.wifi_srv.sendToSerial(value)
    
    #if data_stream == "ui.txt":
    #    app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    #if data_stream == "bm.txt":
    #    app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt HTTP/1.1 Host: 172.16.20.48\r\n')


def checkQueue():
    while True:
        if not app.wifi_srv.log_input_queue.empty():
            payload = app.wifi_srv.log_input_queue.get()
            #format for SSE
            payload = "data: "+payload+"\n\n"
            print("ui payload is :" + payload)
            yield payload

@ui_bp.route('/stream')
def stream():
    newresponse = Response(stream_with_context(checkQueue()), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    newresponse.headers.add('Content-Type', 'text/event-stream')
    return newresponse

@ui_bp.route('/ui', methods=['GET', 'POST'])
def ui():
    if request.method == 'POST':
        app.wifi_srv.requestUri = request.form.getlist("key")[0]
        #print (request.form.getlist("key")[0])
        sendCommand(request.form.getlist("key")[0])
        return render_template('ui.html', title='UI')

        if 'bm.txt' in request.form:
            sendCommand("bm.txt")
            return render_template('ui.html', title='UI')
        if 'ui.txt' in request.form:
            sendCommand("ui.txt")
            return render_template('ui.html', title='UI')

        else:
            return render_template('ui.html', title='UI')
    elif request.method == 'GET':
            return render_template('ui.html', title='UI')