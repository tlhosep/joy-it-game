""" module: tlu_globals
** Content **
This module shall hold some global variables

** Details **
Besides some hardware-bound tasks here we also find the listener for external keyboard-queue events.
These will be performed via a separate coammandline interface that sends events via a remote queue

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-09-30 
"""
from tlu_hardware import tlu_lcd, tlu_led, tlu_matrix, tlu_hardware_global
from tlu_services.tlu_threads import abortThread, startThreadClass
import logging
from multiprocessing import JoinableQueue
from multiprocessing.managers import BaseManager
import time
from threading import Thread
from tlu_hardware.tlu_checkhardware import emulatekey


logger=logging.getLogger(__name__)


class ShowClock(Thread):
    """ Thread to display the time

    Show a clock on the 7-segment LED display
    Display is updated every 0.25 seconds to show the blinking sign for seconds
    """
    def __init__(self):
        Thread.__init__(self)
        self.sevenseg=tlu_led.seven_segment()

    def run(self, *args, **kwargs):
        logger.info("ShowClock started: "+str(self))
        while True:
            time.sleep(0.25)
            self.sevenseg.showClock()
            if getattr(self, "is_aborted", False):
                self.sevenseg.clear()
                logger.info('ShowClock terminated: '+str(self))
                return
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        self.sevenseg.clear()
        logger.info('ShowClock termination requested: '+str(self))

global_clock_thread=None

class Global_vars():
    """ This class holds hardware-components to be used throughout the game
    From all processes you are allowed to set the LCD and the matrix.
    Here you could also start the clock display
    
    """
    global_lcd = None
    global_matrix=None
    def __init__(self):
        logging.info("Global_vars: Init")
        tlu_hardware_global.init()
        self.global_lcd = tlu_lcd.lcd_panel()
        self.global_matrix = tlu_matrix.tlu_matrix()
    
    def lcdMessagebyline(self,line1,line2,line1Format='center',line2Format='center'):
        """
        Show a message on the LCD screen with backlight turned on
        :param line1: Message for line 1
        :param line2: Message for line 2
        :param line1Format: default is center
        :param line2Format: default is center
        """
        self.global_lcd.backlight(True)
        self.global_lcd.messagebyline(line1=line1,line2=line2,line1_format=line1Format,line2_format=line2Format)
    
    def _singleTest(self,testvalue,msg):
        """
        For internal testing purposes only, returns True in case tests has passed.
        If not, displays message in terminal
        :param testvalue: Value to test for None
        :param msg: Message to show in case of an error
        """
        if testvalue==None:
            print(msg)
            return False
        return True
    def test(self):
        """
        For tests only to make sure that the globals do work as expected
        """
        if not self._singleTest(self.global_lcd, "There has to be an lcd"):
            return False
        if not self._singleTest(self.global_matrix, "There has to be an matrix"):
            return False
        return True
 
    def matrixShow_symbol(self,symbol):
        """
        Show a specific symbol ion the LED matrix
        
        :param symbol: Name of symbol to display (see tlu_matrix for details)
        """
        self.global_matrix.brightness(2)
        self.global_matrix.show_symbol(symbol)
    
    def startClock(self):
        """ 
        shows the clock on the 7-seg display
        """
        global global_clock_thread
        if global_clock_thread == None:
            clock=ShowClock()
            startThreadClass(clock)
            global_clock_thread=clock  
            logging.debug("Clock now showing: "+str(clock))
    
    def stopClock(self):
        """ 
        stops the clock from showing
        Needed in order to use the display for other activities :)
        """
        global global_clock_thread
        if global_clock_thread != None:
            abortThread(global_clock_thread)
            logging.debug("Clock now hiding: "+str(global_clock_thread))
        global_clock_thread=None
               
    def cleanup(self):
        """
        stops all threads, turns hardware off        
        """
        self.global_lcd.clear()
        self.global_matrix.show_symbol('space')  #turning it off
        self.stopClock()

        
#global class as we only have one hardware
class GlobManager(BaseManager):
    pass
class KbQueueManager(BaseManager):
    pass

kbQueue=None
globMgr=None
kbmgr=None

def init():
    """
    Initialization of several globally used managers.
    At least we have the global-manager to allow to call the hardware settings.
    In a local test-environment we could also emulate the keys by keyboard-commands.
    Therefore we also start a Listener in these scenarios to accept keystrokes via a remote-queue
    (see sendKeys-commandline interface)
    """
    global kbQueue
    global globMgr
    global kbmgr
    if globMgr == None:
        GlobManager.register('tlu_glob',Global_vars)
        globMgr=GlobManager()
        globMgr.start()
        logging.debug("GlobMgr started")
    if emulatekey and kbQueue == None:
        kbQueue = JoinableQueue()
        KbQueueManager.register('get_kbQueue', callable=lambda:kbQueue)
        kbmgr = KbQueueManager(address=('', 50200),authkey=b'tlu_abracadabra')
        kbmgr.start()
        logging.debug("KeyboardQueueMgr started")
