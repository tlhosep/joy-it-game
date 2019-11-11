""" module: tlu_level00

** Content **
A test-task to test the major functions of the game. 
Each level comes with its own class

** Details **
The game consists of some actions to be performed on the joy-it toolset in order to stop the bomb before it is going to explode :)


@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
"""


import logging
from django.utils.translation import gettext as _
from django.utils import timezone, translation
from tlu_joyit_game.models import Level
from tlu_joyit_game import models
from tlu_hardware.tasks import Countdown
from tlu_game.tlu_levelbase import LevelBase
from tlu_services.tlu_processes import startProcess, abortProcess
import threading
import time

logger=logging.getLogger(__name__)


class Level00(LevelBase):
    """ Testlevel for unittest only...
    Not an official task, used only to test all surrounding functionalities as this task does not require
    end-user interaction
    """
    class GameQueue(LevelBase.GameQueue):
        def run(self, stop_event, gameProcess, hardware, language):
            """ Main loop for Testing the game
            Main
            :param stop_event: event coming from main-loop, once set, level will terminate
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param hardware: list of started threads
            """
            translation.activate(language)
            thread=threading.currentThread()
            (timer,)=hardware  # @UnusedVariable
            while True:
                (queueobject,breakIndicator)=self.getQueueObject(stop_event, gameProcess, thread)
                if breakIndicator:
                    break
                if queueobject == None:
                    time.sleep(0.2)
                    continue
                self.queue.task_done() #release object from queue
                if self.checkAbort(stop_event,gameProcess,thread,queueobject):
                    break
    
    def prepareGame(self, status, queue) -> ():
        """Prepare Test
        Do hardware-preparations
        :param status: current state of the game, used for web-frontend
        :param queue: Message-Q for hardware.messages to be launched
        return list of hardware-processes started here
        """
        timer=Countdown(queue,0.5)
        status.msg=_("Level00 starts..")
        status.level_start=timezone.now()
        models.setGameState(self.user_id, status)
        startProcess(timer)
        return (timer,)
    def finishGame(self, status, hardware):
        """End game-level-test
        Close down hardware-activities started
        :param status: current state of the game, used for web-frontend
        :param hardware: List of hardware-processes that should be terminated here
        """
        (timer,)=hardware
        if status.result != None and status.result==Level.TIMEOUT:
            #for testing purposes timeout is the desired outcome
            status.msg=str(_("Level00 passed"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
        elif status.result != None and status.result!=Level.PASSED:
            status.msg=str(_("Level00 failed"))
            status.level_progress=0
        else:
            status.msg=str(_("Level00 passed"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortProcess(timer)
    
    