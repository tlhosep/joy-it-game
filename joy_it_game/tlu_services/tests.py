""" module: tests

** Content **
Test the settimgs functionality

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-22 
""" 

import unittest
from tlu_services import tlu_local_settings
import copy

class Test(unittest.TestCase):

    localsettings=None

    def testRead_noFile(self):
        '''
        Test the settings-defauls without writing to file
        '''
        ls = tlu_local_settings.local_settings()
        if ls.presence():
            ls.read()
            localsettings=copy.deepcopy(ls.SETTINGS)
            ls.remove()
        ls.read()
        self.assertTrue(ls.SETTINGS['EMAIL_PORT'] == 1025, "Default port does not match")
        self.assertTrue(ls.SETTINGS['EMAIL_HOST'] == "127.0.0.1", "Default host does not match")
        self.assertFalse(ls.SETTINGS['EMAIL_USE_TLS'] , "Default bool TLS does not match")
        self.assertFalse(ls.presence())  
        if localsettings is not None:
            ls.SETTINGS=copy.deepcopy(localsettings)
            ls.save()
            localsettings=None
            

    def testRead_FileCycle(self):
        '''
        Test creating and removing a settings-file
        '''
        ls = tlu_local_settings.local_settings()
        if ls.presence():
            ls.read()
            localsettings=copy.deepcopy(ls.SETTINGS)
            ls.remove()
        ls.read()
        ls.SETTINGS['EMAIL_PORT'] = 1111
        ls.SETTINGS['EMAIL_HOST'] = '127.0.0.1'
        ls.SETTINGS['EMAIL_USE_TLS'] = True
        ls.save()
        ls.read() 
        self.assertTrue(ls.SETTINGS['EMAIL_PORT'] == 1111, "Default port does not match")
        self.assertTrue(ls.SETTINGS['EMAIL_HOST'] == "127.0.0.1", "Default host does not match")
        self.assertTrue(ls.SETTINGS['EMAIL_USE_TLS'] , "Default bool TLS does not match")
        ls.remove()
        self.assertFalse(ls.presence())  
        if localsettings is not None:
            ls.SETTINGS=copy.deepcopy(localsettings)
            ls.save()
            localsettings=None

    def testRemove(self):
        '''
        Test removing the settings-file
        '''
        ls = tlu_local_settings.local_settings()
        ls.read()
        localsettings=copy.deepcopy(ls.SETTINGS)
        ls.save()
        ls.remove()
        self.assertFalse(ls.presence())  
        if localsettings is not None:
            ls.SETTINGS=copy.deepcopy(localsettings)
            ls.save()
            localsettings=None
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRead_noFile']
    unittest.main()