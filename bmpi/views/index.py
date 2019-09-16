from flask import Blueprint, render_template, request
from bmpi import input_queue, output_queue, wifiServer
from flask import current_app as app
from flask import g


index_bp = Blueprint('index', __name__)

def sendCommand(message):
    global output_queue
    wifiServer.sendCommand(message)

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
        else:
            return render_template('index.html', title='Home', user=user)
    elif request.method == 'GET':
            return render_template('index.html', title='Home', user=user)