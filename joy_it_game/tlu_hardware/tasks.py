""" module: tasks

** Content **
A collection of thread-objects that perform certain hardware-bound tasks

** Details **
We have a Countdown, Buzzer, Key, Cursor aso Object here...

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 
from __future__ import absolute_import

from tlu_hardware import tlu_led,tlu_buttons,tlu_buzzer,tlu_matrix, tlu_cursor,\
    tlu_hardware_global, tlu_touch
import time
import logging
from tlu_services.tlu_queue import tlu_queueobject, tlu_queue
from threading import Thread
from tlu_game import tlu_globals
from datetime import datetime
from tlu_hardware.tlu_vibration import tlu_vibrate
from tlu_hardware.tlu_checkhardware import emulatekey
from queue import Empty
from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase

logger = logging.getLogger(__name__)


            
class Countdown(Thread):
    """
    Provides a countdown display (tenths seconds) on 7-segment
    Once timer is run to zero a timeout message would be send to the provided queue
    """
    def __init__(self, queue, seconds):
        """
        Defines the queue where the timeout message would be send to and the amount of seconds the level should last
        :param queue: Message-Queue for Timeout message
        :param seconds: Seconds to wait until timeout, max 99 seconds allowed
        """
        Thread.__init__(self)
        self.is_aborted=False
        self.has_to_restart=False
        self.paused = seconds<0
        if seconds > 999:
            seconds = 999
        if seconds <= 0:
            seconds = 0.1
        self.tenths=int(seconds*10)
        self.queue=queue
        self.sevenseg=tlu_led.seven_segment()
        tlu_globals.init()
        tlu_hardware_global.init()
        glob=tlu_globals.globMgr.tlu_glob()
        glob.stopClock() #terminate Clock in case it is showing
    

    def run(self, *args, **kwargs):
        logger.info("Countdown started with tenths="+str(self.tenths)+" paused="+str(getattr(self, "paused", False)))
        t0=datetime.now()
        diff=0
        while diff < self.tenths:
            if getattr(self, "has_to_restart", False):
                t0=datetime.now()
                logger.info('Countdown restarted')
                diff=0
                self.has_to_restart=False
                self.paused=False
            if getattr(self, "paused", False):
                t0=datetime.now()
                diff=0
                self.sevenseg.clear()
                time.sleep(0.5)
                continue
            self.sevenseg.set4digits(int(self.tenths-diff), 0)
            time.sleep(0.1)
            t1=datetime.now()
            diff = int((t1-t0).total_seconds() * 10)
            if getattr(self, "is_aborted", False):
                self.sevenseg.clear()
                logger.info('Countdown aborted')
                return 
        logger.info('Countdown ended with diff='+str(diff))
        queueobject=tlu_queueobject(tlu_queue.MSG_TIMEOUT)
        self.queue.send(queueobject)
        return Thread.run(self, *args, **kwargs)
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        logger.info('Countdown termination requested')
    def pause(self):
        self.paused=True
        logger.info("Countdown paused")
    def restart(self):
        self.has_to_restart=True
    def changeSecondsAndRestart(self, seconds):
        if seconds > 999:
            seconds = 999
        if seconds <= 0:
            seconds = 0.1
        self.tenths=int(seconds*10)
        self.has_to_restart=True
 
class CheckKey(Thread):
    """
    Check for any key pressed on the board. Once a key is pressed or released a message will be 
    created and send to the provided queue
    """
    def __init__(self, queue, limit=None):
        """
        Initializes the Thread.
        :param queue: Queue to receive the key-messages or a tiemout , if set
        :param limit: Default none, else seconds to wait for a key before a timeout is sent to the queue
        """
        Thread.__init__(self)
        self.is_aborted=False
        self.buttons=tlu_buttons.tlu_buttons()
        if limit != None:
            self.count=int(limit*5) #to reach seconds
        else:
            self.count=None
        self.currentKey=0
        self.button_values=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
        self.queue=queue
        
    def run(self, *args, **kwargs):
        logger.info("Checking for Key pressed in background")
        
        while True:
            if (self.count != None):
                self.count -= 1
                logger.debug("Requesting button with count = "+str(self.count))
                if self.count < 1:
                    queueobject=tlu_queueobject(tlu_queue.MSG_TIMEOUT)
                    self.queue.send(queueobject)
                    logger.info("Buttons no longer checked due to timeout")
                    return
            if getattr(self, "is_aborted", False):
                queueobject=tlu_queueobject(tlu_queue.MSG_STOP)
                self.queue.send(queueobject)
                logger.info("Buttons no longer checked due to abort")
                return
            time.sleep(0.1) #reduce load
            button=self.buttons.button_pressed()
            if button not in self.button_values:
                continue
            if button != self.currentKey:
                if (self.currentKey == 0) and (button > 0):
                    #pressed
                    self.currentKey=button
                    queueobject=tlu_queueobject(tlu_queue.MSG_KEYPRESSED,button)
                    self.queue.send(queueobject)
                    logger.info("Key pressed: "+str(button))
                elif (self.currentKey > 0) and (button == 0):
                    #released
                    queueobject=tlu_queueobject(tlu_queue.MSG_KEYRELEASED,self.currentKey)
                    self.queue.send(queueobject)
                    logger.info("Key released: "+str(self.currentKey))
                    self.currentKey=button #indicate release
        return Thread.run(self, *args, **kwargs)    
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        logger.info('CheckKey termination requested')

class Buzzer(Thread):
    """
    Make the buzzer sound
    """
    def __init__(self,duration_seconds): 
        """
        Initialization
        :param duration_seconds: Duration of sound in seconds
        """
        Thread.__init__(self)
        self.is_aborted=False
        self.tenth=10*duration_seconds
        self.buz=tlu_buzzer.tlu_buz()
        
    def run(self, *args, **kwargs):
        logger.info('Buzzer started with duration='+str(self.tenth))
        self.buz.sound(True)
        while (self.tenth > 0) and (not getattr(self, "is_aborted", False)):
            time.sleep(0.1)
            self.tenth -= 1
        self.buz.sound(False)
        return Thread.run(self, *args, **kwargs)    
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        self.buz.sound(False)
        logger.info('Buzzer termination requested')

class AnimatedBuzzer(Thread):
    """
    Buzzer with symbols shown on the matrix.
    You see a note while the buzzer sounds, followed by a space once done
    """
    def __init__(self, duration_seconds):
        """
        Initialization
        :param duration_seconds: Duration of the sound in seconds
        """
        Thread.__init__(self)
        self.is_aborted=False
        logger.info('animated buzzer started with duration='+str(duration_seconds))
        self.matrix=tlu_matrix.tlu_matrix()
        self.matrix.brightness(2)
        self.matrix.show_symbol('sound')
        self.buz=tlu_buzzer.tlu_buz()
        self.tenth=duration_seconds*10
        
    def run(self):
        logger.info('animated buzzer started with duration='+str(self.tenth))
        self.buz.sound(True)
        while (self.tenth > 0):
            time.sleep(0.1)
            self.tenth -= 1
            if getattr(self, "is_aborted", False):
                logger.debug("Aborting AnimatedBuzzer")
                break
        self.buz.sound(False)
        if getattr(self, "is_aborted", False):
            self.matrix.show_symbol('space')
        else:
            self.matrix.show_symbol('root')
        logger.info('animated buzzer ended')
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        self.buz.sound(False)
        logger.info('animated buzzer termination requested')
 
class CheckCursor(Thread):
    """
    Checks for cursor-key input
    """
    def __init__(self, queue, limit=None):
        """
        Initializes the Thread.
        :param queue: Queue to receive the cursorkey-messages or a tiemout , if set
        :param limit: Default none, else seconds to wait for a cursorkey before a timeout is sent to the queue
        """
        Thread.__init__(self)
        self.is_aborted=False
        self.cursorkeys=tlu_cursor.tlu_cursor()
        if limit != None:
            self.count=int(limit*10)
        else:
            self.count=None
        self.currentKey=0
        self.cursor_values=(0,100,200,300,400)
        self.queue=queue
    def run(self, *args, **kwargs):
        logger.info("Checking for Cursor-Key pressed in background")
        while True:
            if (self.count != None):
                self.count -= 1
                if self.count < 1:
                    logger.info("exiting cursor-check due to retry-limit reached")
                    queueobject=tlu_queueobject(tlu_queue.MSG_TIMEOUT)
                    self.queue.send(queueobject)
                    return
            time.sleep(0.1)
            if getattr(self, "is_aborted", False):
                logger.info("Cursor-Keys no longer checked")
                queueobject=tlu_queueobject(tlu_queue.MSG_STOP)
                self.queue.send(queueobject)
                return
            if self.count != None:
                logger.debug("requesting cursor key  with count "+str(self.count))
            cursorkey=self.cursorkeys.cursor_pressed()
            if cursorkey not in self.cursor_values:
                continue
            if cursorkey != self.currentKey:
                if (self.currentKey >= 0) and (cursorkey == 0):
                    #released
                    queueobject=tlu_queueobject(tlu_queue.MSG_KEYRELEASED,self.currentKey)
                    self.queue.send(queueobject)
                    logging.info("Cursor released: "+str(self.currentKey))
                if (cursorkey > 0):
                    #pressed
                    queueobject=tlu_queueobject(tlu_queue.MSG_KEYPRESSED,cursorkey)
                    self.queue.send(queueobject)
                    logging.info("Cursor presssed: "+str(cursorkey))
                self.currentKey=cursorkey
        return Thread.run(self, *args, **kwargs)
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        logger.info('CheckCursor termination requested')
        
class Vibrate(Thread):
    """
    Make tvibration
    """
    def __init__(self,duration_seconds): 
        """
        Initialization
        :param duration_seconds: Duration of sound in seconds
        """
        Thread.__init__(self)
        self.is_aborted=False
        self.tenth=10*duration_seconds
        self.vib=tlu_vibrate()
        
    def run(self, *args, **kwargs):
        logger.info('Vibration started with duration='+str(self.tenth))
        self.vib.vibrate(True)
        while (self.tenth > 0) and (not getattr(self, "is_aborted", False)):
            time.sleep(0.1)
            self.tenth -= 1
        self.vib.vibrate(False)
        return Thread.run(self, *args, **kwargs)    
    def terminate(self, *args, **kwargs):
        self.is_aborted=True
        self.vib.vibrate(False)
        logger.info('vibration termination requested')

touch_queue=None
def do_touch_check(channel):
    global touch_queue
    queueobject=tlu_queueobject(tlu_queue.MSG_TOUCH_PRESSED)
    touch_queue.send(queueobject)
    logging.info("Touchpad pressed ")
    
class CheckTouch(Thread):
    """
    Checks for cursor-key input
    """
    def __init__(self, queue, limit=None):
        """
        Initializes the Thread.
        :param queue: Queue to receive the touchpad-messages or a tiemout , if set
        :param limit: Default none, else seconds to wait for a touchpad-event before a timeout is sent to the queue
        """
        global touch_queue
        Thread.__init__(self)
        self.is_aborted=False
        self.touch=tlu_touch.tlu_touch()
        if limit != None:
            self.count=int(limit*10)
        else:
            self.count=None
        self.queue=queue
        touch_queue=queue
    def run(self, *args, **kwargs):
        logger.info("Checking for Touchpad touched in background")
        self.touch.start(do_touch_check)
        while True:
            if (self.count != None):
                self.count -= 1
                if self.count < 1:
                    self.touch.stop()
                    logger.info("exiting touch-check due to retry-limit reached")
                    queueobject=tlu_queueobject(tlu_queue.MSG_TIMEOUT)
                    self.queue.send(queueobject)
                    return
            time.sleep(0.1)
            if getattr(self, "is_aborted", False):
                self.touch.stop()
                logger.info("Touchpad no longer checked")
                queueobject=tlu_queueobject(tlu_queue.MSG_STOP)
                self.queue.send(queueobject)
                return
            if self.count != None:
                logger.debug("requesting touchpad pressed with count "+str(self.count))
            if emulatekey:
                q=tlu_globals.tqueue
                try:
                    queueobject = q.get(block=False,timeout=1)
                except Empty:
                    logger.debug('touch-q is empty :(')
                    continue
                except Exception as e:
                    logger.warn('Exception while reading from key-q: '+str(e))
                    queueobject=tlu_queueobject(tlu_queue.MSG_STOP)
                    self.queue.send(queueobject)
                    return
                if queueobject.msg_num == tlu_queue.MSG_TOUCH_PRESSED:
                    do_touch_check(tlu_hardwarebase.touch_bcm)
                q.task_done() #release object from queue
        return Thread.run(self, *args, **kwargs)
    def terminate(self, *args, **kwargs):
        self.touch.stop()
        self.is_aborted=True
        logger.info('CheckCursor termination requested')
