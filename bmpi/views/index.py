from flask import Blueprint, render_template

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
def index():
    return 'Hello, World!'