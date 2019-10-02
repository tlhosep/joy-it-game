""" module: tlu_processDecorator

This module provides a decorator to ease generating a process
It is mostly used for hardware-functionalities 

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
"""

from multiprocessing import Process

def start_new_process(function):
    def decorator(*args, **kwargs):
        global_process = Process(target = function, args=args, kwargs=kwargs)
        global_process.daemon = True
        global_process.start()
    return decorator