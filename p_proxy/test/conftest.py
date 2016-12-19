import pytest
from RefCls import RefCls
from p_proxy.PProxy import PProxy

@pytest.fixture(scope='session')
def p_obj():
    p_obj = PProxy(RefCls, 1,2,3)
    return p_obj

