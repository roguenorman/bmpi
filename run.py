from bmpi import create_app
from bmpi import serialDriver

app = create_app()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', threaded=True, use_reloader=False)
