from datetime import datetime

def save(trader):
    msg = str(trader)
    file = open("resultado.txt", "w")
    file.write(msg)
