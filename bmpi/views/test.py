from flask import Blueprint, render_template, Response, make_response
import serial
from time import sleep
from flask import current_app as app
from flask import g
from bmpi import input_queue, output_queue, wifiServer

test_bp = Blueprint('test', __name__)



@test_bp.route('/test')
def test():
    return render_template('test.html', title='Test')