""" module: tlu_buttons

** Content **
This module provides the hardware commands to check for any key pressed

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-08-01 
""" 

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
import logging
from tlu_game import tlu_globals
from tlu_services import tlu_queue
from queue import Empty
from tlu_hardware.tlu_checkhardware import emulatekey

try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO

# Get an instance of a logger
logger = logging.getLogger(__name__)


class tlu_buttons(tlu_hardwarebase):
    '''
    Wrap button functionality. In case we miss the hardware, allows a keyboard-emulation
    '''
    def __init__(self):
        '''
        Initializes the class
        '''
        tlu_hardwarebase.__init__(self)
        GPIO.setmode(GPIO.BCM)

        # Die IDs der Buttons werden festgelegt
        self.buttonIDs = [[4,3,2,1],[8,7,6,5],[12,11,10,9],[16,15,14,13]]
        # GPIO Pins für die Zeilen werden deklariert.
        self.rowPins = [27,22,5,6]
        # GPIO Pins für die Spalte werden deklariert.
        self.columnPins = [13,19,26,25]

        # Definiere Vier Inputs mit pull up Widerständen.
        for i in range(len(self.rowPins)):
            GPIO.setup(self.rowPins[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # Definiere Vier Outputs und setze sie auf high.
        for j in range(len(self.columnPins)):
            GPIO.setup(self.columnPins[j], GPIO.OUT)
            GPIO.output(self.columnPins[j], 1)

    def lefthand_dip_setting(self):
        return 0xFF
       
    def button_pressed(self) -> int:
        '''
        Checks for a button pressed (1..16), if none, returns 0
        '''
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
                logger.debug('Button-pressed='+str(queueobject.msg_info))
                return queueobject.msg_info
            return 0
        for j in range(len(self.columnPins)):
            # setting each output pin to 0
            GPIO.output(self.columnPins[j],0)
            for i in range(len(self.rowPins)):
                if GPIO.input(self.rowPins[i]) == 0:
                    btnIndex = self.buttonIDs[i][j]
#                    time.sleep(0.3) #prohibit multiple key-presses at the same time
#                    logger.info("button " + str(btnIndex) + " pressed")
                    return btnIndex
            GPIO.output(self.columnPins[j],1)
        return 0    #no button pressed
 
    def cleanup(self):
        '''
        Resets GPIO
        '''
        GPIO.cleanup()