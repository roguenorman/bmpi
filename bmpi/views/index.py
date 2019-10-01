from flask import Blueprint, render_template, request
#from bmpi import input_queue, output_queue, wifiServer
from flask import current_app as app
from flask import g


index_bp = Blueprint('index', __name__)

def sendCommand(data_stream):
    global input_queue
    ui = b'AT+RSI_READ\x01\x27\x00GET /ui.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    start = b'AT+RSI_READ\x01\x2a\x00GET /start.bmp HTTP/1.1 Host: 172.16.20.48\r\n'
    index = b'AT+RSI_READ\x01\x2a\x00GET /index.html HTTP/1.1 Host: 172.16.20.48\r\n'
    recipe = b'AT+RSI_READ\x01\x27\x00GET /rz.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    bm_txt = b'AT+RSI_READ\x01\x27\x00GET /bm.txt HTTP/1.1 Host: 172.16.20.48\r\n'
    bm_html = b'AT+RSI_READ\x01\x27\x00GET /bm.html HTTP/1.1 Host: 172.16.20.48\r\n'
    key1 = b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=1 HTTP/1.1 Host: 172.16.20.48\r\n'
    key2 = b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=2 HTTP/1.1 Host: 172.16.20.48\r\n'
    key3 = b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=3 HTTP/1.1 Host: 172.16.20.48\r\n'
    key4 = b'AT+RSI_READ\x01\x27\x00GET /bm.txt?k=4 HTTP/1.1 Host: 172.16.20.48\r\n'

    if data_stream == "ui":
        input_queue.put(ui)
    if data_stream == "start":
        input_queue.put(start)
    if data_stream == "recipe":
        input_queue.put(recipe)
    if data_stream == "bm.txt":
        input_queue.put(bm_txt)
    if data_stream == "bm.html":
        input_queue.put(bm_html)
    if data_stream == "index":
        input_queue.put(index)
    if data_stream == "key1":
        input_queue.put(key1)
    if data_stream == "key2":
        input_queue.put(key2)
    if data_stream == "key3":
        input_queue.put(key3)
    if data_stream == "key4":
        input_queue.put(key4)


def remove_null_bytes(b_data):
    return b_data.decode().replace('\x00', '')

@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    user = {'username': 'David'}
    #if form.validate_on_submit():
    if request.method == 'POST':
        if 'Reset' in request.form:
            return render_template('index.html', title='Home', user=user)
        if 'Start' in request.form:
            sendCommand("start")
            return render_template('index.html', title='Home', user=user)
        if 'recipe' in request.form:
            sendCommand("recipe")
            return render_template('index.html', title='Home', user=user)
        if 'bm.txt' in request.form:
            sendCommand("bm.txt")
            return render_template('index.html', title='Home', user=user)
        if 'bm.html' in request.form:
            sendCommand("bm.html")
            return render_template('index.html', title='Home', user=user)
        if 'ui.txt' in request.form:
            sendCommand("ui.txt")
            return render_template('index.html', title='Home', user=user)
        if 'key1' in request.form:
            sendCommand("key1")
            return render_template('index.html', title='Home', user=user)
        if 'key2' in request.form:
            sendCommand("key2")
            return render_template('index.html', title='Home', user=user)
        if 'key3' in request.form:
            sendCommand("key3")
            return render_template('index.html', title='Home', user=user)
        if 'key4' in request.form:
            sendCommand("key4")
            return render_template('index.html', title='Home', user=user)
        else:
            return render_template('index.html', title='Home', user=user)
    elif request.method == 'GET':
            return render_template('index.html', title='Home', user=user)