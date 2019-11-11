""" module/commandline app: sendKeys
** Content **
This app shall work as a commandline interface to put keys pressed into a dedicated queue to interact with the game

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-09-30 
"""

from django.core.management.base import BaseCommand
from multiprocessing.managers import BaseManager
import sys
from tlu_services.tlu_queue import tlu_queueobject
from tlu_services import tlu_queue
import time
from queue import Empty

def emulateKey(kbQueue,cqueue,tqueue):
    """
    Main loop to check for keyboard inputs
    :param kbQueue: Queue where the keypad related messages shall be placed
    :type kbQueue:Queue
    :param cqueue: Cursor-Key related queue
    :type cqueue: Queue
    :param tqueue: Tochpad-touches related queue
    :type tqueue: Queue
    """
    def print_help():
        """
        helper to display help
        """
        print('1..9 = Matrix-keys 1..9')
        print('a..g = Matrix-keys 10..16')
        print('i=cursor up')
        print('k=cursor right')
        print('m=cursor down')
        print('j=cursor left')
        print('#=Touchpad')
        print("r=release queues")
        print('t=terminate emulation')
        print('h=This help')
    
    def printQueue(q,name):
        while True:
            try:
                queueobject = q.get(block=False,timeout=1)
                q.task_done()
            except Empty:
                print(name+' is now empty')
                return
            except Exception as e:
                print('Exception while reading from key-q '+name+':'+str(e))
                return
            print(str(queueobject))
        
    keymap={'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15,'g':16}
    cursormap={'i':100,'k':200,'m':300,'j':400}
    printMsg=True
    print('Keyboard-simulation for hardware-keys:')
    print_help()
    while True:
        if printMsg:
            queuempty=kbQueue.empty()&cqueue.empty()&tqueue.empty()
            print("Please press a key (1..9, a..g, i,j,k,m); #=touch, t=terminate, h=help (queues empty:"+str(queuempty)+"):")
            """
            print("Kb="+str(kbQueue.empty()))
            print("curs="+str(cqueue.empty()))
            print("touch="+str(tqueue.empty()))
            """
        try:
            key = sys.stdin.read(1) #input()
            if key != None and key=='t':
                return
            elif key != None and key=='h':
                print_help()
            elif key != None and key=='r':
                printQueue(kbQueue,"Keyboard")
                printQueue(cqueue, "Cursor")
                printQueue(tqueue, "Touch")
            elif key != None and key=='#':
                obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_TOUCH_PRESSED)
                try:
                    tqueue.put(obj)
                except Exception as e:
                    print('Touch-event could not be passed to game, reason was: '+str(e))
                printMsg=True
            elif key:
                if key in keymap:
                    obj1=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,keymap[key])
                    obj2=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYRELEASED,keymap[key])
                    try:
                        kbQueue.put(obj1)
                        kbQueue.put(obj2)
                    except Exception as e:
                        print('Key could not be passed to game, reason was: '+str(e))
                    printMsg=True
                elif key in cursormap:
                    obj1=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,cursormap[key])
                    obj2=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYRELEASED,cursormap[key])
                    try:
                        cqueue.put(obj1)
                        cqueue.put(obj2)
                    except Exception as e:
                        print('Key could not be passed to game, reason was: '+str(e))
                    printMsg=True
                else:
                    printMsg=False
            else:
                printMsg=False
            time.sleep(0.2) #wait for next check
        except KeyboardInterrupt:
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_STOP)
            kbQueue.put(obj)
            print('\nNo more keys awaited due to interrupt')
            return
        except Exception as e:
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_STOP)
            kbQueue.put(obj)
            print('\nNo more keys awaited due to exception / '+str(e))
            return


class Command(BaseCommand):
    """
    Commandline interface to scan for keys pressed.
    The Key will then be forwarded to the remote Queue for further processing
    """
    help = "Scans for keys until termination is requested"

    def add_arguments(self, parser):
        parser.add_argument('--port', help="Portnumber of the queue", required=False)

    def handle(self, *args, **options):  # @UnusedVariable
        """
        Main loop to process the commandline request
        """
        port=50200
        if options['port'] != None:
            port=int(options['port'])
        class KbQueueManager(BaseManager):
            pass
        class CursorQueueManager(BaseManager):
            pass
        class TouchQueueManager(BaseManager):
            pass
        KbQueueManager.register('get_kbQueue')
        CursorQueueManager.register('get_cursorQueue')
        TouchQueueManager.register('get_touchQueue')
        k = KbQueueManager(address=('localhost', port),authkey=b'tlu_abracadabra')
        c = CursorQueueManager(address=('localhost',port+1),authkey=b'tlu_cursormiracle')
        t = TouchQueueManager(address=('localhost',port+2),authkey=b'tlu_touchme')
        print('...trying to connect to remote Queue on ports '+str(port)+" .. "+str(port+2))
        kqueue=None
        cqueue=None
        tqueue=None
        try:
            k.connect()
            kqueue = k.get_kbQueue()
            c.connect()
            cqueue = c.get_cursorQueue()
            t.connect()
            tqueue = t.get_touchQueue()
        except Exception as e:
            print('That did not work, please retry and check that the game is running! Reason was:\n'+str(e))
            return
        emulateKey(kqueue,cqueue,tqueue)
