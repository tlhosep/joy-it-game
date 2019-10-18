""" module: tlu_threads
** Content **
This module wraps the threading fiunctionalities in use

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
"""

import time
import logging
import threading

logger=logging.getLogger(__name__)

threadlist=[]

def startThreadClass(threadclass):
    """Start a Threading Class-object
    
    :param threadclass: The class that should be started
    """
    global threadlist
    threadclass.start()
    threadlist.append(threadclass.name)
    logging.debug('Thread started: '+threadclass.name)
    return threadclass

def startThread(thread, **kwargs):
    """Start a usual Method as a Thread
    
    :param thread: The method that should be used for threading
    """
    global threadlist
    task=threading.Thread(target=thread, **kwargs)
    task.start()
    threadlist.append(task.name)
    logging.debug('Thread started: '+task.name)
    return task
    
def abortThread(thread,timeout=10,msg=""):
    """Terminate the thread (if given)
    
    abort thread, if timeout reached, terminate
    :param thread: The thread that should be terminated
    :param timeout: seconds to wait before returning
    :param msg: Message for logging purposes in case we had a problem
    """
    if thread == None:
        return # not running ;)
    global threadlist
    logger.debug('Thread terminated: '+thread.name)
    thread.is_aborted=True
    thread.join(timeout/2) #usually waits until terminated, or if timeout (in seconds) reached
    count=5*timeout
    try:
        threadlist.remove(thread.name)
    except:
        logger.error("The following thread could not be found in the global thread list: "+str(thread.name))
    while count>0:
        time.sleep(0.1)
        if not thread.is_alive():
            break
        count -= 1
    if count < 1:
        if thread.is_alive():
            # There is no option available to end the thread hardly, this is only possible for processes
            logger.error('thread '+str(thread.name)+' is still alive, could not be shut down.. ->'+str(msg))
            return False
    return True
    
def is_running(self,thread):
    """Check if the thread is still alive
    
    :param thread: The thread that should be checked
    """
    if (thread != None):
        logging.debug("Alive-State of "+str(thread.name)+" is:"+str(thread.is_alive()))
        if thread.is_alive():
            return True
    return False 
