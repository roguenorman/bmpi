from flask import Blueprint, render_template, Response, request, stream_with_context, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import Flask
from queue import Empty


start_bp = Blueprint('start', __name__)

@app.route('/<path:filename>') 
def send_file(filename): 
    return send_from_directory(app.static_folder, filename)

#TODO research buttons so we dont need them in a form and need to post the form and hande redirects etc
@start_bp.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        print('key is: ' + request.form.getlist("key")[0])
        if request.form.getlist("key")[0] == 'OK':
            app.wifi_srv.sendToSerial(b'OK\r\n')
            print('OK')
            return render_template('start.html')
        app.wifi_srv.requestUri = request.form.getlist("key")[0]
        sendCommand(request.form.getlist("key")[0])
        print('POST')
        return redirect(url_for('.start'))
    else:
            return render_template('start.html')