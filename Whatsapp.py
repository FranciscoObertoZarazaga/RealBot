import pywhatkit

def notify(msg):
    pywhatkit.sendwhatmsg_instantly('+543517694686',msg,tab_close=True,close_time=60,wait_time=20)