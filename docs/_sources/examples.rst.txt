Examples
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. image:: _static/simple_example_1.svg

ActiveObject Example
--------------------
Suppose you have designed the above behavioral diagram and you would like to
implement it using this library.  The easiest way to do this is to use the
`ActiveObject` class provided within the `active object` module.

To begin our example we import some items from the miros library:

.. code-block:: python

  from miros.event import Signal, Event, return_status, signals
  from miros.activeobject import ActiveObject, spy_on

Then we define the :abbr:`signals(the arrow labels in the diagram)` which our
:abbr:`events(the arrows)` will use:

.. code-block:: python

  signals.append("WaitComplete")
  signals.append("ResetChart")

The signals object is derived from a :abbr:`singleton class (all objects
instantiated from this class refer to the same object)`, so once our signals are
defined they can be accessed by any other module in our python project.

Now we write our state methods.  The state methods are not really states, but
just simple methods that are called by the HSM event processor when it is trying
to figure out what to do in response to an event.

Let start by writing the outer state method.  This method can be thought of as
representing the rectangle labeled `outer` of the above diagram.

.. code-block:: python

  @spy_on
  def outer(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      # outer state custom entry code would go here
      status = return_status.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      # outer state custom exit code would go here
      status = return_status.HANDLED

    elif(e.signal == signals.WaitComplete):
      # we could write code which runs on the WaitComplete signal here
      status = chart.trans(middle)

    elif(e.signal == signals.ResetChart):
      # we could write code which runs on the ResetChart signal here
      status = chart.trans(outer)
    else:
      # this signal wasn't managed, pass a reference to the 
      # method that is outside of us
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

We see that our method is basically a big if-else structure, which reads the
signal attribute of the `e` (Event) variable and decides what to do about it. We
see that this state reacts to the `WaitComplete` by calling the ``trans`` method
with the `middle` state as an argument.  This will represent the arrow labeled
`WaitComplete` on the above diagram connecting the `outer` state with the
`middle` state.

Likewise we see that this method calls the ``trans`` method with the `outer`
method as an argument when it receives an event with the signal named
`ResetChart`.  This represents the arrow which loops from-and-to the `outer`
rectangle in the above diagram.

We see that the 

`ActiveObjects` are very dynamic and can be hard to debug if we can't see what
they are doing while we build and test them.  So, we instrument the `outer`
method with a ``@spy_on`` decorator.  This adds logging to the method, more will
be said about this as the example continues.

Now lets write the middle state:

.. code-block:: python

  @spy_on
  def middle(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(inner)
      return return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, outer
    return status

The inner state:

.. code-block:: python

  @spy_on
  def inner(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, middle
    return status

Now that our states are defined, we create an `active object` and tell it where
to start in our diagram:

.. code-block:: python

  ao = ActiveObject()
  ao.start_at(outer)

The call to the ``start_at`` `active object` method will create two different :abbr:`daemonic
threads(threads that stop when the main program stops running)`, one is for
managing the `active object` and the other is for managing the `active fabric`.
Then the ``start_at`` call tries to climb into the chart.

We can see what happened by reading the `spy` instrumentation results:

.. code-block:: python

    print(ao.spy_full()) #=>
      # ['START', 
      #  'SEARCH_FOR_SUPER_SIGNAL:outer', 
      #  'SEARCH_FOR_SUPER_SIGNAL:top', 
      #  'ENTRY_SIGNAL:top', 
      #  'ENTRY_SIGNAL:outer', 
      #  'INIT_SIGNAL:outer', 
      #  '<- Queued:(0) Deferred:(0)']

This is very detailed but we can view a summary of what happened using the
`trace` instrumentation instead of the `spy` instrumentation:

.. code-block:: python

    print(ao.trace()) #=>
      # 09:53:38.941445 [01352] None: top->outer

The `trace` is different from our `spy` in that it does not show all of the activity
resulting from our event processor, but instead just shows information about
state transitions and the signal which caused the transition to occur.  In this
case there was :abbr:`no signal(the transition was caused by a start_at)` so the
`trace` displays ``None`` for the signal name.  The `trace` does give us some new
information though: it outputs a timestamp of when the transition took place.

Now that our state is in ``outer`` state, we can send an event at it.  After
this reaction we can see what happened by viewing our instrumentation.

.. code-block:: python

  # clear our spy and trace logs
  ao.clear_trace()
  ao.clear_spy()

  # Send an event with signal 'W' so we can watch the reaction
  event_w = Event(signal=signals.W)
  ao.post_fifo(event_w) #=> "hello world"

  # Look at the reaction of our chart in great detail
  print(ao.spy_full()) #=>
    # ['W:outer',
    #  'SEARCH_FOR_SUPER_SIGNAL:middle',
    #  'ENTRY_SIGNAL:middle',
    #  'INIT_SIGNAL:middle',
    #  'SEARCH_FOR_SUPER_SIGNAL:inner',
    #  'ENTRY_SIGNAL:inner',
    #  'INIT_SIGNAL:inner',
    #  '<- Queued:(0) Deferred:(0)']

  # Look at the reaction of our chart with less detail
  print(ao.trace()) #=>
    # 10:34:47.344218 [01352] W: outer->inner

From the trace output we see that we were in the `outer` state and an event with
the `W` signal caused us to transition into the `inner` state.  This is true,
but it doesn't really describe what happened.

If we want the full story we need to look at the results of our spy.  We see
that the system was in the `outer` state and it reacted to an event with the
signal `W`.  It saw that it needed to transition into the `middle` state, so it
issued an event with the `entry` signal to the middle state.  If you had code
linked to this event in the `middle` state method it would have been run.  Once
it is in the `middle` state it sees that there is an `init` handler, so it fires
another event with the signal `init` which causes a transition into the `inner`
state.  Since the `inner` state required entry, the event processor created an
event with the `entry` signal and sent it to the `inner` state.  Any entry code
within the `inner` state event handler would have been run at this point and
time.  Finally, the event processor issued an other `init` event to the inner
state.  The inner state does not handle this event, so it is ignored and our
system settles into the `inner` state.  It will remain here until it has to
react to events provided by the user.

As mentioned previously, their are two different threads running in the
background since we created our `active object`.  They are both pending on
queues.  The number of items in the active object queue can be seen in our `spy`
instrumentation.  We see that at the end of this reaction to the event with the
`W` signal, there was nothing in the queue so the `active object` thread has
nothing to do.

Lets stop the thread, and place a number of events into the queue managed by the
active object.


Hsm Example
-----------

HsmWithQueues Example
---------------------

InstrumentedHsmEventProcessor Example
-------------------------------------

HsmEventProcessor Example
-------------------------
.. code-block:: python

    def reflect(hsm=None,e=None):
      '''
      This will return the callers function name as a string:
      Example:

        def example_function():
          return reflect()

        print(example_function) #=> "example_function"

      '''
      fnt  = traceback.extract_stack(None,2)
      fnt1 = fnt[0]
      fnt2 = fnt1[2]
      return fnt2

.. To link to this figure: :ref:`deferred-event-state-pattern`
.. _deferred-event-state-pattern:


.. figure:: _static/DeferredEventStatePattern.gif
   :alt: the deferred event state pattern


