""" module: tlu_queue

** Content **
Class to manage a global queue for various tasks

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-08-26 
""" 

from joy_it_game import settings
import logging
import sys
import threading
from multiprocessing import JoinableQueue
logfile=settings.BASE_DIR+"/log/game.log"
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s;%(filename)-16.16s;%(lineno)04d;%(levelname)-8s;%(message)s')

def log_info(info=""):
    """
    log calling function's name and thread with optional info-text.
    
    :param info: message for logging purposes
    """
    calling_func = sys._getframe(1).f_code.co_name
    thread_name = threading.currentThread().name
    s="<{thread_name}, {calling_func}> {info}".format(thread_name=thread_name,calling_func=calling_func,info=info)
    logging.debug(s)

class tlu_queueobject(object):
    ''' Class to hold the message-id and some associated infos, like messages or numbers
    '''
    msg_num=0
    msg_info=None
    def __init__(self,msg_num=0,msg_info=None):
        self.msg_num=msg_num
        self.msg_info=msg_info
    def __str__(self, *args, **kwargs):
        ret= "Msg="+tlu_queue.msgTranslate[self.msg_num]
        if (self.msg_info != None):
            ret+=" info="+str(self.msg_info)
        return ret

class tlu_queue(object):
    ''' This class provides the queue functionalities
    '''
    queue=None
    MSG_NONE=0
    MSG_STOP=1
    MSG_KEYPRESSED=2
    MSG_KEYRELEASED=3
    MSG_TIMEOUT=4
    MSG_TEST=5
    msgTranslate={0:'NONE',1:'STOP',2:'KEYPRESSED',3:'KEYRELEASED',4:'TIMEOUT',5:'TEST'}
    
    def __init__(self):
        '''
        sets up queue
        '''
#        m=Manager()
        self.queue = JoinableQueue()
    def __str__(self, *args, **kwargs):
        return "tlu_queue: "+str(self.queue)
    
    def msgName(self,msg_num) -> str:
        '''
        Service to translate the message-id into an human readable text
        :param msg_num: message-id
        '''
        return self.msgTranslate[msg_num]
        
    def send(self,queueobject):
        '''
        Wrapper for putting an object into the queue
        :param queueobject: this object shall be placed in the queue
        '''
        self.queue.put(queueobject)
        log_info("send: {queueobject}".format(queueobject=str(queueobject)))
        
    def get(self, block=True, timeout=None):
        '''
        Retrieve an queueobject from the queue
        :param block: True if this shall block until message becomes available
        :param timeout: seconds to wait until terminating attempt
        '''
        return self.queue.get(block,timeout)
    
    def close(self):
        '''
        Close the queue by sending an STOP-object to teh queue
        '''
        log_info()
        queueobject=tlu_queueobject(self.MSG_STOP)
        self.send(queueobject)
        
    def run(self):
        '''
        Very basic implementation of runner, has to be overwritten by
        the implementing class.
        '''
        while True:
            queueobject = self.queue.get()
            if queueobject.msg_num == self.MSG_STOP:
                break
            else:
                pass
        