class RefCls():
    def __init__(self, a,b,c):
        self._a = a
        self.b = b
        self.c = c
        # see this for the error in using the below lambda http://stackoverflow.com/questions/8804830/python-multiprocessing-pickling-error
        self.e = lambda x:x

    @property
    def a(self):
        return self._a

    def get_5(self):
        return 5

    def print_a(self):
        print("A value: {}".format(self.a))

    def raise_exc(self):
        raise ValueError("Test exception..")
