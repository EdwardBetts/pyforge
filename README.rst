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

 from forge import Forge
 ...
 f = Forge()

There shouldn't be a real reason for keeping more than one forge manager. What it is typically used for is creating mocks::

 class SomeClass(object):
     def f(self, a, b, c):
         ...

 f = Forge()
 mock = f.create_mock(SomeClass)

Mock tests usually act in a record-replay manner. You record what you expect your mock to do, and then replay it, while Forge tracks what happens and makes sure it is correct::

 f.is_recording() # --> True
 mock.f(1, 2, 3)
 mock.f(3, 4, 5)

 f.replay()
 f.is_recording() # --> False
 f.is_replaying() # --> True
 mock.f(1, 2, 3)
 mock.f(3, 4, 5)

 f.verify() # this verifies no more calls are expected

To start over working from scratch, you can always perform::

 f.reset()

Just like classes yield mocks, regular functions yield stubs, through the use of *Forge.create_function_stub*::

 def some_func(a, b, c):
     pass

 stub = f.create_function_stub(some_func)

As methods and functions are recorded, their signature is verified against the recorded calls. Upon replay the call must match the original call, so you shouldn't worry too much about accidents concerning the function signature.
 
Actions
-------
When expecting a call on a stub, you can control what happens *when* the call takes place. Supported cases are:

- controlling the return value::

   my_stub(1, 2, 3).and_return(666)

- calling another function (no arguments)::

   my_stub(1, 2, 3).and_call(callback)

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

Ordering
--------
By default, forge verifies that the order in which calls are made in practice is the same as the record flow.
You can, however, control it and create groups in which order does not matter::

 forge = Forge()
 mock = forge.create_mock(SomeClass)
 
 mock.func(1)
 mock.func(2)
 mock.func(3) # so far order must be kept
 with forge.any_order():
     mock.func(4)
     mock.func(5)
 mock.func(6)

 forge.replay()
 mock.func(1)
 mock.func(2)
 mock.func(3)
 mock.func(5) # ok!
 mock.func(4) # also ok!
 mock.func(6)

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