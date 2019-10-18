""" module: tlu_level03
** Content **
Class to form the third level of the game

** Details **
In this level the player has to press 20 randomly selected keys. Each key has to be pressed within 1.5 seconds.
If one key was wrong, the  whole level fails


@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-14 
"""

import logging
from django.utils.translation import gettext as _
from django.utils import timezone
from tlu_joyit_game.models import Level

from tlu_joyit_game import models

from tlu_hardware.tasks import Countdown, CheckKey, Buzzer
from tlu_game.tlu_levelbase import LevelBase
import threading
from tlu_services.tlu_threads import abortThread, startThreadClass
from tlu_game import tlu_globals
from random import randint

logger=logging.getLogger(__name__)


class Level03(LevelBase):
    """ Third Level of the game
    You have to press each named button once, within decreasing timelimits
    """
    class GameQueue(LevelBase.GameQueue):
        def run(self, stop_event, gameProcess, hardware):
            """ Queue loop for level 3
            Main
            :param stop_event: event coming from main-loop, once set, level will terminate
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param hardware: list of started threads
            """
            key=-1
            numkeys=0
            thread=threading.currentThread()
            (timer, kbd,) = hardware  # @UnusedVariable
            while True:
                if numkeys>19:
                    stop_event.set()
                    break
                if key == -1:
                    key=randint(1,16)
                    status=models.getGameState(gameProcess.user_id)
                    status.msg=_("You have to press Key #")+str(key)
                    status.level_progress=int(numkeys/20*100)
                    models.setGameState(gameProcess.user_id, status)
                
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
                    glob.lcdMessagebyline(_("Level: ")+"03", _("Key = ")+str(queueobject.msg_info))
                    if key != queueobject.msg_info:
                        status=models.getGameState(gameProcess.user_id)
                        status.level_progress=0
                        status.result=Level.FAILED
                        status.msg=_("That was the wrong key, level terminates!")
                        models.setGameState(gameProcess.user_id, status)
                        logging.debug("Wrong Key:"+str(key)+" instead of:"+str(queueobject.msg_info))
                    else:
                        numkeys += 1
                        key=-1 #generate next key
                        status=models.getGameState(gameProcess.user_id)
                        status.level_progress=int(numkeys/20*100)
                        models.setGameState(gameProcess.user_id, status)
                        logging.debug("Correct key pressed :)")
                        newseconds=4
                        if numkeys > 5:
                            newseconds = 3
                        if numkeys > 10:
                            newseconds = 2.5
                        if numkeys > 15:
                            newseconds = 2
                        timer.changeSecondsAndRestart(newseconds)
                elif queueobject.msg_num == self.MSG_KEYRELEASED:
                    pass
    
    def prepareGame(self, status, queue) -> ():
        """Prepare Level
        Do hardware-preparations
        :param status: current state of the game, used for web-frontend
        :param queue: Message-Q for hardware.messages to be launched
        return list of hardware-processes started here
        """
        kbd=CheckKey(queue)
        startThreadClass(kbd)
        timer=Countdown(queue,4)
        status.msg=_("Level03 starts..")
        models.setGameState(self.user_id, status)
        startThreadClass(timer)
        glob=tlu_globals.globMgr.tlu_glob()
        glob.lcdMessagebyline(_("Level: ")+"03", _("Random Keys"))
        status.msg=(_("Level 3 running"))
        status.level_start=timezone.now()
        status.level_progress=0
        models.setGameState(self.user_id, status)
        return (timer,kbd,)
    def finishGame(self, status, hardware):
        """End game-level
        Close down hardware-activities started
        :param status: current state of the game, used for web-frontend
        :param hardware: List of hardware-processes that should be terminated here
        """
        (timer,kbd,)=hardware
        glob=tlu_globals.globMgr.tlu_glob()
        buz=None
        if status.result != None and status.result!=Level.PASSED:
            buz=Buzzer(0.1)
            startThreadClass(buz)
            status.msg=str(_("Level 3 failed"))
            status.level_progress=0
            glob.matrixShow_symbol('triangle_down')
        else:
            status.msg=str(_("You have passed Level 3 :)"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
            glob.matrixShow_symbol('smiley')
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortThread(kbd, 1, "aborting Keyboard")
        abortThread(timer, 1, "aborting countdown")
        abortThread(buz, 0.5, "aborting Buzzer")
    
    