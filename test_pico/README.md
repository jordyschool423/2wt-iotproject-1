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


## versie2: wifi en mqtt

in dit stuk heb ik de wifi en mqtt connectie toegevoegd.  
wifi wordt bij het opstarten geconnecteerd en als die weg is gevallen of eerste connectie lukt niet zal hij met een interval opnieuw proberen connectie te maken.  
  
mqtt connectie wordt enkel gemaakt als de pomp niet draait en als er wifi connectie is.  
data word ook gepublished met een instelbare interval( niet te laag zetten zodat je niet geblokt wordt door thingspeak zelf).  

## settings.toml

settings.toml file is mee toegevoegd met alle variabele die gebruikt worden.  
comments staan bij de code waarvoor ze dienen.  
eigen data invullen als je deze code wilt testen bij jou thuis.

### extra's:

heb alle variabelen bovenaan de file gezet onder de imports.  
bij elke variabele die van belang is staat commentaar bij. 

 
in geval dat er toch iets niet duidelijk is laat het me weten en dan pas ik het aan zolang de code nog niet gemerged is in main!!!