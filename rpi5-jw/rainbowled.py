import board
import adafruit_rgbled
import time


red_led = board.D16
green_led = board.D12
blue_led = board.D26

led = adafruit_rgbled.RGBLED(red_led,green_led,blue_led)

led.color = (255,0,0)

red_color = 255
green_color = 0
blue_color = 0
stage = 1
step = 15
sleep_timer = 0.1

while True:

    match stage:
        case 1:
            if red_color>0:
                red_color -= step
                green_color += step
                time.sleep(sleep_timer)
            else:
                stage += 1

        case 2:
            if green_color > 0:
                green_color -= step
                blue_color += step
                time.sleep(sleep_timer)
            else:
                stage += 1

        case 3:
            if blue_color > 0:
                blue_color -= step
                red_color += step
                time.sleep(sleep_timer)
            else:
                stage = 1


    color = (red_color,green_color,blue_color)

    led.color = color
    
