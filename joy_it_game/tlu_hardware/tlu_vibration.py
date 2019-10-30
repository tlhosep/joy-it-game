""" module: tlu_vibration
** Content **
This module shall vibrate the board upon error

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-30 
""" 

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase


try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO

class tlu_vibrate(tlu_hardwarebase):
    """"Provides buzzer sound
    """
    vibration=False
    def __init__(self):
        tlu_hardwarebase.__init__(self)
        GPIO.setup(self.vibration_bcm, GPIO.OUT)
        
    @staticmethod
    def righthand_dip_setting() -> int:
        """
        Right DIP-switch: all switches down (0) except switch 1 (leftmost)
        """
        return 0x80

        
    def vibrate(self, on):
        """
        Turns vibration on or off
        :param on: True: Vibrate, else silence
        """
        if on:
            GPIO.output(self.vibration_bcm, GPIO.HIGH)
            self.vibration=True
        else:
            GPIO.output(self.vibration_bcm, GPIO.LOW)
            self.vibration=False