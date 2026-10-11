## eerste test pico

code in code.py kan je in je pico plakken.
je moet in lib nog de adafruit_hcsr04.mpy plakken om de import in orde te krijgen.  
code zorgt ervoor dat een ultrasone sensor de afstand gaat meten om de stand van het water op te meten.  
als deze afstand groter word dan start_fill dan zal de pomp aanslagen
pomp stopt pas met pompen als de waarde lager als stop_fill is.  
setup is momenteel getest met een ledje i.p.v een relais bordje met de pomp eraan.

aansluiten van de pico:

- sensor:

  - vcc -> pin: 36
  - trigger -> pin 19
  - echo -> pin 20
  - ground -> pin 38
- led
  - Vin -> pin 1
  - ground -> pin 3


later kan de sensor eventueel worden vervangen door een waterlevel sensor als de calibratie goed gelukt is  
de led kan worden vervangen door een relais bordje of eventueel in serie gezet worden.
