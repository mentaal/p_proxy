import pytest
from RefCls import RefCls
from p_proxy.PProxy import PProxy

@pytest.fixture(scope='session')
def p_obj():
    p_obj = PProxy(RefCls, cls_args=(1,2,3))
    yield p_obj
    #print("Now cleaning up...")
    p_obj._stop()

