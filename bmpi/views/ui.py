from flask import Blueprint, render_template, Response, request, stream_with_context, redirect, url_for, jsonify
from flask import current_app as app
from flask import Flask
from queue import Empty


ui_bp = Blueprint('ui', __name__)

#TODO put this function in wifi server
#def sendCommand(data_stream):
#    value = b'AT+RSI_READ\x01\x27\x00GET '+ data_stream.encode('ascii') + b' HTTP/1.1 Host: 172.16.20.48\r\n'
#    app.wifi_srv.sendToSerial(value)

#TODO put this function in wifi server
def checkQueue():
    while True:
        if not app.wifi_srv.log_input_queue.empty():
            payload = app.wifi_srv.log_input_queue.get()
            payload = 'data: '+payload+'\n\n'
            #print(payload)
            yield payload

@ui_bp.route('/stream')
def stream():
    response = Response(stream_with_context(checkQueue()), mimetype="text/event-stream")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Content-Type', 'text/event-stream')
    return response

@ui_bp.route('/ui', methods=['GET', 'POST'])
def ui():
    #initial request to get the BM ui
    app.wifi_srv.send_data("/bm.html")
    return render_template('ui.html')

@ui_bp.route('/keypress', methods=["GET","POST"])
def test():
    app.wifi_srv.send_data(request.json)
    #refresh ui
    app.wifi_srv.send_data("/bm.html")
    return render_template('ui.html')



