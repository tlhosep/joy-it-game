""" module: tests

This module shall try to test most of the provided io functionalities

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
"""

import unittest
import tlu_hardware.tlu_buzzer as tlu_buzzer

import logging
from tlu_hardware.tasks import Countdown, CheckKey, CheckCursor, AnimatedBuzzer, Buzzer,\
    CheckTouch
from tlu_services.tlu_queue import tlu_queueobject
from tlu_game.tlu_globals import ShowClock
from tlu_services import tlu_queue
from tlu_hardware.tlu_checkhardware import emulatekey
from tlu_game import tlu_globals
from tlu_services.tlu_threads import startThreadClass, abortThread
from tlu_hardware import tlu_hardware_global
from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase
from tlu_hardware.tlu_cursor import tlu_cursor
from tlu_hardware.tlu_buttons import tlu_buttons
import time
from tlu_hardware.tlu_vibration import tlu_vibrate
from tlu_hardware.tlu_touch import tlu_touch

logger=logging.getLogger(__name__)

class TestQueue(tlu_queue.tlu_queue):
    """
    Simple class to test the queue-functionality.
    Supports only very basic signals
    """
    def myrun(self,testio,countdown=None):
        """
        Inner loop to process the contents of the queue
        :param testio: Outer testclass to allow asserts
        """
        while True:
            queueobject = self.queue.get()
            self.queue.task_done()
            if queueobject.msg_num == self.MSG_STOP:
                logging.debug("STOP message received")
                testio.assertTrue(False,"Stop instead of Key received")
                return
            elif queueobject.msg_num == self.MSG_KEYPRESSED:
                logging.debug("KEYPRESSED message received with number "+str(queueobject.msg_info))
                key_num=queueobject.msg_info
                ok=key_num in [1,100,200,300,400]
                testio.assertTrue(ok,"Key has to be 1 or any cursor, key received="+str(key_num))
                logging.info("Key pressed processed")
                return
            elif queueobject.msg_num == self.MSG_TOUCH_PRESSED:
                logging.debug("TOUCH_PRESSED message received")
                logging.info("touch pressed processed")
                return
            elif queueobject.msg_num == self.MSG_TIMEOUT:
                # Timeout will be raised in test test_countdown_timeout
                logging.debug("TIMEOUT message received")
                return
            elif queueobject.msg_num == self.MSG_TEST:
                if queueobject.msg_info == 1:
                    if countdown != None:
                        countdown.restart()
                        logging.debug("Timer had been reset now")
                elif queueobject.msg_info == 2:
                    if countdown != None:
                        countdown.pause()
                        logging.debug("Timer paused")
                elif queueobject.msg_info == 3:
                    if countdown != None:
                        countdown.changeSecondsAndRestart(0.1)
                        logging.debug("Timer restarted")
                        
                

class TestIO(unittest.TestCase):
    """
    Test most of the I/O modules
    """
    def setUp(self):
        tlu_globals.init()
        tlu_hardware_global.init()
        if emulatekey and self._testMethodName=="test_checkkey" :
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,1)
            tlu_globals.kbQueue.put(obj)
        elif emulatekey and self._testMethodName=="test_checkcursor":
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,100)
            tlu_globals.cqueue.put(obj)
        elif emulatekey and self._testMethodName=="test_checktouch":
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_TOUCH_PRESSED)
            tlu_globals.tqueue.put(obj)
        
     
    def test_buzzer(self):
        """
        Test some basic buzzer settings
        """
        logging.debug('Test started')
        buz=tlu_buzzer.tlu_buz()
        self.assertFalse(buz.noise, "The startup status has to be false")
        buz.sound(True)
        self.assertTrue(buz.noise, "Buzzer should sound now")
        buz.sound(False)
        self.assertFalse(buz.noise, "The ending status has to be false")
        logging.debug('Test may have passed')

    def test_vibration(self):
        """
        Test some basic vibration settings
        """
        logging.debug('Test started')
        if not emulatekey:
            diphex=tlu_hardwarebase.getDipHex(tlu_vibrate)
            print('\nFor vibration check the dip-settings to be like this:')
            print('Left: '+tlu_hardwarebase.showleft_dip(diphex)+' Right: '+tlu_hardwarebase.showright_dip(diphex))
            time.sleep(5)
        vib=tlu_vibrate()
        self.assertFalse(vib.vibration, "The startup status has to be false")
        vib.vibrate(True)
        self.assertTrue(vib.vibration, "Board should vibrate now")
        time.sleep(0.1)
        vib.vibrate(False)
        self.assertFalse(vib.vibration, "The ending status has to be false")
        logging.debug('Test may have passed')
    
    def stop(self,process,msg=''):
        """
        Service-function to abort the running process
        :param process: Process to be aborted
        :param msg: Log-Message in case anything got wrong
        """
        self.assertTrue(abortThread(process,1,msg),"Task could not be stopped:"+str(msg))
    def mytest_clock(self):
        """
        Testing the clock-process
        """
        sc=ShowClock
        startThreadClass(sc)
        self.assertNotEqual(sc, None, "Process could not be established")
        self.stop(sc, "test_clock")
    def test_countdown(self):
        """
        Test countdown display process in general
        """
        queue=TestQueue()
        cd=Countdown(queue, 1.0)
        startThreadClass(cd)
        self.assertNotEqual(cd, None, "Process could not be established")
        self.stop(cd, "test_countdown")
    def test_countdown_timeout(self):
        """
        Test countdown with timeout-event
        """
        queue=TestQueue()
        cd=Countdown(queue, 0.2)
        startThreadClass(cd)
        self.assertNotEqual(cd, None, "Process could not be established")
        queue.myrun(self) #breaks/terminates once timeout reached
        self.stop(cd, "test_countdown_timeout")
    def test_countdown_reset(self):
        """
        Test countdown with reset-event
        """
        queue=TestQueue()
        cd=Countdown(queue, 0.1)
        startThreadClass(cd)
        self.assertNotEqual(cd, None, "Process could not be established")
        queueobject=tlu_queueobject(tlu_queue.tlu_queue.MSG_TEST,1)
        queue.send(queueobject) #forces timer reset
        queue.myrun(self,cd) #breaks/terminates once timeout reached
        self.stop(cd, "test_countdown_reset")
    def test_countdown_pause(self):
        """
        Test countdown with pause and restart-event
        """
        queue=TestQueue()
        cd=Countdown(queue, 0.1)
        startThreadClass(cd)
        self.assertNotEqual(cd, None, "Process could not be established")
        queueobject=tlu_queueobject(tlu_queue.tlu_queue.MSG_TEST,2)
        queue.send(queueobject) #forces timer oause
        queueobject=tlu_queueobject(tlu_queue.tlu_queue.MSG_TEST,3)
        queue.send(queueobject) #forces timer restart
        queue.myrun(self,cd) #breaks/terminates once timeout reached
        self.stop(cd, "test_countdown_pause")
    def test_checkkey(self):
        """
        Test to press the upper left key or by keyboard using the '1'
        """
        logging.debug('test_checkkey started')
        queue=TestQueue()
        if not emulatekey:
            diphex=tlu_hardwarebase.getDipHex(tlu_buttons)
            print('\nFor Keys check the dip-settings to be like this:')
            print('Left: '+tlu_hardwarebase.showleft_dip(diphex)+' Right: '+tlu_hardwarebase.showright_dip(diphex))
            time.sleep(5)
            print('Press the upper left key of the 16key-field')
        ck=CheckKey(queue, 15.0)
        startThreadClass(ck)
        self.assertNotEqual(ck, None, "Process could not be established")
        queue.myrun(self) #breaks/terminates once timeout reached or key pressed ;)
        logging.debug('test_checkkey had key')
        self.stop(ck, "test_checkkey")
        logging.debug('test_checkkey ended')
    def test_checkkequeue(self):
        """
        test the general queue-functionality
        """
        queue=TestQueue()
        queueobject=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,1)
        queue.send(queueobject)
        queue.close()
        queue.myrun(self)
    def test_buzzerProcess(self):
        """
        Test if the buzzer makes a sound
        """
        buz=Buzzer(0.1)
        self.assertNotEqual(buz, None, "Process could not be established")
        startThreadClass(buz)
        abortThread(buz,0.5, "test_buzzerProcess")
    def test_animatedbuzzer(self):
        """
        Test if the buzzer makes a sound while the led display showns sign
        """
        ab=AnimatedBuzzer(1.0)
        self.assertNotEqual(ab, None, "Process could not be established")
        startThreadClass(ab)
        abortThread(ab,1,"animatedBuzzer_class")
        self.assertFalse(ab.is_alive(),"AnimatedBuzzer should have been stopped...")
    def test_checkcursor(self):
        """
        Wait for any of the 4 cursor-keys being pressed
        """
        queue=TestQueue()
        if not emulatekey:
            diphex=tlu_hardwarebase.getDipHex(tlu_cursor)
            print('\nFor cursor check the dip-settings to be like this:')
            print('Left: '+tlu_hardwarebase.showleft_dip(diphex)+' Right: '+tlu_hardwarebase.showright_dip(diphex))
            time.sleep(5)
            print('Please press any of the four cursor-keys to continue')
        cc=CheckCursor(queue, 5.0)
        startThreadClass(cc)
        self.assertNotEqual(cc, None, "Process could not be established")
        queue.myrun(self) #breaks/terminates once timeout reached or key pressed ;)
        logging.debug('test_checkkey had cursor')
        self.stop(cc, "test_checkcursor")
    def test_checktouch(self):
        """
        Wait for touchpad being touched
        """
        queue=TestQueue()
        if not emulatekey:
            time.sleep(1)
            print('\nPlease touch the touchpad to continue...')
        ct=CheckTouch(queue, 5.0)
        startThreadClass(ct)
        self.assertNotEqual(ct, None, "Process could not be established")
        queue.myrun(self) #breaks/terminates once timeout reached or key pressed ;)
        logging.debug('test_chektouch had touch')
        self.stop(ct, "test_checktouch")

if __name__ == '__main__':
    unittest.main()