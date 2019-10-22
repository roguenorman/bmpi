from flask import Blueprint, render_template, request
from flask import current_app as app


ui_bp = Blueprint('ui', __name__)

def sendCommand(data_stream):
    if data_stream == "ui.txt":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "recipe":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /rz.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "bm.txt":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "key1":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=1 HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "key2":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=2 HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "key3":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=3 HTTP/1.1 Host: 172.16.20.48\r\n')
    if data_stream == "key4":
        app.wifi_srv.sendToSerial(b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=4 HTTP/1.1 Host: 172.16.20.48\r\n')

@ui_bp.route('/ui', methods=['GET', 'POST'])
def ui():
    #return render_template(' ui.html', title=' ui')
    if request.method == 'POST':
        if 'recipe' in request.form:
            sendCommand("recipe")
            return render_template('ui.html', title='UI')
        if 'bm.txt' in request.form:
            sendCommand("bm.txt")
            return render_template('ui.html', title='UI')
        if 'ui.txt' in request.form:
            sendCommand("ui.txt")
            return render_template('ui.html', title='UI')
        if 'key1' in request.form:
            sendCommand("key1")
            return render_template('ui.html', title='UI')
        if 'key2' in request.form:
            sendCommand("key2")
            return render_template('ui.html', title='UI')
        if 'key3' in request.form:
            sendCommand("key3")
            return render_template('ui.html', title='UI')
        if 'key4' in request.form:
            sendCommand("key4")
            return render_template('ui.html', title='UI')
        else:
            return render_template('ui.html', title='UI')
    elif request.method == 'GET':
            return render_template('ui.html', title='UI')