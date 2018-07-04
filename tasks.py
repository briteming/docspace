try:
    from queue import Queue
except:
    import Queue
import threading

# Create your tests here.
try:
    q = Queue(10)
except:
    q = Queue.Queue(10)

