""" module: tlu_led
** Content **
Module to support the 7-segment LED display

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-31 
"""

import datetime
import logging

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase

# Get an instance of a logger
logger = logging.getLogger(__name__)

fakeIO=False
try:
    from Adafruit_LED_Backpack import SevenSegment
except ImportError:
    fakeIO=True
    class SevenSegment():
        address = 0x00
        def __init__(self, invert=False, **kwargs):
            for key,value in kwargs.items():
                if key == "address":
                    self.address=value
                    
        def begin(self):
            logger.info("7 segments now initialized")
        def clear(self):
            logger.debug("Clear called")
        def set_digit(self,digit, value):
            pass
#            logger.info("digit #"+str(digit)+" set to:"+str(value))
        def set_colon(self,on):
            logger.debug("Colon set to:"+str(on))
        def write_display(self):
            logger.debug("Show display")
            
class seven_segment(tlu_hardwarebase):
    """
    Class to handle the 7-segment LED display
    """
    segment=None
    stop=False
    def __init__(self):
        """
        Initializes the hardware
        """
        tlu_hardwarebase.__init__(self)
        if fakeIO:
            self.segment = SevenSegment(address=self.led_7seg_address)
        else:
            self.segment = SevenSegment.SevenSegment(address=self.led_7seg_address)
        self.segment.begin()
        self.segment.clear()
        self.segment.write_display()
    def set4digits(self,number,colon):
        """
        Show the number (range 0...9999) given
        :param number: number to display
        :param colon: show the colon in the middle if True
        """
        self.segment.clear()
        # Set left 2 digits
        self.segment.set_digit(0, int(number / 1000))     # Thousands
        self.segment.set_digit(1, int(int(number/100) % 10))      # Hundreds
        # Set right 2 digits
        self.segment.set_digit(2, int((number%100) / 10)) # Tens
        self.segment.set_digit(3, int(number % 10))            # Ones
        self.segment.set_colon(colon)
        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        self.segment.write_display()
        logger.debug("4 digits set for "+str(number))
    def set2numbers(self,left,right,colon):
        """
        Sets two distinct numbers (each range 0..99)
        :param left: lefthand number
        :param right: righthand number
        :param colon: show the colon in the middle if True
        """
        self.segment.clear()
        # Set left two digits
        self.segment.set_digit(0, int(left / 10))     # Tens
        self.segment.set_digit(1, left % 10)          # Ones
        # Set right 2 digits
        self.segment.set_digit(2, int(right / 10))    # Tens
        self.segment.set_digit(3, right % 10)         # Ones
        self.segment.set_colon(colon)
        self.segment.write_display()
        logger.debug("2 numbers set. #1:"+str(left)+" #2:"+str(right))
    def current_time(self,colon):
        """
        Show the current local time (hours/minutes) and allow the colon to blink for the seconds
        :param colon: True: display colon
        """
        self.segment.clear()
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        self.set2numbers(hour, minute, colon)
        self.segment.write_display()
                             
    def showClock(self):
        """
        Show the current time and let the colon blink
        This method has to be called at least every 0.5 seconds to have a working time
        """
        now = datetime.datetime.now()
        second = now.second
        self.current_time(second % 2)

    def clear(self):
        """
        Resets the display to show nothing
        """
        self.segment.clear()
        self.segment.write_display()
     
            