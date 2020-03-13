from flask import Blueprint, render_template, Response, request, stream_with_context, redirect, url_for
from flask import current_app as app
from flask import Flask
from queue import Empty


ui_bp = Blueprint('ui', __name__)

#TODO put this function in wifi server
def sendCommand(data_stream):
    value = b'AT+RSI_READ\x01\x27\x00GET '+ data_stream.encode('ascii') + b' HTTP/1.1 Host: 172.16.20.48\r\n'
    app.wifi_srv.sendToSerial(value)

#TODO put this function in wifi server
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

#TODO research buttons so we dont need them in a form and need to post the form and hande redirects etc
@ui_bp.route('/ui', methods=['GET', 'POST'])
def ui():
    if request.method == 'POST':
        print('key is: ' + request.form.getlist("key")[0])
        if request.form.getlist("key")[0] == 'OK':
            app.wifi_srv.sendToSerial(b'OK\r\n')
            print('OK')
            return render_template('ui.html', title='UI')
        app.wifi_srv.requestUri = request.form.getlist("key")[0]
        sendCommand(request.form.getlist("key")[0])
        print('POST')
        return redirect(url_for('.ui'))
        #return render_template('ui.html', title='UI')
    else:
            return render_template('ui.html', title='UI')

