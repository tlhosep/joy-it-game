""" module: tlu_level04
** Content **
Class to form the fourth level of the game

** Details **
In this level the player has to touch the touchpad and is receiving these instructions
1) Press random Key within 3 seconds
2) Touch again within 1 second
3) Press random Key within 2.5 seconds
4) Press random Key within 1.5 seconds

- state 0: Baseinstructions
- state 1: wait for touch
- => touchevent
- state 2: wait for key
- => keyevent
- state 3: wait for touch
- => touchevent
- state 4 wait for touch
- => touchevent
- state 5: wait for touch
- => touchevent
- state 6: wait for key
- => keyevent
- state 7: wait for touch
- touchevent
- state 8: wait for key
- keyevent
- state 9: done
 
@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-11-08 
"""

import logging
from django.utils.translation import gettext as _
from django.utils import timezone, translation
from tlu_joyit_game.models import Level

from tlu_joyit_game import models

from tlu_hardware.tasks import Countdown, CheckKey, Buzzer, CheckTouch
from tlu_game.tlu_levelbase import LevelBase
import threading
from tlu_services.tlu_threads import abortThread, startThreadClass
from tlu_game import tlu_globals
from random import randint
from tlu_services.tlu_queue import tlu_queue
import time

logger=logging.getLogger(__name__)


class Level04(LevelBase):
    """ Fourth Level of the game
    Touch and follow the instructions
    """
    class GameQueue(LevelBase.GameQueue):
        def msg(self,gameProcess,msg,progress,key=-1,error=False):
            status=models.getGameState(gameProcess.user_id)
            status.msg=msg
            if key > -1:
                status.msg += str(key)
            if error:
                status.result=Level.DIDNOTFINISH
            status.level_progress=progress
            models.setGameState(gameProcess.user_id, status)
        def checktouch(self,queueobject,state,gameProcess,stop_event):
            if queueobject.msg_num == self.MSG_TOUCH_PRESSED:
                return state + 1
            else:
                self.msg(gameProcess,str(_("Sorry, wrong key!")),int(state/12),-1,True)
                stop_event.set()
                return -1

            
        def run(self, stop_event, gameProcess, hardware, language):
            """ Queue loop for level 4
            Main
            :param stop_event: event coming from main-loop, once set, level will terminate
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param hardware: list of started threads
            """
            translation.activate(language)
            self.clearQueue() #cleanup before we start
            key=-1
            state=1
            thread=threading.currentThread()
            (timer, kbd, touch,) = hardware  # @UnusedVariable
            glob=tlu_globals.globMgr.tlu_glob()
            #state 0: Baseinstructions
            self.msg(gameProcess,_("Please touch the touchpad to start"),int(state/12))
            while True:
                if state>8:
                    stop_event.set()
                    break
                if key == -1:
                    key=randint(1,16)
                
                (queueobject,breakIndicator)=self.getQueueObject(stop_event, gameProcess, thread)
                if breakIndicator:
                    break
                if queueobject == None:
                    continue
                self.queue.task_done() #release object from queue
                if self.checkAbort(stop_event,gameProcess,thread,queueobject):
                    if queueobject.msg_num==tlu_queue.MSG_TIMEOUT:
                        glob.lcdMessagebyline(str(_("Level: "))+"04", str(_("Timeout"))+" :(")
                    break
                logging.info("State="+str(state)+" "+str(queueobject))
                if queueobject.msg_num==tlu_queue.MSG_KEYRELEASED:
                    #skip this event
                    continue
                if state == 1:
                    #state 1: wait for touch
                    state = self.checktouch(queueobject,state,gameProcess,stop_event)
                    if -1 == state:
                        break
                    self.msg(gameProcess,str(_("Please press key #")),int(state/8),key)
                    timer.changeSecondsAndRestart(3)
                elif state == 2:
                    #state 3: wait for key
                    if (queueobject.msg_num == self.MSG_KEYPRESSED) and (key == queueobject.msg_info):
                        timer.pause()
                        key = -1
                        self.msg(gameProcess,str(_("Please touch to continue")),int(state/8))
                        state += 1
                    else:
                        timer.pause()
                        self.msg(gameProcess,str(_("Sorry, wrong key!")),int(state/8),-1,True)
                        stop_event.set()
                        break
                elif state == 3:
                    #state 3: wait for touch
                    state = self.checktouch(queueobject,state,gameProcess,stop_event)
                    if -1 == state:
                        break
                    self.msg(gameProcess,str(_("Please press touch two times within 4 seconds")),int(state/8))
                    timer.changeSecondsAndRestart(4)
                elif state == 4:
                    #state 4 wait for touch
                    state = self.checktouch(queueobject,state,gameProcess,stop_event)
                    if -1 == state:
                        break
                elif state == 5:
                    #state 5 wait for touch
                    timer.pause()
                    state = self.checktouch(queueobject,state,gameProcess,stop_event)
                    if -1 == state:
                        break
                    self.msg(gameProcess,str(_("Please press key #")),int(state/8),key)
                    timer.changeSecondsAndRestart(2.5)
                elif state == 6:
                    #state 6: wait for key
                    if (queueobject.msg_num == self.MSG_KEYPRESSED) and (key == queueobject.msg_info):
                        timer.pause()
                        key = -1
                        self.msg(gameProcess,str(_("Please touch to continue")),int(state/8))
                        state += 1
                    else:
                        timer.pause()
                        self.msg(gameProcess,str(_("Sorry, wrong key!")),int(state/8),-1,True)
                        stop_event.set()
                        break
                elif state == 7:
                    #state 7: wait for touch
                    state = self.checktouch(queueobject,state,gameProcess,stop_event)
                    if -1 == state:
                        break
                    self.msg(gameProcess,_("Please press key #"),int(state/8),key)
                    timer.changeSecondsAndRestart(2)
                elif state == 8:
                    #state 8: wait for key
                    if (queueobject.msg_num == self.MSG_KEYPRESSED) and (key == queueobject.msg_info):
                        timer.pause()
                        key = -1
                        self.msg(gameProcess,str(_("You have passed! :)")),int(state/8))
                        state += 1
                    else:
                        timer.pause()
                        self.msg(gameProcess,str(_("Sorry, wrong key!")),int(state/8),-1,True)
                        stop_event.set()
                        break

    
    def prepareGame(self, status, queue) -> ():
        """Prepare Level
        Do hardware-preparations
        :param status: current state of the game, used for web-frontend
        :param queue: Message-Q for hardware.messages to be launched
        return list of hardware-processes started here
        """
        kbd=CheckKey(queue)
        startThreadClass(kbd)
        timer=Countdown(queue,-1)
        startThreadClass(timer)
        touch=CheckTouch(queue)
        startThreadClass(touch)
        status.msg=str(_("Level04 starts.."))
        models.setGameState(self.user_id, status)
        glob=tlu_globals.globMgr.tlu_glob()
        glob.lcdMessagebyline(_("Level: ")+"04", _("Touchpad"))
        status.msg=str(_("Level 4 running"))
        status.level_start=timezone.now()
        status.level_progress=0
        models.setGameState(self.user_id, status)
        return (timer,kbd,touch)
    def finishGame(self, status, hardware):
        """End game-level
        Close down hardware-activities started
        :param status: current state of the game, used for web-frontend
        :param hardware: List of hardware-processes that should be terminated here
        """
        (timer,kbd,touch,)=hardware
        glob=tlu_globals.globMgr.tlu_glob()
        buz=None
        if status.result != None and status.result!=Level.PASSED:
            buz=Buzzer(0.1)
            startThreadClass(buz)
            status.msg=str(_("Level 4 failed"))
            status.level_progress=0
            glob.matrixShow_symbol('triangle_down')
            time.sleep(0.3) #wait a bit
        else:
            status.msg=str(_("You have passed Level 4 :)"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=20
            glob.matrixShow_symbol('smiley')
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortThread(touch, 0.5, "aborting Touch")
        abortThread(kbd, 1, "aborting Keyboard")
        abortThread(timer, 1, "aborting countdown")
        abortThread(buz, 0.5, "aborting Buzzer")
    
    