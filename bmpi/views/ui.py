from flask import Blueprint, render_template, Response, request
from flask import current_app as app

ui_bp = Blueprint('ui', __name__)

def sendCommand(data_stream):
    value = b'AT+RSI_READ\x01\x27\x00GET '+ data_stream.encode('ascii') + b' HTTP/1.1 Host: 172.16.20.48\r\n'
    #print(value)
    app.wifi_srv.sendToSerial(value)

    if data_stream == "ui.txt":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "recipe":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /rz.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "bm.txt":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt HTTP/1.1 Host: 172.16.20.48\r\n')


def event_stream():
    pass
    #format for SSE
    #payload = "data: "+payload+"\n\n"
    #yield payload

@ui_bp.route('/stream')
def stream():
    newresponse = Response(event_stream(), mimetype="text/event-stream")
    newresponse.headers.add('Access-Control-Allow-Origin', '*')
    newresponse.headers.add('Content-Type', 'text/event-stream')
    return newresponse

@ui_bp.route('/ui', methods=['GET', 'POST'])
def ui():
    if request.method == 'POST':
        sendCommand(request.form.getlist("key")[0])
        return render_template('ui.html', title='UI')

        if 'recipe' in request.form:
            sendCommand("recipe")
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