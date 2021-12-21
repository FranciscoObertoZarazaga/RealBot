from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from User import USERS
from Tester import TESTER
from Binance import WS
from Config import THREADS
from threading import Thread

class UserInterface(SocketIO):
    def __init__(self, app):
        super(UserInterface, self).__init__(app, async_mode="threading")

    def update(self,msg):
        broadcast('state',msg)


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = UserInterface(APP)
generador = Bcrypt

class Formulario(FlaskForm):
    name = StringField("Username")
    phone = IntegerField("Phone")
    password = PasswordField('Password')
    password_confirm = PasswordField('Password')
    submit = SubmitField("Send")


@APP.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html', tester=TESTER)
"""
    name = None
    password = None
    logged = False
    form = Formulario() if form == None else form

    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        logged = USERS.login(name, password)

    if logged:
        return render_template('index.html',form=form, tester=TESTER)
    else:
        return render_template('login.html', name=name, password=password, form=form)
"""


@APP.route('/register', methods=['GET', 'POST'])
def register():
    form = Formulario()
    registred = False

    if form.validate_on_submit():
        name = form.name.data
        phone = form.phone.data
        password = form.password.data
        registred = USERS.register(name, phone, password)

    if registred:
        return main(form=form)
    else:
        return render_template('register.html', form=form)


@SOCKETIO.event
def connect():
    pass

@SOCKETIO.event
def on():
    print('on')
    THREADS.update({'bot': Thread(target=WS.run, name='bot', daemon=False)})
    THREADS['bot'].start()
    SOCKETIO.update(TESTER.test())
    broadcast('switch_mode', True)

@SOCKETIO.event
def off():
    print('off')
    Thread(target=WS.stop(), name='bot', daemon=False).start()
    print('listo')
    SOCKETIO.update(TESTER.test())
    broadcast('switch_mode', False)


def broadcast(event, msg):
    SOCKETIO.emit(event, msg)



