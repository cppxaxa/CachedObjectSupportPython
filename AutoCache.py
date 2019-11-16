import threading
import time
import uuid

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self.__stop_event = threading.Event()
        self.setDaemon(True)

    def stop(self):
        self.__stop_event.set()

    def stopped(self):
        return self.__stop_event.is_set()


def CachedCreate(instance, ttl = 86400):
    strUuid = str(uuid.uuid4())
    strUuid = '_' + strUuid.replace('-', '_')
    globals()[strUuid] = instance
    globals()[strUuid + '_lock'] = threading.Event()
    globals()[strUuid + '_ttl'] = ttl
    globals()[strUuid + '_destroyer'] = StoppableThread(target=_CachedDestroy, args=[strUuid, ttl])
    globals()[strUuid + '_destroyer'].start()
    return strUuid

def _CachedDestroy(strUuid, ttl):
    time.sleep(ttl)
    while globals()[strUuid + '_lock'].is_set():
        time.sleep(0.33)
    globals()[strUuid + '_lock'].set()
    globals()[strUuid] = None
    globals()[strUuid + '_destroyer'] = None
    globals()[strUuid + '_ttl'] = 0
    globals()[strUuid + '_lock'].clear()

def CachedGet(strUuid):
    while globals()[strUuid + '_lock'].is_set():
        time.sleep(0.33)
    instance = globals()[strUuid]
    if instance is not None:
        globals()[strUuid + '_lock'].set()
        globals()[strUuid + '_destroyer'].stop()
        globals()[strUuid + '_destroyer'] = StoppableThread(target=_CachedDestroy, args=[strUuid, globals()[strUuid + '_ttl']])
        globals()[strUuid + '_destroyer'].start()
        globals()[strUuid + '_lock'].clear()
        return instance
    return None




if __name__ == '__main__':
    # objRef = CachedCreate(set(), 5)
    # print(objRef)

    if 'objRef' not in globals():
        objRef = CachedCreate(set(), 5)

    while True:
        val = input()

        if CachedGet(objRef) is None:
            print("Absent")
            objRef = CachedCreate(set(), 5)
        else:
            print("Present")