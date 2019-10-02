""" module: tlu_level01
** Content **
Class to form the first level of the game

** Details **
The game consists of some actions to be performed on the joy-it toolset in order to stop the bomb before it is going to explode :)
The first level introduces simply the 16 keys


Created on 17. Sep 2019

@author: thomas lueth
"""


import logging
from django.utils.translation import gettext as _
from django.utils import timezone
from tlu_joyit_game.models import Level

from tlu_joyit_game import models

from tlu_hardware.tasks import Countdown, CheckKey, Buzzer
from tlu_game.tlu_levelbase import LevelBase
import time
import threading
from tlu_services.tlu_threads import abortThread, startThreadClass
from tlu_game import tlu_globals

logger=logging.getLogger(__name__)


class Level01(LevelBase):
    ''' First Level of the game
    You have to press each button once
    '''
    class GameQueue(LevelBase.GameQueue):
        def run(self, stop_event, gameProcess):
            ''' Queue loop for level 1
            Main
            :param stop_event: event coming from main-loop, once set, level will terminate
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            '''
            keymatrix={}
            thread=threading.currentThread()
            while True:
                if len(keymatrix)==16:
                    stop_event.set()
                    break
                (queueobject,breakIndicator)=self.getQueueObject(stop_event, gameProcess, thread)
                if breakIndicator:
                    break
                if queueobject == None:
                    continue
                self.queue.task_done() #release object from queue
                if self.checkAbort(stop_event,gameProcess,thread,queueobject):
                    break
                elif queueobject.msg_num == self.MSG_KEYPRESSED:
                    glob=tlu_globals.globMgr.tlu_glob()
                    glob.lcdMessagebyline(_("Level: ")+"01", _("Key = ")+str(queueobject.msg_info))
                    keymatrix[queueobject.msg_info]=1
                    status=models.getGameState(gameProcess.user_id)
                    status.msg=_("You have just pressed Key #")+str(queueobject.msg_info)
                    status.level_progress=int(len(keymatrix)/16*100)
                    models.setGameState(gameProcess.user_id, status)
                    time.sleep(0.3) #wait for messages to settle
                elif queueobject.msg_num == self.MSG_KEYRELEASED:
                    pass
    
    def prepareGame(self, status, queue) -> ():
        '''Prepare Level 1
        Do hardware-preparations
        :param status: current state of the game, used for web-frontend
        :param queue: Message-Q for hardware.messages to be launched
        return list of hardware-processes started here
        '''
        kbd=CheckKey(queue)
        startThreadClass(kbd)
        timer=Countdown(queue,16)
        status.msg=_("Level00 starts..")
        models.setGameState(self.user_id, status)
        startThreadClass(timer)
        glob=tlu_globals.globMgr.tlu_glob()
        glob.lcdMessagebyline(_("Level: ")+"01", _("Easy start ")+":)")
        status.msg=(_("Level 1 running"))
        status.level_start=timezone.now()
        status.level_progress=0
        models.setGameState(self.user_id, status)
        return (timer,kbd,)
    def finishGame(self, status, hardware):
        '''End game-level 1
        Close down hardware-activities started
        :param status: current state of the game, used for web-frontend
        :param hardware: List of hardware-processes that should be terminated here
        '''
        (timer,kbd,)=hardware
        glob=tlu_globals.globMgr.tlu_glob()
        buz=None
        if status.result != None and status.result!=Level.PASSED:
            buz=Buzzer(0.1)
            startThreadClass(buz)
            status.msg=str(_("Level 1 failed"))
            status.level_progress=0
            glob.matrixShow_symbol('triangle_down')
        else:
            status.msg=str(_("You have passed Level 1 :)"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
            glob.matrixShow_symbol('smiley')
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortThread(kbd, 1, "aborting Keyboard")
        abortThread(timer, 1, "aborting countdown")
        abortThread(buz, 0.5, "aborting Buzzer")
        logger.info('Level01 State= '+str(status))
        logger.debug('Level01 ended')
    
    