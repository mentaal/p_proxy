import pytest
from RefCls import RefCls
from p_proxy.PProxy import PProxy
import string
import random

def test_many():
    #lots!
    objs = [PProxy(RefCls, 1,2,3) for i in range(5)]
    for obj in objs:
        obj.print_a()
    #implicit shutdown expected

def test_many_long_strings():
    objs = [PProxy(RefCls, 1,2,3) for i in range(5)]
    long_data = ''.join(random.choices(string.printable, k=200000))
    for obj in objs:
        for i in range(1000):
            s_upper = obj.upper(long_data[:random.randint(100000,200000)],
                        _async=True)

    for obj in objs:
        r = obj._pp_get_last()[0]
