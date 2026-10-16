# project automatische drinkbak

In dit project staat alle code van ons project voor het vak IOT-essentials.

Hierbij realiseren wij een drinkbak voor huisdieren die zichzelf automatisch bijvult als hij te leeg is.
Alle data zoals niveau's van de drinkbak, reserve reservoir, aantal keren gedronken zal worden gemonitord en online bereikbaar zijn.


## aankopen
- [ ] niveau sensor(2x)
- [ ] waterpomp
- [ ] ...


## programmeren
- [ ] uitlezen van de niveau sensoren
- [ ] uitlezingen in een formaat wegschrijven om door te sturen naar webapp
- [ ] api voor communicatie tussen pi en webapp
- [ ] aansturing van leds(of eventueel andere leuke manieren) om data op het model weer te geven


## eventuele ideeen

- fysieke aflezing van het reservoir met leds
- fysieke aflezing van het reservoir met lcd
- drukknop om reservoir bijgevuld door te geven
- in geval van display -> drukknop om display aan te zetten en de data door te sturen naar display


## KVH-pico
Ik werk met een relais zodat de sensor niet constant stroom krijgt. Dit voorkomt variatie in voltages ten gevolge van temperatuurswisselingen en elektrolyse. De relais opent het circuit kort.

Main.py werkt hetzelfde op een pico als code.py, dat is het programma dat runned bij startup. Ik heb mijn endless loop zo gemaakt dat je eerst op enter moet duwen voor die zijn actie uitvoert.

Waterbowl.py heb ik gemaakt om de code van de sensor appart te zetten, zodat alles wat overzichtelijker blijft. Deze wordt geïmport in main.py om de functies aan te kunnen spreken. Hier open ik het circuit eerst voor 5 seconden via de relais (om de sensor te stabiliseren) en dan voor ik 100 metingen uit op 1seconde. Daarvan neem ik de mediaan en die stuur ik terug. Dit onderdrukt ruis en uitschieters.

Daarnaast heb ik een schema getekend zodat we dit systeem kunnen nabouwen.
