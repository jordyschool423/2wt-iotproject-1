# IoT WaterVuller — Waterbaksensor (CircuitPython)

Project voor het vak **IoT Essentials**: een drinkbak voor huisdieren die zichzelf
automatisch bijvult. Deze module leest met twee sensoren het water niveau in de
drinkbak en berekent daaruit het volume in mL.

De gemeten data wordt later doorgestuurd naar de cloud, waar het op thingspeak kan gemonitored worden en doorgestuurd worden naar Raspberry Pi 5. 

## Hardware

| Onderdeel | Rol | Aansluiting |
|---|---|---|
| Raspberry Pi Pico 2 W | Microcontroller (CircuitPython) | — |
| Water Level Sensor (analoog) | Meet water niveau in de drinkbak | `A0`, voeding via `GP22` |
| HC-SR04 ultrasoon sensor | Meet afstand tot het wateroppervlak | trigger `GP19`, echo `GP18` |

`GP22` wordt gebruikt als een soort "schakelaar" om de sensor alleen van stroom
te voorzien tijdens een meting.

## Benodigde library

Plaats `adafruit_hcsr04.mpy` in de `lib` map van de Pico.

## Gebruik

1. Sla de code op als `main.py` op de Pico.
2. Open de serial monitor (in VS Code: `CTRL+SHIFT+P` → *CircuitPython Serial Monitor*).
3. `CTRL+C` om de REPL te openen, `CTRL+D` om het programma te starten.
4. Druk Enter voor een meting; `CTRL+C` stopt het programma.


## Hoe de meting werkt

De drinkbak wordt door twee onafhankelijke methoden gemeten (Waterlevel Sensor [WLS] en Ultrasoon Sensor [US]), die gecombineerd worden tot één schatting:

### 1. Water Level Sensor (WLS) — analoge meting

- `GP22` zet de sensor aan, er worden 100 metingen gedaan en de **mediaan** wordt
  gebruikt (ongevoelig voor outliers).
- De 16-bit ruwe waarde wordt omgezet naar voltage en daarna via **lineaire
  interpolatie** tussen kalibratiepunten naar volume in mL.

Kalibratiepunten WLS:

| Voltage (V) | Volume (mL) |
|---|---|
| 0.03 | 0 |
| 0.37 | 25 |
| 0.88 | 50 |
| 1.18 | 75 |
| 1.22 | 100 |
| 1.27 | 125 |

### 2. Ultrasoon sensor (HC-SR04) — afstandsmeting

- De sensor meet de afstand tot het wateroppervlak. Er worden 5 metingen gedaan
  en de mediaan wordt gebruikt. Mislukte metingen (geen echo) worden
  overgeslagen.
- De afstand in cm wordt via lineaire interpolatie omgezet naar volume.

Kalibratiepunten ultrasoon (let op: kleinere afstand = méér water):

| Afstand (cm) | Volume (mL) |
|---|---|
| 6.48 | 0 |
| 5.53 | 25 |
| 4.56 | 50 |
| 3.26 | 75 |
| 2.94 | 100 |
| 2.62 | 125 |

### 3. Gecombineerde schatting

`combined_volume()` neemt een **gewogen gemiddelde** van beide schattingen:

- Ultrasoon: gewicht **0.75**
- WLS: gewicht **0.25**

De ultrasoon sensor krijgt een hoger gewicht omdat de analoge water level sensor
in de praktijk minder nauwkeurig bleek (o.a. gevoelig voor vervuiling en
niet-lineair gedrag op het oppervlak). De gewichten zijn empirisch bepaald door
beide sensoren te vergelijken op bekende volumes (0–125 mL in stappen van 25 mL)
en kunnen bijgesteld worden in de functie `combined_volume()`.

## Functieoverzicht

| Functie | Doel |
|---|---|
| `median(data)` | Mediaan van een lijst meetwaarden |
| `read_water_level()` | Zet WLS aan, leest 100x, geeft mediaan terug |
| `water_level_to_voltage(level)` | 16-bit waarde → voltage |
| `voltage_to_volume(voltage)` | Voltage → mL (lineaire interpolatie) |
| `read_ultrasonic_distance()` | Leest 5x afstand, geeft mediaan terug in cm |
| `distance_to_volume(distance)` | Afstand in cm → mL (lineaire interpolatie) |
| `combined_volume(wls, us)` | Gewogen gemiddelde van beide schattingen |
