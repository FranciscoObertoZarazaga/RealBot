from flask import Flask, render_template
from flask_socketio import SocketIO

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP, async_mode="threading")

@APP.route('/')
def index():
    return render_template('index.html')

@SOCKETIO.event
def connect():
    print('Conectado')

def broadcast(event, msg):
    SOCKETIO.emit(event, msg)

class UserInterface:
    def __init__(self):
        pass

    def update(self,msg):
        broadcast('state',msg)


USER_INTERFACE = UserInterface()
