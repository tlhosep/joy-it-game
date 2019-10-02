""" module: tlu_threadDecorator

This module provides a decorator to ease generating a thread
It is mostly used for hardware-functionalities 

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
"""

from threading import Thread

def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator