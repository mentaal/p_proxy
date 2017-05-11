import pytest
import random
import string
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

def test_async(p_obj):
    for i in range(10):
        p_obj.string_num(i, _async=True)
    results = p_obj._pp_get_last(5)
    assert results == [str(n) for n in range(5, 10)]

def test_get_array(p_obj):
    a = p_obj.get_array()
    assert a == list(range(10))

def test_get_array_async(p_obj):
    for i in range(5):
        p_obj.get_array(_async=True)
    a = p_obj._pp_get_last()[0] #_pp_get_last returns a list
    assert a == list(range(10))



def test_async_exc(p_obj):
    with pytest.raises(IndexError):
        results = p_obj._pp_get_last()

def test_short_strings(p_obj):
    for i in range(5000):
        s_upper = p_obj.upper(''.join(random.choices(string.printable,
                                k=random.randint(1,100))))


def test_long_strings(p_obj):
    long_data = ''.join(random.choices(string.printable, k=200000))
    for i in range(5000):
        s_upper = p_obj.upper(long_data[:random.randint(100000,200000)])

