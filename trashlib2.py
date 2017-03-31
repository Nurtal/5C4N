import time
import sys
import math
import signal


# display progress bar in command line
for i in range(101):
    time.sleep(0.01)

    factor = math.ceil((i/2))

    progress_bar = "#" * int(factor)
    progress_bar += "-" * int(50 - factor)

    display_line = "|"+progress_bar+"|"
    sys.stdout.write("\r%d%%" % i)
    sys.stdout.write(display_line)
    sys.stdout.flush()





from multiprocessing import Process, Queue


def longfunction(x, y, queue):
    res = 0
    while True:
        res += x*y
    queue.put(res)

def call_of_longfunction():
    queue = Queue() #using to get the result
    proc = Process(target=longfunction, args=(1, 3, queue,)) #creation of a process calling longfunction with the specified arguments
    proc.start() #lauching the processus on another thread
    try:
        res = queue.get(timeout=1) #getting the resultat under 1 second or stop
        proc.join() #proper delete if the computation has take less than timeout seconds
    except: #catching every exception type
        proc.terminate() #kill the process
        print "too long"



call_of_longfunction()
