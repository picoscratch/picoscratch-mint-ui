from display import oled, readPBM
from time import sleep

def showAlerts():
    noAlerts()

def noAlerts():
    oled.fill(0)
    oled.text("Keine Meldungen", 5, 5)
    oled.show()
    sleep(3)