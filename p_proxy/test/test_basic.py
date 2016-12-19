import pytest
def test_method(p_obj):
    p_obj.print_a()
    p_obj.print_a()

def test_get_5(p_obj):
    assert p_obj.get_5() == 5


def test_get_attr(p_obj):
    assert p_obj.a == 1
    assert p_obj.b == 2
    assert p_obj.c == 3
    #assert p_obj.e(6) == 6

def test_set_attr(p_obj):
    p_obj.d = 'blah'
    assert p_obj.d == 'blah'
    p_obj.d = ['blah2']
    assert p_obj.d == ['blah2']

def test_exc(p_obj):
    with pytest.raises(ValueError):
        p_obj.raise_exc()


#def test_method_args(p_obj):
