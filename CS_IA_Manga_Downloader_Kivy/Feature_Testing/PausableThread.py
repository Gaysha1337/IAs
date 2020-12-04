import threading, time
class PausableThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self._event = threading.Event()
        if target:
            args = (self,) + args
        super(PausableThread, self).__init__(group, target, name, args, kwargs)

    def pause(self):
        self._event.clear()

    def resume(self):
        self._event.set()

    def _wait_if_paused(self):
        self._event.wait()


def t(thread):
    print("t func has started")
    time.sleep(1)
    thread.start()
    print("thread started")

    for i in range(10000):
        if i == 10:
            thread.pause()
            print("paused")
            time.sleep(3)
        if i == 2000:
            print("resumed")
            thread.resume()
    print("done")
        
if __name__ == "__main__":
    x = PausableThread(target=print,args=("cat","dog"))
    t(x)
    x.resume()