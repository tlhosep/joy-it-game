""" module: tlu_matrix
** Content **
This module wraps the matrix-hardware componend and provides helper to show specific items
In case no hardware is found, the functionality would be emulated

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-31 
"""

from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
import re
import time
import logging
import tlu_hardware.tlu_threadDecorator

FakeIO=False
try:
    from luma.led_matrix.device import max7219
    from luma.core.interface.serial import spi, noop
    from luma.core.render import canvas
    from luma.core.virtual import viewport
    from luma.core.legacy import text, show_message
    from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
except ImportError:
    FakeIO=True

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class tlu_matrix(tlu_hardwarebase):
    '''
    Class for the matrix-LED-display
    '''
    serial=None 
    device=None
    def __init__(self):
        '''
        Initializer, mainly sets hardware
        '''
        tlu_hardwarebase.__init__(self)
        # create matrix device
        # cascaded = Number of cascaded MAX7219 LED matrices, default=1
        # block_orientation = choices 0, 90, -90, Corrects block orientation when wired vertically, default=0
        # rotate = choices 0, 1, 2, 3, Rotate display 0=0°, 1=90°, 2=180°, 3=270°, default=0
        if FakeIO:
            logger.info("Init")
        else:
            self.serial = spi(port=0, device=1, gpio=noop())
            self.device = max7219(self.serial, cascaded= 1, block_orientation=90, rotate= 0)
        
    def message(self,msg):
        '''
        Display the message (one by one) with a delay-rate of 4 on the one-char-display
        :param msg: Message to show
        '''
        if FakeIO:
            logger.info("Message:"+msg)
        else:
            show_message(self.device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=4)
        
    @tlu_hardware.tlu_threadDecorator.start_new_thread
    def demo(self):
        '''
        Run demo provided by joy-it scrips as a Thread
        Included to show the abilities of this module
        '''
        if FakeIO:
            logger.info("demo started")
        else:
            msg = "MAX7219 LED Matrix Demo"
            print(msg)
            show_message(self.device, msg, fill="white", font=proportional(CP437_FONT))
            time.sleep(1)
        
            msg = "Fast scrolling: Lorem ipsum dolor sit amet, consectetur adipiscing\
            elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut\
            enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut\
            aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in\
            voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint\
            occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit\
            anim id est laborum."
            msg = re.sub(" +", " ", msg)
            print(msg)
            show_message(self.device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0)
        
            msg = "Slow scrolling: The quick brown fox jumps over the lazy dog"
            print(msg)
            show_message(self.device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.1)
        
            print("Vertical scrolling")
            words = [
                "Victor", "Echo", "Romeo", "Tango", "India", "Charlie", "Alpha",
                "Lima", " ", "Sierra", "Charlie", "Romeo", "Oscar", "Lima", "Lima",
                "India", "November", "Golf", " "
            ]
        
            virtual = viewport(self.device, width=self.device.width, height=len(words) * 8)
            with canvas(virtual) as draw:
                for i, word in enumerate(words):
                    text(draw, (0, i * 8), word, fill="white", font=proportional(CP437_FONT))
        
            for i in range(virtual.height - self.device.height):
                virtual.set_position((0, i))
                time.sleep(0.05)
        
            msg = "Brightness"
            print(msg)
            show_message(self.device, msg, fill="white")
        
            time.sleep(1)
            with canvas(self.device) as draw:
                text(draw, (0, 0), "A", fill="white")
        
            time.sleep(1)
            for _ in range(5):
                for intensity in range(16):
                    self.device.contrast(intensity * 16)
                    time.sleep(0.1)
        
            self.device.contrast(0x80)
            time.sleep(1)
        
            msg = "Alternative font!"
            print(msg)
            show_message(self.device, msg, fill="white", font=SINCLAIR_FONT)
        
            time.sleep(1)
            msg = "Proportional font - characters are squeezed together!"
            print(msg)
            show_message(self.device, msg, fill="white", font=proportional(SINCLAIR_FONT))
        
            # http://www.squaregear.net/fonts/tiny.shtml
            time.sleep(1)
            msg = "Tiny is, I believe, the smallest possible font \
            (in pixel size). It stands at a lofty four pixels \
            tall (five if you count descenders), yet it still \
            contains all the printable ASCII characters."
            msg = re.sub(" +", " ", msg)
            print(msg)
            show_message(self.device, msg, fill="white", font=proportional(TINY_FONT))
        
            time.sleep(1)
            msg = "CP437 Characters"
            print(msg)
            show_message(self.device, msg)
        
            time.sleep(1)
            for x in range(256):
                with canvas(self.device) as draw:
                    text(draw, (0, 0), chr(x), fill="white")
                    time.sleep(0.1)
            
    def demo_background(self):
        '''
        Show the demo as a background-Thread
        '''
        self.demo()
    def show_symbol(self,name):
        '''
        Show a symbol on the display, provided by a specific name
        :param name: please see 'symbols' below for the current abilities
        '''
        # see https://en.wikipedia.org/wiki/Code_page_437
        symbols = {'smiley':1, 
                   'arrow_left':27,
                   'arrow_right':26,
                   'arrow_up':24,
                   'arrow_down':25,
                   'triangle_up':30,
                   'triangle_down':31,
                   'root':251,
                   'sound':14,
                   'space':32,
                   }
        if name not in symbols:
            logger.error("show symbol: "+name+" -> symbol unknown!!!")
            return
        if FakeIO:
            logger.info("show symbol: "+name+" -> "+str(symbols[name]))
        else:
            with canvas(self.device) as draw:
                text(draw,(0,0), chr(symbols[name]), fill="white")
                
    def brightness(self,level):
        '''
        Control the brightness of the display, 2 seems to be valuable
        :param level: any level between 0 and 5
        '''
        lev=level
        if lev>5 or lev<0:
            lev=5
        if FakeIO:
            logger.info("brightness: "+str(level))
        else:
            self.device.contrast(lev*16)
            
    