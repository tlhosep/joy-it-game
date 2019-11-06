""" module: tlu_globals
** Content **
This module shall hold some global variables to be used within the hardware section

** Details **


@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-15 
"""
import logging
from multiprocessing.managers import BaseManager
from multiprocessing import Value


logger=logging.getLogger(__name__)


class Global_hardware_vars():
    """ 
    This class holds a counter to count the initialization of the single hardware
    """
    number_of_hardware_starts = Value('i',0)
    def increaseHardwareStarts(self):
        with self.number_of_hardware_starts.get_lock():
            self.number_of_hardware_starts.value += 1
        return self.number_of_hardware_starts.value 

    def decreaseHardwareStarts(self):
        with self.number_of_hardware_starts.get_lock():
            self.number_of_hardware_starts.value -= 1
        return self.number_of_hardware_starts.value 
        
#global class as we only have one hardware
class GlobHardwareManager(BaseManager):
    pass

globHardwareMgr=None


def init():
    """
    Initialization of the globally used manager.
    """
    global globHardwareMgr
    while True:
        if globHardwareMgr == None:
            GlobHardwareManager.register('tlu_hardware_glob',Global_hardware_vars)
            globHardwareMgr=GlobHardwareManager()
            globHardwareMgr.start()
            logging.debug("GlobHardwareMgr started")
            return
        else:
            try:
                globHardwareMgr.connect()
                return
            except:
                globHardwareMgr=None
                