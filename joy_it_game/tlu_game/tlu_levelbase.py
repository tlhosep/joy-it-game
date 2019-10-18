""" module: tlu_levelbase
** Content **
This module provides the base-functionalities of all levels.

** Details **
It encapsulates most of the re-occuring checks to keep the level-implementations as small 
as possible thus preventing them from copy/paste bugs.

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-09-26 
""" 

from multiprocessing import Process, Event
from django.utils.translation import gettext as _

from tlu_services.tlu_processes import abortProcess, startProcess, processlist
import multiprocessing
from tlu_services.tlu_threads import abortThread, startThread
from tlu_hardware.tasks import Countdown
from tlu_joyit_game import models
from tlu_joyit_game.models import Level, userOk, getGameState
from django.utils import timezone
import logging
from tlu_services import tlu_queue
import time
import threading
from tlu_game import tlu_globals

logger=logging.getLogger(__name__)


class LevelBase(Process):
    """ Baseclass for all levels of the game
    Holds commonly needed functionalities and provides base methods that could be overwritten as needed
    
    """

    def checkAbort(self,thread,user_id,msg):
        """ Check if a thread should be aborted.
        Each thread has now added an attribute "is_aborted", if set
        the thread should terminate itself
        
        :param thread: The thread in question
        :param user_id: user that is currently active, needed for the gamestated
        :param msg: Message that will be shown on the web once the task has been aborted
        """
        if getattr(thread, "is_aborted", False):
            status=models.getGameState(user_id)
            status.msg=msg
            status.level_progress=100
            status.result=Level.ABORT
            models.setGameState(user_id, status)
            return True
        return False

    class GameQueue(tlu_queue.tlu_queue):
        """ Queue object for the game to work on several messages
            The Queue forms the processes of the game and serves as a kind of state machine
            Has to be overwritten by the implementation of the level
        """
        def set_abortmsg(self,user_id):
            """
            Internal service function
            :param user_id: The user in question
            """
            status=models.getGameState(user_id)
            status.msg=_("Game aborted :(")
            status.result=Level.ABORT
            status.level_progress=100
            models.setGameState(user_id, status)
        def getQueueObject(self,stop_event,gameProcess,thread)->():
            """
            Try to fetch an message from the queue (non-blocking!) and check if the process shall be terminated.
            Returns an list of the message (or None) and an indicator/bool to indicate if the processing shall be stopped
            :param stop_event: the event from the main-level that would be "set" here in case the level ended or terminated
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param thread: The thread where the queue is looping in
            """
            try:
                queueobject = self.queue.get(block=False,timeout=0.5)
            except:
                if stop_event.is_set():
                    logger.debug('Gamequeue level x aborted while waiting for msg')
                    self.set_abortmsg(gameProcess.user_id)
                    return (None,True)
                elif getattr(thread,'is_aborted',False):
                    logger.debug('Queue-Thread shall be aborted/stopped')
                    self.set_abortmsg(gameProcess.user_id)
                    stop_event.set()
                    return (None,True)
                elif gameProcess.exit.is_set():
                    logger.debug('Game-Process shall be terminated')
                    self.set_abortmsg(gameProcess.user_id)
                    stop_event.set()
                    return (None,True)
                else:
                    return (None,False)
            return (queueobject,False)
        
        def checkAbort(self,stop_event,gameProcess,thread,queueobject):
            """
            Checks the current thread, queue and message object for an indication that we shall abort.
            Returns True in case we have to abort
            :param stop_event: the event from the main-level that would be "set" here in case the level ended or terminated
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param thread: The thread where the queue is looping in
            :param queueobject: the message-object that we should check here
            """
            if stop_event.is_set():
                logger.debug('Gamequeue aborted')
                self.set_abortmsg(gameProcess.user_id)
                return True
            elif getattr(thread,'is_aborted',False):
                logger.debug('Queue-Thread shall be aborted/stopped')
                self.set_abortmsg(gameProcess.user_id)
                stop_event.set()
                return True
            elif gameProcess.exit.is_set():
                logger.debug('Game-Process shall be terminated')
                self.set_abortmsg(gameProcess.user_id)
                stop_event.set()
                return True
            elif queueobject.msg_num == self.MSG_STOP:
                logger.debug('Gamequeue stopped via msg')
                self.set_abortmsg(gameProcess.user_id)
                stop_event.set()
                return True
            elif queueobject.msg_num == self.MSG_TIMEOUT:
                logger.debug('Timeout raised in queue')
                status=models.getGameState(gameProcess.user_id)
                status.msg=_("Timeout reached :(")
                status.result=Level.TIMEOUT
                status.level_progress=100
                models.setGameState(gameProcess.user_id, status)
                stop_event.set()
                return True
            return False
            
        def run(self,stop_event, gameProcess, hardware):
            """
            Main game-loop
            Use this code as a *template* for your implementation only
            :param stop_event: the event from the main-level that would be "set" here in case the level ended or terminated
            :param gameProcess: the main process running the level. Needed to check for termination requests and the user_id
            :param hardware: list of started threads
            """

            thread=threading.currentThread()
            while True:
                (queueobject,breakIndicator)=self.getQueueObject(stop_event, gameProcess, thread)
                if breakIndicator:
                    break
                if queueobject == None:
                    continue
                self.queue.task_done() #release object from queue
                if self.checkAbort(stop_event,gameProcess,thread,queueobject):
                    break

    def __init__(self, user_id):
        """
        Constructor of the base-class
        
        :param user_id: ID of the user, needed for various parameter
        """
        Process.__init__(self)
        self.exit=Event()
        self.user_id=user_id
        
    def clearprocesses(self):
        """
        terminates all tasks that have been started so far, assumes that we have a single player game here ;)
        """
        for p in multiprocessing.active_children():
            if p.name in processlist:
                abortProcess(p)
                    
    def cleanup(self,suspendall=True):
        """ stops all potentially running hardware activities and terminates all remaining tasks
        sets hardware to a startup state
        
        :param suspendall: if True, all tasks started by the app will be aborted
        """
        glob=tlu_globals.globMgr.tlu_glob()
        glob.cleanup()
        if suspendall:
            self.clearprocesses()        
    
    def startup(self):
        """ Starts the hardware by performing a cleanup and showing the clock
        Used from outside within the view at initialization
        """
        self.cleanup(False)
        glob=tlu_globals.globMgr.tlu_glob()
        glob.startClock()

    def prepareGame(self,status,queue) -> ():
        """
        Method to be overwritten by implementation.
        Would be called before starting the processing of the message queue
        Use this as a *template* only!
        return list of started processes (needed to terminate them at the end)
        :param status: status object of the level
        :param queue: Message queu for game-messages
        """
        timer=Countdown(queue,1)
        status.msg=_("Level00 starts..")
        status.level_start=timezone.now()
        models.setGameState(self.user_id, status)
        startProcess(timer)
        return (timer,)
    
    def finishGame(self,status,hardware):
        """
        Method to be overwritten by implementation.
        Would be called after ending the processing of the message queue
        Use this as a *template* only!
        
        :param status: status of the current level
        :param hardware: started processes to run the level, needed to terminate them
        """
        (timer,)=hardware
        if status.result != None and status.result!=Level.PASSED:
            status.msg=str(_("Level x failed"))
            status.level_progress=0
        else:
            status.msg=str(_("Level x passed"))
            status.level_progress=100
            status.result=Level.PASSED
            status.points=5
        status.level_ended=timezone.now()
        models.setGameState(self.user_id, status)
        abortProcess(timer)
        logger.info('Level x State= '+str(status))
        logger.debug('Level x ended')
        
    def run(self, *args, **kwargs):
        """
        The main process for this level
        Please overwrite the following methods and not this one:
        * prepareGame and 
        * finishGame besides 
        * GameQueue.run as 
        these 3 provide the necessary game-functionalities and not this "run" method
        """
        logger.debug('level started')
        status=models.getCleanGameState(self.user_id)
        status.msg=(_("Level is running"))
        status.level_progress=0
        models.setGameState(self.user_id, status)
        if not userOk(self.user_id):
            status.msg=_("You have to login in order to play this level...")
            models.setGameState(self.user_id, status)
            return
        queue=self.GameQueue()
        stop_event=Event()
        hardware=self.prepareGame(status, queue)
        qThread=startThread(queue.run, args=(stop_event,self,hardware,), name="queue_for_level") #needed to loop through the messages
        
        stop_event.wait() #wait until queues stops processing or level gets terminated
        stop_event.clear()
        status=getGameState(self.user_id)
        self.finishGame(status, hardware)
        status=getGameState(self.user_id)
        logger.info('Level State= '+str(status))
        logger.debug('Level ended')

        queue.close()
        abortThread(qThread, 1, "aborting message-Queue")
        glob=tlu_globals.globMgr.tlu_glob()
        glob.startClock() #restart clock in case it had been stopped
        return
    def terminate(self, *args, **kwargs):
        """
        Terminate the game-process in case this was requested
        """
        self.exit.set()
        logger.info('Level termination requested')
        time.sleep(2) # wait a bit to close the queue and the level safely
        return Process.terminate(self, *args, **kwargs) #this line adds extra safety, if the soft termination inside the run function did not work within 2 seconds ;)

        