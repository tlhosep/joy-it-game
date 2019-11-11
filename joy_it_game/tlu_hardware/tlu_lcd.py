""" module: tlu_lcd
** Content **
This module provides helper to display some text on the LCD panel

** Details **
In case there is no hardware, we emulate the display functionality

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-30 
"""

import logging
import time
import tlu_hardware.tlu_threadDecorator
from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
import inspect

try:
    import Adafruit_CharLCD as LCD
except ImportError:
    class LCD():
        address=None
        backlight=1
        msg=None
        blink=False
        cursor=False
        busnum=None
        cols=0
        lines=0
        class Adafruit_CharLCDBackpack():
            def caller_name(self):
                frame=inspect.currentframe()
                frame=frame.f_back.f_back.f_back
                code=frame.f_code
                s=code.co_filename+" via "
                frame=frame.f_back
                code=frame.f_code
                s +=  code.co_filename
                return s
            def __init__(self, address=0x20, busnum=0, cols=16, lines=2):
                self.address=address
                self.busnum=busnum
                self.cols=cols
                self.lines=lines
                print("LCD initialized: "+self.caller_name())
            def set_backlight(self, off):
                self.backlight=off
            def message(self, msg):
                self.msg=msg
                print("Message for LCD while in dummy mode:\n"+msg)
            def clear(self):
                print("Message for LCD cleared while in dummy mode")
                self.msg=""   
            def blink(self,blink):
                self.blink=blink
            def show_cursor(self,show): 
                self.cursor=show
            def move_right(self):
                pass
            def move_left(self):
                pass
        

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
        
class lcd_panel(tlu_hardwarebase):
    """
    Class to control the LCD panel (2 lines with 16 chars)
    """
    lcd=None
    def __init__(self):
        """
        Initializes the module
        """
        tlu_hardwarebase.__init__(self)
        self.lcd = LCD.Adafruit_CharLCDBackpack(address=self.lcd_address)

    def backlight(self,on):
        """
        Turns backlight of the display on or off
        :param on: True=on
        """
        if on:
            self.lcd.set_backlight(0)
        else:
            self.lcd.set_backlight(1)
        logger.info("backlight turned on: "+str(on))
        
    def clear(self):
        """
        Clears the display (display nothing)
        """
        self.lcd.clear()
        self.backlight(False)
            
    def message(self, msg):
        """
        Show provided message (up to 32 chars)
        :param msg: Ascii-message to show, max 32 chars
        """
        if len(msg)<1:
            self.lcd.clear()
        else:
#            self.lcd.clear()
            self.lcd.message(msg)
        logger.info("message set to: "+msg)
    
    def messagebyline(self,**kwargs):
        """
        As we may want to add formatting we could use this method.
        Parameters could be:
        *line1: The upper line
        *line2: the lower one
        *line1_format: left, center or rigth (to adjust the message)
        *line2_format: left, center or rigth (to adjust the message)
        """
        line1=""
        line2=""
        line1_format="left"
        line2_format="left"
        def get_format(form):
            if form=="left":
                return form
            elif form=="center":
                return form
            elif form=='right':
                return form
            else:
                return 'left'
        def justify(msg,form):
            l = len(msg)
            lx=self.lcd_columns
            fl='{:<'+str(lx)+'}'
            fc='{:^'+str(lx)+'}'
            fr='{:>'+str(lx)+'}'
            if l>lx:
                return msg[0:lx-1]
            elif form=='left':
                return fl.format(msg)
            elif form=='center':
                return fc.format(msg)
            elif form=='right':
                return fr.format(msg)    
        for key,value in kwargs.items():
            if key == "line1":
                line1=value
            elif key == "line2":
                line2=value
            elif key == "line1_format":
                line1_format=get_format(value)
            elif key == "line2_format":
                line2_format=get_format(value)
        line1=justify(line1,line1_format)
        line2=justify(line2,line2_format)
        self.message(line1+'\n'+line2)
            
    def show_cursor(self,on,blink):
        """
        Show a cursor to provide a sign that input may be required
        :param on: Turn the cursor on
        :param blink: Let the cursor blink
        """
        self.lcd.show_cursor(on)
        self.lcd.blink(blink)
        logger.info("cursor set to: "+str(on)+" Blink:"+str(blink))
            
    def move_msg(self,msg,left):
        """
        Move the message in a certain direction.
        This is useful for longer messages
        The method starts a thread for the move
        :param msg: Message to display
        :param left: move to left if true, else to the right
        """
        self.message(msg)
        
        @tlu_hardware.tlu_threadDecorator.start_new_thread
        def lcdmove(self,msg,left):
            """
            Thread to perform the movement. each move is displayed for 0.5 seconds
            :param msg: Messsage to shift
            :param left: Move to left, else right
            """
            # Demo scrolling message right/left.
            for i in range(self.lcd_columns-len(msg)):  # @UnusedVariable
                time.sleep(0.5)
                if left:
                    self.lcd.move_left()
                else:
                    self.lcd.move_right()
        lcdmove(msg, left)
        logger.info("lcd_move to left:"+str(left)+" With msg: "+msg)
          

