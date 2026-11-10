#Base imports
import time
import threading


#File imports
from camera import get_animal                                                                  #import om foto te maken en terug te sturen wat er aan het drinken is
from oled import refresh_display, refresh_display_drinking, show_message, turn_off_display    #imports functie om oled aan te sturen

#global variables
exit_event = threading.Event()  # Create an event to signal the thread to exit
waterlevel_in_bowl = -1  # Placeholder for the water level in the bowl
waterlevel_in_tank = -1  # Placeholder for the water level in the tank
animal = None  # Placeholder for the animal drinking status

#Functions
def check_animal_drinking(tank_volume):
    """Check if an animal is drinking and change the display."""
    while not exit_event.is_set():
        if waterlevel_in_bowl <= 200 and not animal:
            show_message("Someone is drinking!")
            animal = get_animal()  
            if animal:
                refresh_display_drinking(f"{animal} is drinking")
        elif waterlevel_in_bowl > 200:
            animal = None   
        time.sleep(1)  # Check every second 
    
def get_pico_data():
    """Get the water level data from the Pico script."""
    global waterlevel_in_bowl, waterlevel_in_tank
    while not exit_event.is_set():
        # Placeholder for getting data from the Pico script
        # Replace this with actual code to read from the Pico
        waterlevel_in_bowl = 300  # Example value
        waterlevel_in_tank = 45   # Example value
        time.sleep(5)  # Update every 5 seconds

def call_pump_to_fill_bowl():
    """Call the pump to fill the bowl if the water level is low and no animal is drinking."""



# --- Main Execution ---
show_message("loading data...")

get_pico_data()  # Get initial data from the Pico script

#while loop to wait for valid water level data before starting the main loop and threads.
while waterlevel_in_tank == -1 or waterlevel_in_bowl == -1:
    print("Waiting for Pico data to be available...")  # Placeholder for waiting for Pico data
    get_pico_data()  # Get data from the Pico script
    time.sleep(1)

#Threading 
t1 = threading.Thread(target=check_animal_drinking, args=(waterlevel_in_tank), daemon=True)  # Create a thread for the get_animal function
#t2 = threading.Thread(target=get_pico_data, daemon=True)  # Create a thread for the get_pico_data function

t1.start()  # Start the thread to check for drinking animals continuously
#t2.start()  # Start the thread to get the Pico data continuously

try:
    while True:
        #check if animal is drinking, if not: update OLED (otherwise this would overwrite the message that an animal is drinking)
        if waterlevel_in_bowl <= 200:
            refresh_display(waterlevel_in_tank)  # Update the OLED with the water level in the tank

        #Call on pump to fill bowl if waterlevel is low and no animal is drinking
        if waterlevel_in_bowl <= 10:
            show_message("Filling bowl...")
            call_pump_to_fill_bowl()  # Call the pump to fill the bowl
            time.sleep(5)  # Simulate time taken to fill the bowl
            new_waterlevel_in_bowl = 500  # Placeholder for new water level after filling
            refresh_display(new_waterlevel_in_bowl)  # Update the OLED with the new water level in the bowl

        time.sleep(10)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    exit_event.set()  # Signal the thread to exit
    t1.join()               # wait for the thread to finish
    #t2.join()               # wait for the thread to finish
    turn_off_display()      #shutdown of the oled       
    print("Program successfully terminated.")
