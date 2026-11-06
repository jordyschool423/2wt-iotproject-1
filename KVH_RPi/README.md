Voor deze code heb je een aantal dependenties nodig om deze te doen werken

--- Via apt ---
picamera2
opencv-python


--- in de environ met pip---
pip install torch (cpu)          ← eerst, voor de CPU versie van Pytorch (zeker niet de GPU-versie)
pip install ultralytics --no-deps ← tweede, maar zonder dat hij zelf deps gaat regelen

-> Dependencies
pip install ultralytics-thop psutil polars pillow pyyaml requests matplotlib numpy

Na de installation krijg je waarschijnlijk de errormeldingen van nvidia dependencies. Deze mag je negeren aangezien we niet met GPU werken. 

