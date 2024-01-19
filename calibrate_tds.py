import time
from machine import Pin
from dftds import GravityTDS, KValueRepositoryFlash
from psds1820 import get_temp

tds_sensor = GravityTDS(
    pin=28,
    aref=5.0,
    adc_range=65535,
    k_value_repository=KValueRepositoryFlash("tds_calibration.json")
)
while True:
    tds_sensor.temperature = get_temp() # type: ignore
    tds_sensor.begin()
    tds_sensor.update()
    if not tds_sensor.calibrated:
        print("Calibrating")
        tds_sensor.calibrate(69)
    print(tds_sensor.tds_value)
    time.sleep(2)