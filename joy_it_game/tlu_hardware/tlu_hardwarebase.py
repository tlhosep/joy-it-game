""" module: tlu_hardwarebase
** Content **
This module provides the base for all hardware-bound classes

** Details **
Besides defining the dip-settings that are needed in order to get the hardware working,
we also define the port-numbers we need to setup the GPI correctly

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-31 
""" 
import inspect
from tlu_hardware import tlu_hardware_global
try: 
# Check and import real RPi.GPIO library
    import RPi.GPIO as GPIO

except ImportError:
    import FakeRPi.GPIO as GPIO

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class tlu_hardwarebase(object):
    """
    Class used as a baseclass to perform certain hardware-bound activities
    Please note that the GPIO is working in BCM Mode only as the modes could not be mixed!
    """
    #buttons in bcm notation
    button_up = 26
    button_down = 13
    button_left = 25
    button_right = 19
    

    #buzzer
    buzzer_bcm = 18

    #lcd panel
    lcd_address = 0x21
    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows    = 2
    
    #led 7 segment display
    led_7seg_address = 0x70
    
    def caller_name(self):
        frame=inspect.currentframe()
        frame=frame.f_back.f_back
        code=frame.f_code
        return code.co_filename
    def prev_caller_name(self):
        frame=inspect.currentframe()
        frame=frame.f_back.f_back.f_back
        code=frame.f_code
        return code.co_filename

    def __init__(self):
        """
        Initializer, sets mode of GPIO at the first call
        """
        glob=tlu_hardware_global.globHardwareMgr.tlu_hardware_glob()
        number_of_hardware_starts = glob.increaseHardwareStarts()
        if number_of_hardware_starts == 1:
            GPIO.setmode(GPIO.BCM)
            logging.info("GPIO hardware now initialized, count="+str(number_of_hardware_starts)+" called via "+self.caller_name()+" called by "+self.prev_caller_name())
    
    def __del__(self):
        """
        Resets GPIO if needed
        """
        try:
            glob=tlu_hardware_global.globHardwareMgr.tlu_hardware_glob()
        except:
            return #in case server already stopped at cleanup-phase
#        lock = Lock()
#        with lock:
        number_of_hardware_starts = glob.decreaseHardwareStarts()
        if number_of_hardware_starts == 0:
            GPIO.cleanup()    
            logging.info("GPIO hardware now cleaned, count="+str(number_of_hardware_starts))
        
    @staticmethod
    def lefthand_dip_setting() -> int:
        """
        Default for the left DIP-switch: all buttons down (0)
        """
        return 0x00

    @staticmethod
    def righthand_dip_setting() -> int:
        """
        Default for the right DIP-switch: all buttons down (0)
        """
        return 0x00
    
    @classmethod
    def getDipHex(base_cls,cls) -> int:
        left=base_cls.lefthand_dip_setting()
        right=base_cls.righthand_dip_setting()
        try:
            left=cls.lefthand_dip_setting()
        except:
            pass
        try:
            right=cls.righthand_dip_setting()
        except:
            pass
        return (left << 8) | right

    @staticmethod
    def showdip(diphex) -> str:
        """
        Show the DIP-setting in a human readable format
        :param diphex: 8-bit code for the DIP-switch, 0=down, 1 = up
        """
        setting=0x80
        result ="|"
        for i in range(8):  # @UnusedVariable
            if (setting & diphex != 0):
                result += "°|"
            else:
                result += "_|"
            setting = setting >> 1
        return result
    
    @staticmethod
    def showleft_dip(diphex) -> str:
        """
        Show the setting for the lefthand switch in human readable format
        """
        return tlu_hardwarebase.showdip(diphex >> 8)
    
    @staticmethod
    def showright_dip(diphex) -> str:
        """
        Show the setting for the righthand switch in human readable format
        """
        return tlu_hardwarebase.showdip(diphex & 0xFF)
    