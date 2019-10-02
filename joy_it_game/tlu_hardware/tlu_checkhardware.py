""" module: tlu_checkhardware

This module shall test, if the application runs on supported hardware
If not: set emulatekey to false

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
""" 

emulatekey=False
try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO  # @UnusedImport

except ImportError:
    emulatekey=True
