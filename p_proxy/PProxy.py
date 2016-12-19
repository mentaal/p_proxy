#import multiprocessing as mp
from multiprocessing import Process, Queue
import logging
import inspect
from inspect import Signature, Parameter
import traceback
import sys

logger = logging.getLogger(__name__)

def f(receive_q, send_q, cls, cls_args, cls_kwargs):
    #initialize class
    c = cls(*cls_args, **cls_kwargs)
    while True:
        tn_num, op, attr, args, kwargs = receive_q.get()
        result = None
        exc = None
        try:
            if op == 'call' and attr == '_quit_':
                send_q.put((tn_num, result, None))
                return
            if op == 'set':
                print("attr now: {}, args now:{}".format(attr, args))
                setattr(c, attr, args[0])
            elif op == 'get':
                result = getattr(c, attr)
            elif op == 'call':
                result = getattr(c, attr)(*args, **kwargs)
        except Exception as e:
            #print("Sending exception!")
            e.tb = traceback.format_exc()
            send_q.put((tn_num, result, e))
            return
        else:
            #print("Sending result...")
            send_q.put((tn_num, result, None))


class PProxy():
    '''class to act as a proxy for another.
    Perform the following tasks:
        1) analyze passed in class and create proxy functions+properties
        2) setup queue/pipe based infrastructure to communicate with a handler in
        another process
        3)launch handler task in another process
        '''
    def __init__(self, cls, *, cls_args=(), cls_kwargs=None):
        super().__setattr__('tn_num',0)
        super().__setattr__('_send_q', Queue())
        super().__setattr__('_receive_q', Queue())
        if cls_kwargs is None:
            cls_kwargs = {}

        super().__setattr__('_p', Process(target=f, args=(
                self._send_q, self._receive_q, cls, cls_args, cls_kwargs)))
        self._p.start()
        self._cache_funcs(cls)

    def _cache_funcs(self, cls):
        'create local function proxies and also include signature info'
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            def proxy_func():
                n = name
                f = lambda *args, **kwargs: self._issue_tn(
                        'call', n, *args, **kwargs)
                f.__signature__ = Signature.from_callable(func)
                return f
            super().__setattr__(name, proxy_func())


    def _get_tns(self):
        old_results = []
        while True:
            tn_num, result, e = self._receive_q.get()
            #print("Received tn_num is: {}".format(tn_num))
            if e:
                print(e.tb)
                raise e
            if tn_num < self.tn_num:
                interim_results.append(result)
            else:
                #print("Returning result...")
                return result, old_results

    def _issue_tn(self, op, attr, *args, async=False, **kwargs):
        #print("In _issue_tn, op: {}, attr: {}".format(op, attr), flush=True)
        self._send_q.put((self.tn_num, op, attr, args, kwargs))
        result = None
        if not async:
            result, old_results = self._get_tns()
        super().__setattr__('tn_num', self.tn_num + 1)
        return result #implicitly discarding old results



    def __getattr__(self, item):
        #print("in getattr, item: {}".format(item), flush=True)
        print("Self: {}".format(self))
        remote_item = self._issue_tn('get', item)
        if callable(remote_item):
            f = lambda *args, **kwargs: self._issue_tn(
                    'call', item, *args, **kwargs)
            #TODO - need to address the fact that this code won't work - cannot pickle dynamically created callables
            f.__signature__ = Signature.from_callable(remote_item)
            #now cache it to speed up next lookup
            super().__setattr__(name, f)
            return f
        else:
            return remote_item

    def __setattr__(self, item, value):
        self._issue_tn('set', item, value)

    def _stop(self):
        self._issue_tn('call', '_quit_', async=True)



if __name__ == '__main__':
    from .test.RefCls import RefCls
    p_obj = PProxy(RefCls, cls_args=(1,2,3))
    p_obj.print_a()
    p_obj.stop()






