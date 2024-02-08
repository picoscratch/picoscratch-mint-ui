from display import oled
from time import sleep

oled.fill(0)
oled.text("Hallo Skript!", 0, 0)
oled.show()
time.sleep(1)
