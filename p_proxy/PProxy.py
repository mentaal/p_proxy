import multiprocessing as mp
from multiprocessing import Process, Queue
import logging
import inspect
from inspect import Signature
import signal
import traceback
import atexit

logger = logging.getLogger(__name__)

#logger = mp.get_logger()
#logger.propagate = True
#logger.setLevel(logging.DEBUG)


# Save a reference to the original signal handler for SIGINT.
default_handler = signal.getsignal(signal.SIGINT)


def f(receive_q, send_q, cls, cls_args, cls_kwargs):
    # Set signal handling of SIGINT to ignore mode.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    #initialize class
    c = cls(*cls_args, **cls_kwargs)
    while True:
        tn_num, op, attr, args, kwargs = receive_q.get()
        #print("Worker: tn_num: {}, op: {}, attr: {}".format(tn_num, op, attr))
        result = None
        exc = None
        try:
            if op == 'call' and attr == '_quit_':
                send_q.put((tn_num, result, None))
                return
            if op == 'set':
                #print("attr now: {}, args now:{}".format(attr, args))
                setattr(c, attr, args[0])
            elif op == 'get':
                result = getattr(c, attr)
            elif op == 'call':
                result = getattr(c, attr)(*args, **kwargs)
        except Exception as e:
            #print("Worker: Sending exception!")
            e.tb = traceback.format_exc()
            send_q.put((tn_num, result, e))
        else:
            #print("Worker: Sending result...")
            send_q.put((tn_num, result, None))


class PProxy():
    '''class to act as a proxy for another.
    Perform the following tasks:
        1) analyze passed in class and create proxy functions+properties
        2) setup queue/pipe based infrastructure to communicate with a handler in
        another process
        3)launch handler task in another process
        '''
    def __init__(self, cls, *cls_args, **cls_kwargs):
        self._pp_tn_num = 0
        self._pp_num_in_flight = 0
        self._pp_send_q    = Queue()
        self._pp_receive_q = Queue()
        if cls_kwargs is None:
            cls_kwargs = {}

        self._pp_p = Process(target=f, args=(
                self._pp_send_q, self._pp_receive_q, cls, cls_args, cls_kwargs))
        self._pp_p.start()
        self._pp_cache_funcs(cls)
        atexit.register(self._pp_issue_tn, 'call', '_quit_', async=True)


    def _pp_cache_funcs(self, cls):
        'create local function proxies and also include signature info'
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            def proxy_func():
                n = name
                f = lambda *args, _async=False, **kwargs: self._pp_issue_tn(
                        'call', n, *args, async=_async, **kwargs)
                f.__signature__ = Signature.from_callable(func)
                f.__doc__ = func.__doc__
                return f
            super().__setattr__(name, proxy_func())


    def _pp_get_tns(self):
        old_results = []
        while True:
            _tn_num, result, e = self._pp_receive_q.get()
            self._pp_num_in_flight -= 1
            logger.debug("In _pp_get_tns,_tn_num: {}. in_flight: {}".format(
                _tn_num, self._pp_num_in_flight) + "result: {}".format(result))
            #print("Received _tn_num is: {}".format(_tn_num))
            if e:
                print(e.tb)
                raise e
            #_pp_issue_tn increments _tn_num for the next command
            if _tn_num < self._pp_tn_num - 1:
                old_results.append(result)
            else:
                #print("Returning result: {}, old_results: {}".format(
                #    result, old_results))
                return result, old_results

    def _pp_issue_tn(self, op, attr, *args, async=False, **kwargs):
        logger.debug("In _pp_issue_tn, op: {}, attr: {}".format(op, attr))
        self._pp_send_q.put((self._pp_tn_num, op, attr, args, kwargs))
        self._pp_num_in_flight += 1
        logger.debug("In _pp_issue_tn, _pp_num_in_flight: {}".format(self._pp_num_in_flight))
        result = None
        self._pp_tn_num += 1
        if not async:
            result, old_results = self._pp_get_tns()
        return result #implicitly discarding old results



    def __getattr__(self, item):
        #print("in getattr, item: {}".format(item), flush=True)
        remote_item = self._pp_issue_tn('get', item)
        if callable(remote_item):
            f = lambda *args, _async=False, **kwargs: self._pp_issue_tn(
                    'call', item, *args, async=_async, **kwargs)
            #TODO - need to address the fact that this code won't work - cannot pickle dynamically created callables
            f.__signature__ = Signature.from_callable(remote_item)
            #now cache it to speed up next lookup
            super().__setattr__(name, f)
            return f
        else:
            return remote_item

    def _pp_get_last(self, num_items=1):
        '''get the last number of return values accumulated due to non blocking
        transactions. Returns a list!'''
        if num_items > self._pp_num_in_flight:
            raise IndexError("Too many return results requested")
        result, old_results = self._pp_get_tns()
        old_results.append(result)
        return old_results[-num_items:]

    def __setattr__(self, item, value):
        if item[:4] == '_pp_':
            #use base class
            super().__setattr__(item, value)
        else:
            self._pp_issue_tn('set', item, value)

    def _pp_stop(self):
        self._pp_issue_tn('call', '_quit_', async=True)
        atexit.unregister(self._pp_issue_tn)



if __name__ == '__main__':
    from .test.RefCls import RefCls
    p_obj = PProxy(RefCls, 1,2,3)
    p_obj.print_a()






