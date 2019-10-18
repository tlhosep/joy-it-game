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

def emulateKey(kbQueue):
    """
    Main loop to check for keyboard inputs
    :param kbQueue: Queue where the messages shall be placed
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
        
    keymap={'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15,'g':16,'i':100,'k':200,'m':300,'j':400}
    lastkey=0
    printMsg=True
    queue=kbQueue
    print('Keyboard-simulation for hardware-keys:')
    print_help()
    while True:
        if printMsg:
            print("Please press a key (1..9, a..g, i,j,k,m); t=terminate, h=help:")
        try:
            key = sys.stdin.read(1) #input()
            if key != None and key=='t':
                return
            elif key != None and key=='h':
                print_help()
            elif key:
                if key in keymap:
                    lastkey=keymap[key]
                    obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYPRESSED,keymap[key])
                    try:
                        queue.put(obj)
                    except Exception as e:
                        print('Key could not be passed to game, reason was: '+str(e))
                    printMsg=True
                else:
                    obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_KEYRELEASED,lastkey)
                    try:
                        queue.put(obj)
                    except Exception as e:
                        print('Key could not be passed to game, reason was: '+str(e))
                    printMsg=False
            else:
                printMsg=False
            time.sleep(0.2) #wait for next check
        except KeyboardInterrupt:
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_STOP)
            queue.put(obj)
            print('\nNo more keys awaited due to interrupt')
            return
        except Exception as e:
            obj=tlu_queueobject(tlu_queue.tlu_queue.MSG_STOP)
            queue.put(obj)
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

    def handle(self, *args, **options):
        """
        Main loop to process the commandline request
        """
        port=50200
        if options['port'] != None:
            port=int(options['port'])
        class KbQueueManager(BaseManager):
            pass
        KbQueueManager.register('get_kbQueue')
        m = KbQueueManager(address=('localhost', port),authkey=b'tlu_abracadabra')
        print('...trying to connect to remote Queue on port '+str(port))
        queue=None
        try:
            m.connect()
            queue = m.get_kbQueue()
        except Exception as e:
            print('That did not work, please retry and check that the game is running! Reason was:\n'+str(e))
            return
        emulateKey(queue)
