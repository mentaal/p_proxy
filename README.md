PProxy
======

This class does the following:

1. Creates a new child process using the multiprocessing library
2. A worker function function instantiates the class that is to be proxied
3. Method and attribute access gets delegated to the work function in the child
   process
4. Non blocking functionality is catered for and support for obtaining the
   results of previously invoked non blocking function calls is provided

Motivation
----------

The main reason why this module was written was to facilitate multiple
instantiations of a module which calls a DLL using ctypes. The DLL governs
access to a particular piece of hardware. Multiple instantiations of the DLL
allows the supplied functionality to be used in parallel but only if the DLL is
opened in a separate process. Otherwise, the DLL has to perform context
switching operations which are slow.

Limitations
------------

Currently, callables which are dynamically created in the class to be proxied
can't be called. This is because the function get's pickled and sent from the
child process. This with things like lambda functions as they are not picklable.
Some solutions are:

1. To potentially not return the pickled callable at all, and only grab its name
   and other metadata.
2. Use options suggested [here](http://stackoverflow.com/questions/8804830/python-multiprocessing-pickling-error)


Hazards
-------

Need to ensure that underlying queues are empty before exiting.
Do this with `p_obj._pp_get_last()`

see here: http://bugs.python.org/issue8426

pertintant paragraph:

    That's because join() will wait until the feeder thread has managed to
    write all the items to the underlying pipe/Unix socket, and this might
    hang if the underlying pipe/socket is full (which will happen after
    one has put around 128K without having popped any item).
