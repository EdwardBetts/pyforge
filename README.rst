What is it?
===========
Forge is a mocking library for Python. It draws most of its inspiration from Mox (http://code.google.com/p/pymox). It is aimed to be simple, but still feature-rich, and provide maximum flexibility for unit testing using the mock approach.

Installation
============
Installing forge is pretty much the same as most of the packages you already know

::

 python setup.py install

Usage
=====

Basics
------
Forge mostly creates mock objects and function stubs, but in a variety of flavors. Using Forge always starts with creating a mock manager, called a Manager, which is created with the Forge class::

 >>> from forge import Forge
 >>> forge_manager = Forge()

There shouldn't be a real reason for keeping more than one forge manager. What it is typically used for is creating mocks::

 >>> class SomeClass(object): 
 ...     def f(self, a, b, c):
 ...         pass    
 >>> mock = forge_manager.create_mock(SomeClass)

Mock tests usually act in a record-replay manner. You record what you expect your mock to do, and then replay it, while Forge tracks what happens and makes sure it is correct::

 >>> forge_manager.is_recording() 
 True
 >>> mock.f(1, 2, 3) # doctest: +ELLIPSIS
 <...>
 >>> mock.f(3, 4, 5) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> forge_manager.is_recording()
 False
 >>> forge_manager.is_replaying()
 True
 >>> mock.f(1, 2, 3)
 >>> mock.f(3, 4, 5)
 >>> forge_manager.verify() # this verifies no more calls are expected

To start over working from scratch, you can always perform::

 >>> forge_manager.reset()

Just like classes yield mocks, regular functions yield stubs, through the use of *Forge.create_function_stub*::

 >>> def some_func(a, b, c):
 ...     pass
 >>> stub = forge_manager.create_function_stub(some_func)

As methods and functions are recorded, their signature is verified against the recorded calls. Upon replay the call must match the original call, so you shouldn't worry too much about accidents concerning the function signature.
 
Actions
-------
When expecting a call on a stub, you can control what happens *when* the call takes place. Supported cases are:

- controlling the return value::

   my_stub(1, 2, 3).and_return(666)

- calling another function (no arguments)::

   my_stub(1, 2, 3).and_call(callback)

- calling another function with certain arguments/keyword arguments::

   my_stub(1, 2, 3).and_call(callback, args=(100, 200), kwargs={'some_arg':20})

- calling another function (with the arguments of the call)::

   my_stub(1, 2, 3).and_call_with_args(callback)

- raising an exception (happens after all callbacks are fired)::

   my_stub(1, 2, 3).and_raise(MyException())

Comparators
-----------
If you don't know the exact value that the argument to a function is going to get, you sometimes have to use predicates to help you distinguish valid cases from invalid ones. For starters we'll mention that mock objects will only compare 'true' to themselves, so you shouldn't worry about any funky business as far as mock comparison goes.

To complete the picture, if you want to assert all sorts of checks on the arguments you are recording, you can use comparators. For instance, the following doesn't care about which argument is passed to 'name', as long as it is a string::

 my_stub(name=IsA(basestring))

Many comparators exist in Forge:

* ``Is(x)``: compares true only if the argument is *x*
* ``IsA(type)``: compares true only if the argument is of type *type*
* ``RegexpMatches(regexp, [flags])``: compares true only if the argument is a string, and matches *regexp*
* ``Func(f)``: compares true only if *f* returns True for the argument
* ``IsAlmost(value, [places])``: compares true only if the argument is almost identical to *value*, by *places* digits after the floating point
* ``Contains(element)``: compares true only if *element* exists in the argument
* ``HasKeyValue(key, value)``: compares true only if the argument has *key* as a key, whose value is *value*
* ``HasAttributeValue(attr, value)``: same as HasKeyValue, but for attributes
* ``Anything()``: always compares true
* ``And(...), Or(...), Not(c)``: and, or and a negator for other comparators

Ordinary Function Stubs
-----------------------
You can easily create stubs for global functions using the *create_function_stub* API::

 >>> fake_isinstance = forge_manager.create_function_stub(isinstance)

Replacing Methods and Functions with Stubs
------------------------------------------
Forge includes a mechanism for installing (and later removing) stubs instead of ordinary methods and functions

Ordering
--------
By default, forge verifies that the order in which calls are made in practice is the same as the record flow.
You can, however, control it and create groups in which order does not matter::

 >>> class SomeClass(object):
 ...     def func(self, arg):
 ...        pass
 >>> mock = forge_manager.create_mock(SomeClass)
 >>> mock.func(1) # doctest: +ELLIPSIS
 <...>
 >>> mock.func(2) # doctest: +ELLIPSIS
 <...>
 >>> mock.func(3) # doctest: +ELLIPSIS
 ... # so far order must be kept
 <...>
 >>> with forge_manager.any_order(): # doctest: +ELLIPSIS
 ...     mock.func(4)
 ...     mock.func(5)
 <...>
 <...>
 >>> mock.func(6) # doctest: +ELLIPSIS
 <...>
 >>> forge_manager.replay()
 >>> mock.func(1)
 >>> mock.func(2)
 >>> mock.func(3)
 >>> mock.func(5) # ok!
 >>> mock.func(4) # also ok!
 >>> mock.func(6)

Wildcard Mocks
--------------
Although not recommended, sometimes you just want a mock that accepts anything during record, and just verifies that you stick to it in replay. This is useful for prototyping an interface that doesn't exist yet. This is done in Forge by using *wildcard mocks*::

 mock = forge.create_wildcard_mock()
 stub = forge.create_wildcard_function_stub()
 mock.f()
 mock.g(1, 2, 3, d=4) # ok - mock is a wildcard
 stub()
 stub(1, 2, 3, d=4)
 
 forge.replay()
 ...

Class Mocks
-----------
Sometimes you would like to simulate the behavior of a class, and not an object. Forge allows to do this with the *create_class_mock* API::

 class_mock = forge.create_class_mock(MyClass)
 class_mock.regular_method() # <-- will raise an exception, because regular methods cannot
                             #     be called directly on classes
 class_mock.some_class_method() # ok
 class_mock.some_static_method() # also ok
 class_mock(1, 2, 3).and_return(...) # will check the signature against the class constructor

Hybrid Mocks
------------
Suppose you have a class like the following::

 class File(object):
     def __init__(self, filename):
         self.f = open(filename, "rb")
     def read(self, size):
         ...
     def log(self, buffer):
         ...
     def read_and_log(self, size):
         data = self.read(size)
         self.log(data)
         return data

Now, suppose you want to write a test for read_and_log, while mimicking the behavior of read() and log(). This is quite common, because sometimes methods in your classes have lots of side effects which are hard to plumb during test writing. One easy approach would be to create a File object and to replace read() and log() with stubs (see above). This is fine, but the problem is with the class construction, which opens a file for reading.

In some cases, constructors (especially in legacy code to which you add tests) do lots of things that are hard to stub, or that are likely to change thus breaking any stubbing work you might install. For this case Forge has hybrid mocks::

 mock = forge.create_hybrid_mock(File)
 mock.read(20).and_return("data")
 mock.log(data)
 forge.replay()
 assert mock.read_and_log(20) == "data"
 forge.verify()

Hybrid mocks are, well, hybrid. They behave as regular mocks during record, but calling any method during replay that hasn't been recorded will invoke the original method on the mock, thus testing it in an isolated environment.
