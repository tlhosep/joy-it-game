""" module: tlu_processes

This module provides wrapper and services to use processes

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
"""
import time
import logging

logger=logging.getLogger(__name__)

processlist=[]

def numberOfProcesses():
    """
    Return the number of currently started processes
    """
    return len(processlist)

def startProcess(process):
    """
    Start a given process
    :param process: process to start
    """
    global processlist
    process.daemon=True
    process.start()
    processlist.append(process.name)
    logging.debug("Process started: "+str(process.name))
    return process

def abortProcess(process,timeout=10,msg=""):
    """
    Abort the named process
    :param process: process to be aborted
    :param timeout: seconds to wait before going for a hard termination
    :param msg: Log-Message (optional)
    """
    global processlist
    count=10*timeout
    processlist.remove(process.name)
    process.terminate()
    while count>0:
        time.sleep(0.1)
        if not process.is_alive():
            break
        count -= 1
    if count < 1:
        logger.error("the process with id "+str(process.ident)+" could not be gracefully terminated:"+str(msg))
        return False
    return True
    
def is_running(self,process):
    """
    Check if the given process is still running
    :param process: Process to examine
    """
    if (process != None):
        logging.debug("Alive-State of "+str(process.ident)+" is:"+str(process.is_alive()))
        if process.is_alive():
            return True
    return False 
