""" module: tlu_cursor
** Content **
This module shall wrap the touchpad hardware

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-07 
"""

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
import logging

try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO
# Get an instance of a logger
logger = logging.getLogger(__name__)

class tlu_touch(tlu_hardwarebase):
    """
    Provide cursorkey functionalities
    """
    def __init__(self):
        """
        Initializer, mainly sets GPIO
        """
        tlu_hardwarebase.__init__(self)
        GPIO.setup(self.touch_bcm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logging.info("Touch now initialized")
        
    def start(self,callback):
        GPIO.add_event_detect(self.touch_bcm, GPIO.FALLING, callback=callback, bouncetime=200)
        
    def stop(self):
        GPIO.remove_event_detect(self.touch_bcm)
