""" module: tests

This module shall try to test most of the provided game functionalities

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
""" 

import unittest
import logging
from django.contrib.auth import get_user_model
from tlu_joyit_game.models import Game, getGameState, setGameState, userOk, Level,\
    getCleanGameState
import time
from tlu_game.tlu_level00 import Level00
from tlu_game import tlu_globals
from tlu_hardware.tlu_checkhardware import emulatekey
from tlu_hardware import tlu_hardware_global

logger=logging.getLogger(__name__)


class TestGame(unittest.TestCase):
    """
    Test most of the  tlu_game methods
    """
    def getGame(self, username="TestXYZ987"):
        """
        Service function to setup an individual user per test, so each test gets unique :)
        :param username: Name of the testcase to setup exactly this user for the test
        """
        logging.debug('getGame called')
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username,
                                          email="1@test.de",
                                          password="test1234!@t.de")
        userset=User.objects.filter(username=username) #get created user
        self.assertNotEqual(userset, None, "The user has to be found")
        self.assertTrue(userset.count()==1, "We expect exact one user here, found: "+str(userset.count())+" content:"+str(userset))
        user=userset[0] #get first user, we do not expect more ;)
        game = user.game
        game.current_level=None #start from scratch
        game.save()
        return game

    def test_status(self):
        """
        Test the status object
        """
        logging.debug('Test test_status started')
        game=self.getGame('test_status')
        gamestate=getCleanGameState(game.user.id)
        self.assertEqual(gamestate.level_progress, 0, "The initial Progress has to be 0")
        gamestate.msg="HALLO"
        gamestate.level_progress=55
        setGameState(game.user.id,gamestate)
        gamestate=getGameState(game.user.id)
        self.assertEqual(gamestate.msg, "HALLO", "The messages differ :(")
        self.assertEqual(gamestate.level_progress, 55, "The Progress has to be 55")
        logging.debug('Test status ended')
     

    def test_create_game(self):
        """
        Test to create the gamestate
        """
        logging.debug('Test test_create_game started')
        game= self.getGame('test_create_game')
        gamestate=getCleanGameState(game.user.id)
        self.assertEqual(gamestate.level_progress, 0, "The initial Progress has to be 0")
        self.assertEqual(game.current_level,None,"Level not assigned yet")
        self.assertTrue(userOk(game.user.id), "User has to be logged on at the start of this test")
         
    def test_start_game(self):
        """
        Test to startup the game (level 0)
        """
        tlu_globals.init() #in case not called before ;)
        tlu_hardware_global.init()
        logging.debug('Test test_start_game started')
        game=self.getGame('test_start_game')
        logging.debug("test_start_game: b4 start:  Game="+str(game))
        game.start(Level00,0)
        logging.debug("test_start_game: after start:  Game="+str(game))
        time.sleep(1.2) #wait until game times out internally after 1 second, then continue here
        res=game.result()
        self.assertEqual(res, Level.PASSED, "Expected result of game00-run is "+str(Level.PASSED))
        levelobject=game.current_level
        self.assertNotEqual(levelobject, None, "The level has to be known")
        self.assertEqual(levelobject.levelnum, 0, "Level has to be 0")
        self.assertEqual(levelobject.points, 5, "5 points achieved")
        self.assertEqual(levelobject.result, 1, "results have to match")
        self.assertNotEqual(levelobject.level_start, None, "The level should have a starting time")
        self.assertNotEqual(levelobject.level_ended, None, "The level should have a ending time")
        self.assertEqual(levelobject.prevLevel, None, "The previous level has to be empty")

    def test_abort(self):
        """
        Test to abort the game during its operation (level 0)
        """
        tlu_globals.init() #in case not called before ;)
        tlu_hardware_global.init()
        logging.debug('Test test_abort started')
        game=self.getGame('test_abort')
        game.start(Level00,0)
        game.abort()
        logging.debug('Test test_abort ended, analysis starts')
        levelobject=game.current_level
        logging.debug('Test test_abort result is: '+str(levelobject))
        self.assertNotEqual(levelobject, None, "The level has to be known")
        self.assertEqual(levelobject.levelnum, 0, "Level has to be 0")
        self.assertEqual(levelobject.points, 0, "No points achieved")
        self.assertNotEqual(levelobject.level_start, None, "The level should have a starting time")
        self.assertNotEqual(levelobject.level_ended, None, "The level should have a ending time")
        self.assertEqual(levelobject.result, Level.ABORT, "results have to match (aborted)="+str(Level.ABORT))
       
    def test_retry(self):
        """
        Test to simulate a retry-wish of the player
        """
        tlu_globals.init() #in case not called before ;)
        tlu_hardware_global.init()
        logging.debug('Test test_retry started')
        game=self.getGame('test_retry')
        logging.debug("test_retry: b4 start:  Game="+str(game))
        game.start(Level00,0)
        time.sleep(0.5) #allow the game top start
        logging.debug("test_retry: after start: Game="+str(game))
        game.retry()
        levelobject=game.current_level
        self.assertNotEqual(levelobject, None, "The level has to be known")
        self.assertEqual(levelobject.levelnum, 0, "Level has to be 0")
        self.assertEqual(levelobject.points, 0, "No points achieved")
        self.assertEqual(levelobject.result, Level.RETRY, "results have to match (retry)="+str(Level.RETRY))
        
       
    def test_success(self):
        """
        Test a successful run of level 0
        """
        tlu_globals.init() #in case not called before ;)
        tlu_hardware_global.init()
        logging.debug('Test test_success started')
        game=self.getGame('test_success')
        logging.debug('game created: '+str(game))
        task=Level00
        logging.debug("test_success: b4 start:  Game="+str(game))
        game.start(task,0)
        logging.debug("test_success: after start:  Game="+str(game))
        self.assertTrue(game.is_running(), "Started game has to run (for at least 2.5 seconds)")
        time.sleep(1.2) #wait a bit to terminate the level internally
        res=game.result() #wait for level to terminate
        games=Game.objects.all()
        for g in games:
            logging.debug(str(g))
        self.assertEqual(res, Level.PASSED, "Expected result is "+str(Level.PASSED))
        levelobject=game.current_level
        self.assertNotEqual(levelobject, None, "The level has to be known")
        self.assertEqual(levelobject.levelnum, 0, "Level has to be 0")
        self.assertEqual(levelobject.points, 5, "5 points achieved")
        self.assertNotEqual(levelobject.level_start, None, "The level should have a starting time")
        self.assertNotEqual(levelobject.level_ended, None, "The level should have a ending time")
        self.assertEqual(levelobject.result, Level.PASSED, "results have to match (passed)="+str(Level.PASSED))

    def test_globals(self):
        """ Test the global-functionality provided by tlu_globals
        
        """
        tlu_globals.init() #in case not called before ;)
        tlu_hardware_global.init()
        glob=tlu_globals.globMgr.tlu_glob()
        self.assertTrue(glob.test(), "The test has to pass...")
        if emulatekey:
            self.assertNotEqual(tlu_globals.kbQueue, None, "Keyboardqueue should not be null on mac")
        
if __name__ == '__main__':
    unittest.main()