# CTRL + SHIFT + P for commando palet
# Selecteer CircuitPython Serial Monitor -> Pico
# CTRL + C to start terminal

# CTRL-D to start program
# CTRL-C to stop program

# File imports
import waterbowl

# Library imports
import time
import math


def voltage_to_volume(voltage):
    """
    Turns voltage into volume in mL using a quadratic 
    equation derived from calibration data
    """
    return (419.7334 * voltage**2 - 687.4488 * voltage + 329.9911)

# waterlevel_sensor 
try:
    while True:
        input("Press Enter to read water level... (CTRL + C to stop)")
        water_level = waterbowl.read_water_level()
        voltage = (water_level / 65535) * 3.3  # Convert to voltage
        if voltage < 0.8: # Threshold for low water level, under calibration range
            print("Water level is too low to measure.")
            continue
        volume = voltage_to_volume(voltage)
        print("Waterlevel in voltage:", f"{voltage:.2f}V")
        print("Waterlevel in volume:", f"{volume:.0f}mL")

# CTRL + C to stop the program
except KeyboardInterrupt:
    print("\nProgram stopped by user.")