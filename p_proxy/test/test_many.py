import pytest
from RefCls import RefCls
from p_proxy.PProxy import PProxy

def test_many():
    #lots!
    objs = [PProxy(RefCls, 1,2,3) for i in range(5)]
    for obj in objs:
        obj.print_a()
    #implicit shutdown expected



