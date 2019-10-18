""" module: tlu_buzzer
** Content **
This module shall make a sound

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase


try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO

class tlu_buz(tlu_hardwarebase):
    """"Provides buzzer sound
    """
    noise=False
    def __init__(self):
        tlu_hardwarebase.__init__(self)
        GPIO.setup(self.buzzer_bcm, GPIO.OUT)
        
    def sound(self, on):
        """
        Turns sound on or off
        :param on: True: Make noise, else silence
        """
        if on:
            GPIO.output(self.buzzer_bcm, GPIO.HIGH)
            self.noise=True
        else:
            GPIO.output(self.buzzer_bcm, GPIO.LOW)
            self.noise=False