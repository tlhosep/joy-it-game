""" module: models

This module contains the major database models of the game
*** Content ***
The main database model

** Details **
We have the game that extends the user by adding a current level
In addition we do have a set of levels associated to a game

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
""" 

from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from tlu_hardware.tlu_buttons import tlu_buttons
from tlu_hardware.tlu_cursor import tlu_cursor
import logging
from joy_it_game import settings
import time
from multiprocessing import Manager
from tlu_services.tlu_processes import abortProcess, startProcess
import multiprocessing

logfile=settings.BASE_DIR+"/log/game.log"
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s;%(filename)-16.16s;%(lineno)04d;%(levelname)-8s;%(message)s')

manager = Manager()
states = manager.dict()

class gameState(object):
    ''' Class to hold the status of a level played
    This class is needed to allow to post the current status on the web. The game provides frequent updates to the state.
    These are then taken by the Ajax-call that request updates for the frontend
    '''
    msg = ""
    level_progress = 0
    result=None
    level_start=None
    level_ended=None
    points=0
    def cleanup(self):
        ''' Kind of basic initialization
        This is needed to have a clenan state when a level would be started as the same state would be used
        for all levels for a particular use        
        '''
        self.msg=""
        self.level_progress=0
        self.result=None
        self.level_start=None
        self.level_ended=None
        self.points=0
       
    def __init__(self):
        '''
        Calls cleanup
        '''
        self.cleanup()
    def fromUserId(self,user_id):
        '''
        Initializes class-object by a recorded state if available
        Else calls cleanup
        :param user_id: ID to identify the user of the game
        '''
        global states
        status_dict=None
        if user_id in states:
            status_dict=states[user_id]
        if status_dict==None:
            self.cleanup()
            return
        logging.debug("Status read for user-id:"+str(user_id)+" is:"+str(states[user_id]))
        self.msg=status_dict['MSG']
        self.level_progress=status_dict['LEVEL_PROGRESS']
        self.result=status_dict['RESULT']
        self.level_start=status_dict['LEVEL_START']
        self.level_ended=status_dict['LEVEL_ENDED']
        self.points=status_dict['POINTS']
    def saveUserId(self,user_id):
        '''
        Saves the current state of the game in the global states dictionary
        by using the user-id as the key
        :param user_id: Key to identify the user
        '''
        global states
        status_dict={}
        status_dict['MSG']=self.msg
        status_dict['LEVEL_PROGRESS']=self.level_progress
        status_dict['RESULT']=self.result
        status_dict['LEVEL_START']=self.level_start
        status_dict['LEVEL_ENDED']=self.level_ended
        status_dict['POINTS']=self.points
        states[user_id]=status_dict
        logging.debug("status saved for user-id:"+str(user_id)+" is:"+str(states[user_id]))
                
    def __str__(self, *args, **kwargs):
        return str(vars(self))
    
def getGameState(user_id) -> gameState:
    '''
    Service to return the gamestate of the user given
    :param user_id: Key to identify the state
    '''
    state=gameState()
    state.fromUserId(user_id)
    return state
def getCleanGameState(user_id) -> gameState:
    '''
    Provides and sets a fresh gameState
    :param user_id: Key to identify the state
    '''
    state=gameState()
    state.saveUserId(user_id)
    return state
def setGameState(user_id,gamestate):
    '''
    sets the updated state, service function to wrap the gamestate call
    :param user_id: Key to identify the state
    :param gamestate: gamestate that should be saved
    '''
    gamestate.saveUserId(user_id)

def userOk(user_id):
    ''' Check if user is allowed to play
    The user has to be logged in/authenticated in order to play the levels
    :param user_id: The user in question
    '''
    try:
        user=User.objects.get(pk=user_id)
    except:
        return False
    if user.is_authenticated:
        if user.game != None:
            return True
    return False
    
 
def getProcess(pid):
    '''
    retrieve the process by id
    '''
    for p in multiprocessing.active_children():
        if p.pid ==pid:
            logging.debug("Process for pid:"+str(pid)+" is:"+str(p))
            return p
    logging.debug("Process for pid:"+str(pid)+" is:None")
    return None
 

class Game(models.Model):
    ''' The Game - Main class
    Major class to play the game. Controls the Levels, starts and stops the processes
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True,default=None, related_name='active_levels')
    process_pid = models.IntegerField(null=True,default=None)
    
    '''some constants
    The dipswitch_settings and frequent_updates are required for each level. This is needed
    to lookup the correct task and to forward the frequency for the updates on the web (in ms)
    '''
    dipswitch_settings=(tlu_buttons(),tlu_buttons(),tlu_cursor(),tlu_buttons())
    frequent_updates=(2000,1000,500,500)
      
    def __str__(self):
        ret= "id:"+str(self.id)+"user:"+str(self.user)+" lev:"+str(self.current_level)+" process-id:"+str(self.process_pid)
        return ret
    def setLevel(self,level):
        '''
        Sets the level of the game
        :param level: levelobject to be set
        '''
        self.current_level=level
    def getLevel(self):
        '''
        Returns the current level-object
        '''
        return self.current_level
    def endReached(self):
        '''
        Check if the end of the game is reached now.
        Returns True if so.
        '''
        if self.current_level != None:
            return self.current_level.levelnum >= (len(self.frequent_updates)-1)
        return False
    def completed(self,level_num): 
        '''
        Check if the given level-number indicates the end of the game
        :param level_num: number to check for end of game
        '''
        return level_num>(len(self.frequent_updates)-1)
    def getFrequentUpdatesMs(self,level_num):
        '''
        Returns the number of miliseconds that we wait until the next Ajax-Call has to be made.
        There is one number defined for each level, as each level is different
        :param level_num: number of level that has to be examined
        '''
        return self.frequent_updates[level_num]
    def getDipSwitch(self,level_num):
        '''
        Return the hex-code for the 2 dip-switches. Their setting depend on the hardware that would be used for the level.
        :param level_num: number of level to request the setting
        '''
        return self.dipswitch_settings[level_num]
    def getOverallProgress(self):
        '''
        Calculate the overall progress in percent of the game based on the current level and current progress
        '''
        state=getGameState(self.user.id)
        if self.current_level == None:
            return 0
        return int((100/(len(self.frequent_updates)-1))*(self.current_level.levelnum-1))+int(state.level_progress/100*(100/(len(self.frequent_updates)-1)))
    def getAchievedPoints(self):
        '''
        Calculate the total number of achieved points by iterating through all successfully passed levels so far
        '''
        achievedPoints=0
        level = self.current_level
        while level != None:
            if level.result==Level.PASSED:
                achievedPoints+=level.points
            level = level.prevLevel
        return achievedPoints
    def getState(self):
        '''
        Service wrapper to return the game-state
        '''
        state=getGameState(self.user.id)
        return state
    def _abortTask(self,msg,timeout=3):
        ''' Internal method to abort the level played
        
        :param msg: msg for logging purposes while aborting the process
        :param timeout: time in seconds to wait for a process to abort
        '''
        #simply aborts a task
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        if (self.current_level != None) and (process != None):
            logging.debug("Aborting task with id "+str(process.ident))
            abortProcess(process,timeout,msg)
            self.process_pid=None    
    def startFromScratch(self,task):
        '''
        Restart the game from scratch at the task provided
        :param task: Level that should be used to start the game
        '''
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        
        logging.debug("game start from scratch requested")
        if (self.gamelevel.level != None) and (process != None):
            self.abort()
        self.current_level=None
        return self.start(task)
     
    def restart(self):
        '''
        Force restart of the game by setting the current level to none
        '''
        self.current_level=None
        self.save()
        
    def start(self,task,level_num):
        ''' Start the game-level
        
        :param task: the level-process to be played
        :param level_num: the number of the level to be played
        '''
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        logging.debug("game start requested")
        if (self.current_level != None) and (process != None):
            self.abort()
        with transaction.atomic():
            level=Level()
            level.setup(level_num,self,self.current_level)
            level.save()
            self.current_level=level
            self.save()
        logging.debug("This is the game: "+str(self))
        proc=task(self.user.id)
        startProcess(proc)
        self.process_pid=proc.pid
        logging.debug("Game started:"+str(self.process_pid))
        self.save()
        return proc
    def _end(self,msg, status):
        ''' Internal used method to end the current game-level
        
        :param msg: debugging message for aborting the game
        :param status: status for the termination, any of the states provided by the Level-class
        '''
        self._abortTask(msg)
        gamestate=getGameState(self.user.id)
        if (status==Level.ABORT) and (gamestate.result == Level.NOT_STARTED):
            #abort only if not already stopped
            gamestate.result=Level.ABORT
        else:
            gamestate.result=status
        if gamestate.level_ended == None:
            gamestate.level_ended=timezone.now() # set ending time
        if gamestate.result==None:
            gamestate.result=Level.FAILED
        self.current_level.setFromGameState(gamestate)
        self.current_level.save()
    def abort(self):
        ''' short for _end with Level.ABORT
        
        '''
        self._end("while aborting", Level.ABORT)
    def retry(self):
        '''
        Sets result of previous level to retry
        '''
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        logging.debug("game retry requested")
        if (self.current_level != None) and (process != None):
            self._abortTask("Aborting to retry", 3)
        if self.current_level != None:
            self.current_level.result=Level.RETRY
            self.current_level.save()
    def result(self,timeout=60):
        ''' Wait for the level to end
        Wait until task produces a result or timeout(in seconds) runs out
        Retrieves the result of a level
        :param timeout: Seconds to wait b4 terminating the process, default 60 seconds
        '''
        logging.info("requesting result of level")
        state=getGameState(self.user.id)
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        if (self.current_level != None) and (self.process_pid != None):
            alive=False
            if process!=None:
                alive=process.is_alive()
            logging.debug("result called, current alive-status of task: "+str(alive)+" state="+str(state))
            count=timeout*10
            while (alive) and (count > 0):
                #wait for task to end
                logging.debug("current alive-state of task: "+str(process.is_alive())+" count="+str(count))
                time.sleep(0.1)
                count -= 2
                if process!=None:
                    alive=process.is_alive()
            state=getGameState(self.user_id)
            logging.debug("result called, updated alive-state of task: "+str(alive)+" count="+str(count)+" state="+str(state))
            if count < 1:
                logging.warn("result called, but timed-out")
                self._abortTask("aborting while waiting for result due to timeout",1)
                state.result=Level.FAILED
            logging.debug("current state: "+str(state))
            setGameState(self.user.id, state)
            self.process_pid=None
            self._end("End requested with state: "+str(state),state.result)
            self.save()
        return state.result
    def is_running(self):
        ''' Check if Game is running
        '''
        process=None
        if self.process_pid != None:
            process=getProcess(self.process_pid)
        if (self.current_level != None) and (process != None):
            logging.debug("Alive-State of "+str(process.ident)+" is:"+str(process.is_alive()))
            if process.is_alive():
                return True
        return False 
    
@receiver(post_save, sender=User)
def create_game(sender, instance, created, **kwargs):
    if created:
        Game.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_game(sender, instance, **kwargs):
    instance.game.save()
    
class Level(models.Model):
    ''' The Level played for the game
    Defines some constants for the status of the game-level:
    *NOT_STARTED=0
    *PASSED=1
    *RETRY=2
    *ABORT=3
    *FAILED=4
    *STARTED=5
 
    This is also the database representation of the current level.
    Forms a daisy-chain by referencing to the previous level, if available
    '''
    NOT_STARTED=0
    PASSED=1
    RETRY=2
    ABORT=3
    FAILED=4
    STARTED=5
    TIMEOUT=6
    resultdict=(_("not started"), _('passed'), _('retry'), _('abort'), _('failed'), _("started"), _("timeout"))
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True) #reference to the underlying game object
    prevLevel=models.ForeignKey('Level',on_delete=models.SET_NULL, null=True,default=None, related_name='all_levels') #daisy-chain for a game consisting of levels
    levelnum = models.IntegerField(default=-1) # Level-Number ranging from 00 (Test only), 1..99
    level_start = models.DateTimeField(null=True, default=None) #When did the user start this level?
    level_ended = models.DateTimeField(null=True, default=None) #When did it end?
    points = models.IntegerField(default=0) #achieved points for the level
    result = models.IntegerField(default=0) #result of level played: NOT_STARTED, PASSED, RETRY, ABORT, FAILED, STARTED
    
    def __str__(self):
        ret="Level: "+str(self.levelnum)+" points: "+str(self.points)+" res: "+str(self.result)
        if self.level_start != None:
            ret += " start: "+str(self.level_start)
        if (self.level_ended != None):
            ret += " end: "+str(self.level_ended)
        if (self.prevLevel != None):
            ret+=" prev-Level= "+str(self.prevLevel)
        return ret
    
    @classmethod
    def create(cls,game):
        level = cls(game=game)
        return level
        
    def setup(self,levelnum,game,prevLevel=None):
        """ Set some defaults for the level, including the reference to the game
        
        :param levelnum: level number (1..99)
        :param game: reference to the game currently played
        :param prevLevel: reference to previous level, if exist else None (default)
        """
        self.prevLevel=prevLevel
        self.achieved_points=0
        self.levelnum=levelnum
        self.level_start=None
        self.level_ended=None
        self.points=0
        self.result=Level.NOT_STARTED
        self.game=game

    def setFromGameState(self,gameState):
        ''' Load Level-status from state-object
        As the state object only exists in memory this
        methos persists the state as part of the level-object in the database
        
        :param gameState: state that has to be persisted
        '''
        self.level_start=gameState.level_start
        self.level_ended=gameState.level_ended
        self.points=gameState.points
        self.result=gameState.result
        
    def strFromResult(self,result):
        '''
        Returns the string representation of the given result
        :param result: Number-Code of result of level
        '''
        if result==None:
            return "NONE"
        if result < len(self.resultdict):
            return str(self.resultdict[result])
        return "???"
   
