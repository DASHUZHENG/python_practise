#thread test
import threading
import time

def loop(a):
    
    print "test number %s" % a
    
    print 'thread %s is running...' % threading.current_thread().name
    n = 0
    while n < 5:
        n = n + 1
        print 'thread %s >>> %s' % (threading.current_thread().name, n)
        #time.sleep(1)
    print 'thread %s ended.' % threading.current_thread().name

print 'thread %s is running...' % threading.current_thread().name






t = threading.Thread(target=loop,args=("haha",),name='1')
b = threading.Thread(target=loop,args=("jiong",), name='2')

print "test position"

t.start()
b.start()

print "test position2"

t.join()
print "test position3"
b.join()

print 'thread %s ended.' % t.name
print 'thread %s ended.' % b.name