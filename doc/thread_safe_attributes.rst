.. _thread_safe_attributes-thread-safe-attributes:

Thread Safe Attributes
======================

If you use a statechart, your program is multi-threaded.

Sometimes, you will want to access an attribute of your statechart from another
thread, like the main part of your program.  When you do this, you are trying to
access memory that could be changed in one thread while it is being read in by
another thread.  

To see why this is an issue imagine using a calculator to solve a simple math
problem: calculate the value of ``b``, starting with ``a == 0.35``, given the
following equation:

.. code-block:: python
  
  b = a*cos(0.45) + 3*a^1.2

Seems simple enough.  Suppose you pick a straight-forward strategy: 

   * mark down the value of ``a`` on a piece of paper so you can reference it as you work
   * break the calculation into ``a * cos(0.45)`` and ``3*a*1.2``
   * then add these results together to find ``b``

But while calculated the ``a*cos(0.45)`` part of the problem, someone grabs your
paper, changes your temporary value of ``a`` to ``0.3``, then puts it back on
your desk.  You don't notice.  When you get to the ``3*a^1.2`` part of the
calculation, you use the wrong ``a`` value, so you get the wrong answer for ``b``.

This is called a **race condition**.  Here our ``a`` variable was shared between
two threads, you and the other person.  When you program with multiple
concurrent processes/threads and you share memory, you are exposed to this kind
of problem.

A simple way to avoid such a situation is to not share the temporary paper in
the first place.  Do not use shared attributes.

Another way to deal with it is to have one thread change a shared attribute and
have the other thread read the shared attribute.  But, this will required that
maintenance developers understand there are hidden rules in your code base;
they could innocently change something an introduce extremely subtle bugs.

Typically, shared variables are protected using thread locks.  A lock is a flag
which works across multiple threads.  You can lock the object for read/writing
while you use it.  In our example, we would lock ``a`` in its ``0.35`` state
while calculating both sub-parts of our problem then unlock it when we are done.
The other process, would simply wait until the thread-lock cleared, then they
would change the value of ``a`` to ``0.3`` and do their own work.  So, there is
a cost, you block one thread while waiting for the other to work, and you have
to share lock variables across all of your threads.  It is easy to screw this
up, and it is very hard to test for race conditions.

But why is it hard to test for race conditions?  As of Python 3, a thread will
run for 15 milliseconds before Python passes control to another thread.  Most of
the time, the common memory that is used by both threads will work as you expect
it to.  Infrequently a thread switch will occur midway through a non-atomic
operation, where some shared value is to be changed by the other
thread.  After this unlikely event, your thread will re-gain control and finish
its calculation producing the wrong answer.

These kinds of bugs are more probabilistic than deterministic, because Python's
access to the system clock is jittery.  It's timing will never be the same for
every two runs of the program (it's like playing a slot machine) so it will be
hard for you to reproduce your issue.

The miros library accepts that people will want to access a statechart's
internal attributes from the outside.  Significant efforts have been made to
make this kind of activity easy for you to do in a "thread-safe" manner.  The
``ThreadSafeAttributes`` class was constructed to eat the complexity of making
thread safe attributes by wrapping "getting" (use of the ".") and "setting"
operations (use of the "=") within thread safe locks.  In addition to this, the
non-atomic "+=", "-=" ... "//=" statements using thread-safe attributes were
also wrapped within locks.  For situations that are more complex, the
thread-safety features provided by the ``ThreadSafeAttributes`` class can be
used to explicitly get the thread lock.

I will introduce these ideas gradually through a set of examples.  Let's
begin by looking at four interacting threads (possible race conditions are
highlighted):

.. code-block:: python
  :emphasize-lines: 18, 19, 31, 32
  :linenos:
  
  import time
  from threading import Thread
  from threading import Event as ThreadEvent

  from miros import ThreadSafeAttributes

  class GetLock1(ThreadSafeAttributes):
    _attributes = ['thread_safe_attr_1']

    def __init__(self, evt):
      '''running in main thread'''
      self.evt = evt
      self.thread_safe_attr_1 = 0

    def thread_method_1(self):
      '''running in th1 thread'''
      while(self.evt.is_set()):
        self.thread_safe_attr_1 += 1
        print("th1: ", self.thread_safe_attr_1)
        time.sleep(0.020)

  class GetLock2():
    def __init__(self, evt, gl1):
      '''running in main thread'''
      self.evt = evt
      self.gl1 = gl1

    def thread_method_2(self):
      '''running in th1 thread'''
      while(self.evt.is_set()):
        self.gl1.thread_safe_attr_1 -= 1
        print("th2: ", self.gl1.thread_safe_attr_1)
        time.sleep(0.020)

  class ThreadKiller():
    def __init__(self, evt, count_down):
      '''running in main thread'''
      self.evt = evt
      self.kill_time = count_down

    def thread_stopper(self):
      '''running in killer thread'''
      time.sleep(self.kill_time)
      self.evt.clear()

  # main thread:
  evt = ThreadEvent()
  evt.set()

  gl1 = GetLock1(evt)
  gl2 = GetLock2(evt, gl1=gl1)
  killer = ThreadKiller(evt, count_down=0.1)

  threads = []
  threads.append(Thread(target=gl1.thread_method_1, name='th1', args=()))
  threads.append(Thread(target=gl2.thread_method_2, name='th2', args=()))

  for thread in threads:
    thread.start()

  thread_stopper = Thread(target=killer.thread_stopper, name='killer', args=())
  thread_stopper.start()
  thread_stopper.join()

The ``GetLock1`` class inherits from the ``ThreadSafeAttributes`` class, which
uses a metaclass to give it access to the following syntax (seen on line 8 of
the above example):

.. code-block:: python
  
  _attributes = ['thread_safe_attr_1']

The ``ThreadSafeAttributes`` class tries to protect you.  When we write the
``_attributes = ['thread_safe_attr_1']`` syntax ``ThreadSafeAttributes`` creates
a set of hidden attributes, which are wrapped inside of a `descriptor protocol
<https://docs.python.org/3.6/howto/descriptor.html>`_ (think @property).  One of
the hidden attributes, `_lock` is a `threading.RLock
<https://docs.python.org/3.5/library/threading.html#rlock-objects>`_.  It is
used to lock and unlock itself around accesses to the other hidden attribute
`_value`.  Essentially this means that this code:

.. code-block:: python
  
  gl1.thread_safe_attr_1
  gl1.thread_safe_attr_1 = 1

... would turn into something like this before it is run:

.. code-block:: python
  
  with gl1._lock:
   gl1.thread_safe_attr_1

  with gl1._lock:
   gl1.thread_safe_attr_1 = 1

This is a typical meta-programming feature a lot of libraries provide.  But
things get a bit weird when we look at the non-atomic ``+=`` in the following
code example:

.. code-block:: python
  
  gl1.thread_safe_attr_1 += 1

When using the ``ThreadSafeAttributes`` class the above code turns into something like this:

.. code-block:: python
  
  with gl1._lock:
    temp = gl1.thread_safe_attr_1
    temp = temp + 1
    gl1.thread_safe_attr_1 = temp 

So the ``ThreadSafeAttributes`` class protects calls to the
seemingly-innocuous-looking, yet dangerous, "+=", "-=", ... "//=" family of
Python calls.  They are dangerous because they are not-atomic and can cause race
conditions if they are applied to attributes shared across threads.

So our example, written without the ``ThreadSafeAttributes`` class, but with the
same protections would look like this (shared attributes protections
highlighted):

.. code-block:: python
  :emphasize-lines: 11, 18-21, 33-36
  :linenos:
  
  place code here
  import time
  from threading import RLock
  from threading import Thread
  from threading import Event as ThreadEvent

  class GetLock1():

    def __init__(self, evt):
      '''running within main thread'''
      self._rlock = RLock()
      self.evt = evt
      self.thread_safe_attr_1 = 0

    def thread_method_1(self):
      '''running within th1 thread'''
      while(self.evt.is_set()):
        with self._rlock:
          self.thread_safe_attr_1 += 1
        with self._rlock:
          print("th1: ", self.thread_safe_attr_1)
        time.sleep(0.020)

  class GetLock2():
    def __init__(self, evt, gl1):
      '''running within main thread'''
      self.evt = evt
      self.gl1 = gl1

    def thread_method_2(self):
      '''running within th2 thread'''
      while(self.evt.is_set()):
        with self.gl1._rlock:
          self.gl1.thread_safe_attr_1 -= 1
        with self.gl1._rlock:
          print("th2: ", self.gl1.thread_safe_attr_1)
        time.sleep(0.020)

  class ThreadKiller():
    def __init__(self, evt, count_down):
      '''running within main thread'''
      self.evt = evt
      self.kill_time = count_down

    def thread_stopper(self):
      '''running within killer thread'''
      time.sleep(self.kill_time)
      self.evt.clear()

  evt = ThreadEvent()
  evt.set()

  gl1 = GetLock1(evt)
  gl2 = GetLock2(evt, gl1=gl1)
  killer = ThreadKiller(evt, count_down=0.1)

  threads = []
  threads.append(Thread(target=gl1.thread_method_1, name='th1', args=()))
  threads.append(Thread(target=gl2.thread_method_2, name='th2', args=()))

  for thread in threads:
    thread.start()

  thread_stopper = Thread(target=killer.thread_stopper, name='stopper', args=())
  thread_stopper.start()
  thread_stopper.join()

We haven't looked at any code results yet. Let's run it and see what it does:

.. code-block:: bash
  
   $python thread_safe_attributes_2.py
   th1:  1
   th2:  0
   th1:  1
   th2:  0
   th1:  1
   th2:  0
   th2:  -1
   th1:  0
   th1:  1
   th2:  0

We see that the number oscillates about 0.  If we remove the time delays at the
bottom of the thread functions you will see wild oscillation in this number,
since one thread by change will get many more opportunities to run.  So you can
see that it might be hard to reproduce exactly two identical traces of the
program output.

Ok, now for something scary, let's look at our code without thread locks (the race conditions are highlighted):

.. code-block:: python
  :emphasize-lines: 15, 16, 28, 29
  :linenos:

  import time
  from threading import Thread
  from threading import Event as ThreadEvent

  class GetLock1():

    def __init__(self, evt):
      '''running within main thread'''
      self.evt = evt
      self.thread_race_attr_1 = 0

    def thread_method_1(self):
      '''running within th1 thread'''
      while(self.evt.is_set()):
        self.thread_race_attr_1 += 1
        print("th1: ", self.thread_race_attr_1)
        time.sleep(0.020)

  class GetLock2():
    def __init__(self, evt, gl1):
      '''running within main thread'''
      self.evt = evt
      self.gl1 = gl1

    def thread_method_2(self):
      '''running within th2 thread'''
      while(self.evt.is_set()):
        self.gl1.thread_race_attr_1 -= 1
        print("th2: ", self.gl1.thread_race_attr_1)
        time.sleep(0.020)

  class ThreadKiller():
    def __init__(self, evt, count_down):
      '''running within main thread'''
      self.evt = evt
      self.kill_time = count_down

    def thread_stopper(self):
      '''running within killer thread'''
      time.sleep(self.kill_time)
      self.evt.clear()

  evt = ThreadEvent()
  evt.set()

  gl1 = GetLock1(evt)
  gl2 = GetLock2(evt, gl1=gl1)
  killer = ThreadKiller(evt, count_down=0.1)

  threads = []
  threads.append(Thread(target=gl1.thread_method_1, name='th1', args=()))
  threads.append(Thread(target=gl2.thread_method_2, name='th2', args=()))

  for thread in threads:
    thread.start()

  thread_stopper = Thread(target=killer.thread_stopper, name='stopper', args=())
  thread_stopper.start()
  thread_stopper.join()

I changed the ``thread_safe_attr_1`` name to ``thread_race_attr_1`` to make a
point.  The highlighted code shows where race conditions can occur.  If we run
the code we see:

.. code-block:: bash
 
  python thread_safe_attributes_3_unsafe.py
  th1:  1
  th2:  0
  th1:  1
  th2:  0
  th2:  -1
  th1:  0
  th1:  1
  th2:  0
  th1:  1
  th2:  0

Which looks almost exactly the same as the last run.  Race conditions are very
hard to find.

Let's move back to our original-original example, suppose we absolutely needed
to run calculations on the ``thread_safe_attr_1`` in more than one thread (which
I can't see the need for).  I'll change the name of ``thread_safe_attr_1`` to
``a``. The ``ThreadSafeAttributes`` class can not implicitly protect you in such
situations, but what it can do is give you the lock and you can use it to
protect your own code (highlighting how to get the lock):

.. code-block:: python
  :emphasize-lines: 18, 34
  :linenos:
  
  import math
  import time
  from threading import Thread
  from threading import Event as ThreadEvent
  
  from miros import ThreadSafeAttributes
  
  class GetLock1(ThreadSafeAttributes):
    _attributes = ['a']
  
    def __init__(self, evt):
      '''running within main thread'''
      self.evt = evt
      self.a = 0
  
    def thread_method_1(self):
      '''running within th1 thread'''
      _, _lock = self.a
      while(self.evt.is_set()):
        with _lock:
          self.a = 0.35
          b = self.a * math.cos(0.45) + 3 * self.a ** 1.2
          print("th1: ", b)
        time.sleep(0.020)
  
  class GetLock2():
    def __init__(self, evt, gl1):
      '''running within main thread'''
      self.evt = evt
      self.gl1 = gl1
  
    def thread_method_2(self):
      '''running within th2 thread'''
      _, _lock = self.gl1.a
      while(self.evt.is_set()):
        with _lock:
          self.gl1.a = 0.30
          b = self.gl1.a * math.cos(0.45) + 3 * self.gl1.a ** 1.2
          print("th2: ", b)
        time.sleep(0.020)
  
  class ThreadKiller():
    def __init__(self, evt, count_down):
      '''running within main thread'''
      self.evt = evt
      self.kill_time = count_down
  
    def thread_stopper(self):
      '''running within killer thread'''
      time.sleep(self.kill_time)
      self.evt.clear()
  
  # main thread:
  evt = ThreadEvent()
  evt.set()
  
  gl1 = GetLock1(evt)
  gl2 = GetLock2(evt, gl1=gl1)
  killer = ThreadKiller(evt, count_down=0.1)
  
  threads = []
  threads.append(Thread(target=gl1.thread_method_1, name='th1', args=()))
  threads.append(Thread(target=gl2.thread_method_2, name='th2', args=()))
  
  for thread in threads:
    thread.start()
  
  thread_stopper = Thread(target=killer.thread_stopper, name='stopper', args=())
  thread_stopper.start()
  thread_stopper.join()

The lock can be obtained by calling ``_, _lock = <thread_safe_attribute>``.

This is a little nasty piece of metaprogramming that could baffle a beginner or
anyone who looks at the thread safe attribute.  Most of the time your thread
safe attribute acts as an attribute, but other times it acts as an iterable,
what gives?  It only acts as an interable when proceeded by ``_, _lock``.  If
you use this technique in one of your threads, you must use it in all of your
threads.  Once again I recommend against performing calculations directly on
your shared attributes.  Instead, copy their variable into a temp, perform a
calculation then assign the results into them.

.. note::

  The ``ThreadSafeAttributes`` feature actually reads the last line of code you
  have written, the behaves differently depending on what you have written.  It
  is because of this feature it can release it's lock in what looks like a
  syntactically inconsistent way.

