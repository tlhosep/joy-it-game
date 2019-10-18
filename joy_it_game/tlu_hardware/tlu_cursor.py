""" module: tlu_cursor
** Content **
This module shall wrap the cursor-key hardware

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-08-01 
"""

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
import logging
from django.utils.translation import gettext_lazy as _
from tlu_services import tlu_queue
from queue import Empty
from tlu_hardware.tlu_checkhardware import emulatekey
from tlu_game import tlu_globals

try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO
# Get an instance of a logger
logger = logging.getLogger(__name__)


class tlu_cursor(tlu_hardwarebase):
    """
    Provide cursorkey functionalities
    """
    def __init__(self):
        """
        Initializer, mainly sets GPIO
        """
        tlu_hardwarebase.__init__(self)
        GPIO.setup(self.button_up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        

    def lefthand_dip_setting(self):
        return 0x0F
    
    def cursorname(self,cursornum) -> str:
        """
        Helper function to translate the cursorkey number provided
        into readable text
        :param cursornum: number of key pressed
        """
        if cursornum == 100:
            return str(_("up"))
        elif cursornum == 200:
            return str(_("right"))
        elif cursornum == 300:
            return str(_("down"))
        else:
            return str(_("left"))
        
    def cursor_pressed(self) -> int:
        """
        Check if key has been pressed, if so returns code, if not returns 0
        In case no hardware is found, we will use the keyboard emulation here via remote queue
        """
        if emulatekey:
            q=tlu_globals.kbQueue
            try:
                queueobject = q.get(block=False,timeout=1)
            except Empty:
                logger.debug('key-q is empty :(')
                return 0
            except Exception as e:
                logger.debug('Exception while reading from key-q: '+str(e))
                return 0
            q.task_done() #release object from queue
            if queueobject.msg_num == tlu_queue.tlu_queue.MSG_KEYPRESSED:
                logger.debug('Cursor-pressed='+str(queueobject.msg_info))
                return queueobject.msg_info
            return 0
        if GPIO.input(self.button_up) == 0:
            return 100
        if GPIO.input(self.button_right) == 0:
            return 200
        if GPIO.input(self.button_down) == 0:
            return 300
        if GPIO.input(self.button_left) == 0:
            return 400
        return 0    #no button pressed
