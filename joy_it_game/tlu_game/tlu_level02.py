''' module: tlu_level02

*** Content ***
Class to form the second level of the game

** Details **
The game consists of some actions to be performed on the joy-it toolset in order to stop the bomb before it is going to explode :)
The second level introduces simply the 4 cursor keys


@author: thomas lueth
'''


import logging
from django.utils.translation import gettext as _
from django.utils import timezone
from tlu_joyit_game.models import Level

from tlu_joyit_game import models

from tlu_hardware.tasks import Countdown, CheckCursor, Buzzer
from tlu_game.tlu_levelbase import LevelBase
import time
from tlu_hardware.tlu_cursor import tlu_cursor
import threading
from tlu_services.tlu_threads import abortThread, startThreadClass
from tlu_game import tlu_globals

logger=logging.getLogger(__name__)


class Level02(LevelBase):
    ''' First Level of the game
    You have to press each button once
    '''
    class GameQueue(LevelBase.GameQueue):
        def run(self, stop_event, gameProcess):
            ''' Main loop for Level2
            Main
            :param stop_event: event coming from main-loop, once set, level will terminate
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            '''
            keymatrix={}
            thread=threading.currentThread()
            while True:
                if len(keymatrix)==4:
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
                    glob.lcdMessagebyline(_("Level: ")+"02", _("Cursor = ")+tlu_cursor.cursorname(None, queueobject.msg_info))
                    keymatrix[queueobject.msg_info]=1
                    symbolname='space'
                    if queueobject.msg_info==100:
                        symbolname='arrow_up'
                    elif queueobject.msg_info==200:
                        symbolname='arrow_right'
                    elif queueobject.msg_info==300:
                        symbolname='arrow_down'
                    elif queueobject.msg_info==400:
                        symbolname='arrow_left'
                    
                    glob.matrixShow_symbol(symbolname)
                    status=models.getGameState(gameProcess.user_id)
                    status.msg=_("You have just pressed cursor - ")+tlu_cursor.cursorname(None, queueobject.msg_info)
                    status.level_progress=int(len(keymatrix)/4*100)
                    models.setGameState(gameProcess.user_id, status)
                    time.sleep(0.5) #wait for messages to settle
                elif queueobject.msg_num == self.MSG_KEYRELEASED:
                    pass
        
    def prepareGame(self, status, queue) -> ():
        '''Prepare Level
        Do hardware-preparations
        :param status: current state of the game, used for web-frontend
        :param queue: Message-Q for hardware.messages to be launched
        return list of hardware-processes started here
        '''
        cc=CheckCursor(queue)
        startThreadClass(cc)
        timer=Countdown(queue,4)
        status.msg=_("Level 2 starts..")
        models.setGameState(self.user_id, status)
        startThreadClass(timer)
        glob=tlu_globals.globMgr.tlu_glob()
        glob.lcdMessagebyline(_("Level: ")+"02", _("Cursorkeys... ")+":)")
        status.msg=(_("Level 2 running"))
        status.level_progress=0
        status.level_start=timezone.now()
        models.setGameState(self.user_id, status)
        return (timer,cc,)
    def finishGame(self, status, hardware):
        '''End game-level
        Close down hardware-activitiues started
        :param status: current state of the game, used for web-frontend
        :param hardware: List of hardware-processes that should be terminated here
        '''
        (timer,cc,)=hardware
        glob=tlu_globals.globMgr.tlu_glob()
        buz=None
        if status.result != None and status.result!=Level.PASSED:
            buz=Buzzer(0.1)
            startThreadClass(buz)
            status.msg=str(_("Level 2 failed"))
            status.level_progress=0
            glob.matrixShow_symbol('triangle_down')
        else:
            status.msg=str(_("You have passed Level 2 :)"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
            glob.matrixShow_symbol('smiley')
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortThread(cc, 1, "aborting Cursor")
        abortThread(timer, 1, "aborting countdown")
        abortThread(buz, 0.5, "aborting Buzzer")
        logger.info('Level02 State= '+str(status))
        logger.debug('Level02 ended')
    
    