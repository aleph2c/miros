.. _towardsthefactoryexample-towards-a-factory:

Using and Unwinding a Factory
=============================

.. image:: _static/factory1.svg
    :align: center

.. _towardsthefactoryexample-example-summary:

Example Summary
---------------
1. :ref:`Write a standard flat version of a statechart<towardsthefactoryexample-standard-approach>`
2. :ref:`Re-write the state methods so that you can register callbacks with specific
   events.<towardsthefactoryexample-registering-callbacks-to-specific-events>`
3. :ref:`Re-write the state methods so that you can register a parent with
   them<towardsthefactoryexample-registering-a-parent-to-a-state-method>`
4. :ref:`Remove the need to explicitly write a number of state methods, instead, we
   can get them from a template
   function<towardsthefactoryexample-building-a-method-to-build-state-methods>`
5. :ref:`Use the miros factory
   methods<towardsthefactoryexample-using-the-miros-factory-method>`
6. :ref:`Use miros to convert it's factory method into a flat version of a state
   function for
   debugging.<towardsthefactoryexample-unwinding-a-factory-state-method>`

.. _towardsthefactoryexample-why-you-would-want-a-factory:

Why a Factory?
--------------

The event processor used to create the dynamics of your statechart expects all
of your state methods to have a specific shape.  Their method signatures have
to look a certain way and their if-else structures have to be framed-in just
right, otherwise the event processor might get lost while it's searching for
the correct behavior.

The event processor provides the illusion that you are using a completely
different type of programming language, but it's still all Python.  Your state
methods are just being called over and over again with different arguments.

Miro Samek describes this as "an inversion of control".  By using his event
processor algorithm, you are packing the management of the topological search
complexity into the bottom of your software system.

The beautiful thing about the framework is that a state method only has to
describe which other state method is it's parent.  Then when the event
processor is called, it will look at the current state and
recurse over your state methods determining how and when each of your state
methods should be called in accordance to the Harel Formalism.  You don't
have to worry about how this is done, you just have to remember how the maps
behave, then translate your map into state methods.

The cost of this is that you have to express your application code within
:ref:`specifically
structured ways<recipes-what-a-state-does-and-how-to-structure-it>`.  Wouldn't it be
nice if the library wrote the methods for you too?  Well, it can do that using
the factory pattern, but let's consider the downside of structuring your
application like this.

If you use this library to write your state methods for you, you are placing
yet another layer of abstraction between you and your application code.  A bug
might be even harder to find than it was before.  The nice thing about the
state methods is that they are easy to understand, they are flat,
and you can literally see the code and break within it for debugging.  The
cognitive load experienced while trouble shooting a flat state method is much
less than it would be for something that is auto-generated.

In this example I will walk you through how we can move from a simple state
method towards one that is written for you automatically.  I will also describe
fusion state methods which use both techniques and thereby allow you to
register event callbacks while your code is executing and why you might want
to do this.

Then I will also describe how to create a state method using a factory, then how to
ask the framework to print out what that code would look like if it were
hard-coded into your project.  I will then demonstrate a technique of unwinding
a complicated design, into such flat methods, so that you can 'see' what is
going on.

.. _towardsthefactoryexample-standard-approach:

Standard Approach
-----------------

.. image:: _static/factory1.svg
    :align: center

To create the above diagram we would define three state methods, ``c``, ``c1``
and ``c2`` and an active object.

.. code-block:: python
  :emphasize-lines: 42
  
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def c(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(c1)
    elif(e.signal == signals.BB):
      status = chart.trans(c)
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def c1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status


  @spy_on
  def c2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status


  ao = ActiveObject()
  ao.start_at(c2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01) # give your active object a moment to respond
  pp(ao.spy())

Remember to give your chart a moment to react to an event before you let your
program complete.  The output of this could would look like this in the
terminal:

  .. code-block:: python
    :emphasize-lines: 7,14

    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:c2',
     'SEARCH_FOR_SUPER_SIGNAL:c',
     'ENTRY_SIGNAL:c',
     'ENTRY_SIGNAL:c2',
     'INIT_SIGNAL:c2',
     '<- Queued:(0) Deferred:(0)',
     'A:c2',
     'SEARCH_FOR_SUPER_SIGNAL:c1',
     'SEARCH_FOR_SUPER_SIGNAL:c2',
     'EXIT_SIGNAL:c2',
     'ENTRY_SIGNAL:c1',
     'INIT_SIGNAL:c1',
     '<- Queued:(0) Deferred:(0)']

We see that the spy log shows that we had two run to completion events with no
surprises.  Notice that the event processor tried to call the state functions
with the ``ENTRY_SIGNAL``, ``INIT_SIGNAL`` and ``EXIT_SIGNAL`` as it should
have, even though our state methods did not handle these events.  The handlers
for these events were left out of the state method examples to keep the code
compact.

.. _towardsthefactoryexample-registering-callbacks-to-specific-events:

Registering Callbacks to Specific Events
----------------------------------------
To build our state method code generation we need to create something that is 
common to all state methods.  The state method does two different things, it
responds to events and it returns parent information.  

To break this down even more, we can say that it does four things.  It asks two
questions and answers two questions.  It asks "How should I respond to the
events that I care about?" and "Who is my parent?".

Then it answers these questions with information specific to that state method.
To make something common across all state methods we can ask the questions but
we can't answer them.  The answers will have to be injected into the state
methods after they have been created.

To be more specific a general state method could look something like this:

.. code-block:: python
  :emphasize-lines: 4-6, 8-11

  @spy_on
  def general_state_method(chart, e):

    # How should I respond to the events that I care about?
    with chart.signal_callback(e, general_state_method) as fn:
      status = fn(chart, e)

    # Who is my parent?
    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

We see that the chart argument provides different context managers,
``signal_callback`` and ``parent_callback``.  It is within these context
managers that the answers are made.

To inject the information into the chart
object so that these context managers have something to answer with we can use the
``register_signal_callback`` and the ``register_parent`` of the active object.

Things should become a bit clearer with an example, reconsider our previous design:

.. image:: _static/factory3.svg
    :align: center


.. code-block:: python
  :emphasize-lines: 4, 16, 28
  
  @spy_on
  def tc(chart, e):

    with chart.signal_callback(e, tc) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc1(chart, e):

    with chart.signal_callback(e, tc1) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc2(chart, e):

    with chart.signal_callback(e, tc2) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

To distinguish these state methods from the previous ones we pre-pend their names
with `t` which stands for template.

These state methods almost look identical, the highlighted lines spell out how
they are different;  the ``signal_callback`` context manager is using the state
method's name to get its information.  Other than that it hardly seems worth
writing out the code three times.

Now we have to give it the information required to perform the actions we want,
first we define some callback methods, then we describe how we want our state
methods to call them.

.. code-block:: python
  :emphasize-lines: 1-11, 13, 15-31

  def trans_to_tc(chart, e):
    return chart.trans(tc)

  def trans_to_tc1(chart, e):
    return chart.trans(tc1)

  def trans_to_tc2(chart, e):
    return chart.trans(tc2)

  def do_nothing(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(tc, signals.BB, trans_to_tc)
  ao.register_signal_callback(tc, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc, signals.INIT_SIGNAL,  trans_to_tc1)
  ao.register_parent(tc, ao.top)

  ao.register_signal_callback(tc1, signals.A, trans_to_tc2)
  ao.register_signal_callback(tc1, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc1, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc1, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc1, tc)

  ao.register_signal_callback(tc2, signals.A, trans_to_tc1)
  ao.register_signal_callback(tc2, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc2, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc2, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc2, tc)

In the first highlighted block we create four different callback methods.  They
have the same method signature as a state method and they work exactly as they
would if they were defined within a state method.

The second block is just an instantiation of an active object, it has the event
processor and it also provides a means to register callback methods for events
and to register a parent state.

The next block shows how are three state methods are given their information.
For instance, the event ``BB`` will cause state ``tc`` to transition to itself.

If we run this code like we did in our previous example we would expect to it
behave the same:

.. code-block:: python

  ao.start_at(tc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)  # give your active object a moment to respond
  pp(ao.spy())

If we ran this code, we would see:

  .. code-block:: python
    :emphasize-lines: 7,14

    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:tc2',
     'SEARCH_FOR_SUPER_SIGNAL:tc',
     'ENTRY_SIGNAL:tc',
     'ENTRY_SIGNAL:tc2',
     'INIT_SIGNAL:tc2',
     '<- Queued:(0) Deferred:(0)',
     'A:tc2',
     'SEARCH_FOR_SUPER_SIGNAL:tc1',
     'SEARCH_FOR_SUPER_SIGNAL:tc2',
     'EXIT_SIGNAL:tc2',
     'ENTRY_SIGNAL:tc1',
     'INIT_SIGNAL:tc1',
     '<- Queued:(0) Deferred:(0)']

.. _towardsthefactoryexample-registering-a-parent-to-a-state-method:

Using the Miros Factory Method
------------------------------
We pretty much wrote the same method three times in a row in our last example.
Wouldn't it be nice if something could write the thing for us?  

This is exactly what the ``miros.hsm.state_method_template`` does.

It writes the template code within another function, then copies it so that
this function result is unique in memory, then it renames it and then decorates
it with some instrumentation.

.. code-block:: python

  from miros.hsm import spy_on

  def state_method_template(name):

    def base_state_method(chart, e):

      with chart.signal_callback(e, name) as fn:
        status = fn(chart, e)

      if(status == return_status.UNHANDLED):
        with chart.parent_callback(name) as parent:
          status, chart.temp.fun = return_status.SUPER, parent

      return status

    resulting_function = copy(base_state_method)
    resulting_function.__name__ = name
    resulting_function = spy_on(resulting_function)
    return resulting_function

With this method we can automatically write our state methods then register
event callbacks and parent states.

Let's re-create our example, this time using this ``state_method_template``
method:

.. image:: _static/factory4.svg
    :align: center

.. code-block:: python
 
  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # create the states
  fc  = state_method_template('fc')
  fc1 = state_method_template('fc1')
  fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  ao.register_parent(fc, ao.top)

  # write the design information into the fc1 state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  ao.register_parent(fc1, fc)

  # write the design information into the fc2 state
  ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  ao.register_parent(fc2, fc)

  # start up the active object what what it does
  ao.start_at(fc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())

This is a much more compact version of our map.  I removed the registration of
signals that weren't being used by the design, but more importantly I used the
``state_method_template`` to create the state methods that could have
information added to them with the active object registration methods.

The output from this program is:

.. code-block:: python
  :emphasize-lines: 7,14

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'ENTRY_SIGNAL:fc2',
   'INIT_SIGNAL:fc2',
   '<- Queued:(0) Deferred:(0)',
   'A:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'EXIT_SIGNAL:fc2',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)']

We see the expected behavior.

.. _towardsthefactoryexample-unwinding-a-factory-state-method:

Unwinding a Factory State Method
--------------------------------




