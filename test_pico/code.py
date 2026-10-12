import time
import board
import digitalio
import adafruit_hcsr04

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP14, echo_pin=board.GP15)

pump = digitalio.DigitalInOut(board.GP0)
pump.direction = digitalio.Direction.OUTPUT


# laagste punt van het glas(of vanaf waar hij moet beginnen met vullen) in cm
start_fill = 30
# punt vanaf waar hij moet stoppen met vullen in cm
stop_fill = 10

#geeft waarde terug of pomp moet aanslaan of niet
def set_pump(on_off):
    pump.value = on_off


def next_state(distance, filling):
    if not filling and distance > start_fill:
        return True
    if filling and distance < stop_fill:
        return False
    
    #behoud de stand van de pomp als de status niet moet veranderen
    return filling


filling = False
set_pump(filling)

while True:
    try:
        #haalt de stand van het water op
        distance = sonar.distance
    except RuntimeError:
        print("no echo, retrying")
        time.sleep(1)
        continue

    #checked of hij bij moet worden gevuld
    filling = next_state(distance, filling)
    set_pump(filling)
    #debug print
    print(f"distance: {distance:.1f} cm  filling: {filling}")
    time.sleep(1)