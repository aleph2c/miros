.. included from recipes

Anytime you start a statechart, your program is multi-threaded.  Sometimes, you
will want to access an attribute of your statechart from another thread,
like the main part of your program.  When you do this, you are trying to
access memory that could be changed in one thread while it is being read in by
another thread.  

To see why this is an issue imagine using a calculator to solve a simple math
problem: calculate the value of ``b``, starting with ``a == 0.35``, given the
following equation:

.. code-block:: python
  
  b = a*cos(0.45) + 3*a^1.2

Seems simple enough.  You pick a straight-forward strategy: 

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
operation, where some shared value happen to also be changed by the other
thread.  When the Python task manager switches back to your thread, the result
of your calculation will be wrong.  These kinds of bugs are more probabilistic
than deterministic, because Python's access to the system clock is jittery: It's
timing will never be the same every two runs of the program, so it will be hard
for you to reproduce your issue.

The miros library accepts that people will want to access a statechart's internal
attributes from the outside.  Significant efforts have been made to make this
kind of activity easy for you to do in a "thread-safe" manner.  The
``ThreadSafeAttributes`` class was constructed to make this easy for you.

