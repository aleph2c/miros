
  *Simple things should be simple, complex things should be possible.* 
  
  -- Alan Kay

.. _recipes:

.. _recipes-recipes:

Recipes
=======

This section contains a set of examples that can be referenced as you are
building up your own programs.

.. contents:: 
   :backlinks: entry

.. _recipes-demo:

Demonstration of Capabilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this section I'll show you how you can use the miros library by layering more
and more of its features into a simple program.

.. contents::
  :local:

.. _recipes-state-abstraction:

State Abstraction in Miros
--------------------------

In miros a state is a behavioral specification for an event processor.  A state
is a function that does the following:

* It accepts two arguments:
   1. an object of type/subclass of ``miros.ActiveObject``, which has an event processor.
   2. an event of type/subclass of  ``miros.Event``
* It describes how it is situated in a hierarchy and how it is connected to
  other states, by changing the ``temp.fun`` attribute of it's first argument.
* It returns an ``miros.return_status`` attribute, which tells the event processor 
  how the state function reacted to the event.

The user starts and then posts events to the ActiveObject, and its event
processor reacts to these events by calling your state functions over and over
again with a set of internal and external events.  The internal events are used
to search the hierarchical state machine, to run it's entry and exit conditions
and to initialize the state once it has been settled into.  The external events
are user defined (more will be said about this shortly).

The state functions do two different things, they describe how they are
topologically related to other states and they contain code which will run as
the event processor calls them over and over again.  What emerges from this
interplay is a Hierarchical State Machine (HSM) behavior which follows the Harel
Formalism (picture-to-behavior rules).

Now that we understand a bit of theory and how the miros abstraction works,
let's look at some examples.

.. _recipes-minimal-viable-states:

Minimal Viable States
---------------------

In a statechart diagram, a state is represented by a named rounded rectangle.
In a hierarchical state machine a state can exist within a state.  Here we see
an inner_state placed within an outer_state:

.. image:: _static/state_recipe_1.svg
    :target: _static/state_recipe_1.pdf
    :align: center

Every state function, must at least describe where it is situated in the HSM
hierarchy. Here is the miros code for the above diagram:

.. code-block:: python
  :emphasize-lines: 2, 7
  
   def outer_state(chart, e):
     chart.temp.fun = chart.top  # describe how we fit in the hierarchy
     status = return_status.SUPER  # describe how we reacted to the event
     return status

   def inner_state(chart, e):
     chart.temp.fun = outer_state  # describe how we fit in the hierarchy
     status = return_status.SUPER  # describe how we reacted to the event
     return status

Above we see two minimal-viable state functions, which react to every possible
event the same way.  They set the ``temp.fun`` to their super state (it's outer
state) and return a status telling the event processor that they did this.

Now that we know how to make a minimal-viable state function, and how it relates to a
hierarchical state machine, let's talk about how to connect it to a thread, how
to start it and how to give it some behavior.

.. _recipes-attachment-points-and-a-working-state-machine:

Attachment Points and a Working State Machine
---------------------------------------------

A state function is lazy about how it describes its graphical relationship to
the other states in its hierarchical state machine.  To ask it a question about
how it sits in the hierarchy, or how it is connected to another part of the
state machine, the event processor needs to send it an event.  The state
function will respond by setting it's return status to something and it will
change the ``temp.fun`` attribute of its first argument.

But before it can do either of these things, an event processor needs to be
connected to a state function.  This is done with the Active object's ``start_at``
method.  On the diagram, this is called the attachment point.  It is where the
ball and the socket meet.

I'll redraw our simple state machine with some more details:

.. image:: _static/state_recipe_2.svg
    :target: _static/state_recipe_2.pdf
    :align: center

The above diagram is saying that there is an attachment point between an
``ActiveObject`` and the ``outer_state``.  To create and run a state machine, we
will instantiate the ``ActiveObject``, then ``start_at`` the ``outer_state``.
When we call this ``start_at`` method, the miros library will create a thread
for this statechart and run it until the main program is stopped.

We have also added a new graphing element called the init pseudostate, the black
dot.  The black dot has an arrow pointing to the ``inner_state``.  This means,
after I have entered into the ``outer_state`` and I have settled, transition
into the ``inner_state``.

To make our new design work, we will have to change our ``outer_state``
function.  It will need to provide graphical information about an init event.
It will set the ``temp.fun`` to ``inner_state`` and it will have to tell the
event processor it needs to perform a transition into another state.  This is
all done within the ``trans`` method:
  
.. code-block:: python
  :emphasize-lines: 8, 10-13, 30

   import time

   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   def outer_state(chart, e):
     status = return_status.UNHANDLED
     # the event processor is asking us about events called INIT_SIGNAL
     if(e.signal == signals.INIT_SIGNAL):
       # we are transitioning to inner_state
       # we let the trans method, set temp.fun and our return status
       status = chart.trans(inner_state)
     # we do this for any other event
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   def inner_state(chart, e):
     # we do this for all events
     chart.temp.fun = outer_state
     status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject('ao')

     # Create a thread and start our state machine
     ao.start_at(outer_state)

     # Run our main program so that the state machine's thread
     # can do some stuff.
     # The state machine's thread will be stopped when our main thread stops
     time.sleep(0.01)

I have highlighted the code that would cause the init transition and the
attachment point (``start_at``).  If we run this code, the statechart will start
in the ``outer_state``, then settle, then transition into the ``inner_state``.
But you will have to trust me about this, since the code doesn't provide any
user feedback.

Now that we know how to build and start a small statechart.  Let's look at
how to instrument it so it provides feedback about its behavior.

.. _recipes-feedback-about-behavior-through-instrumentation:

Feedback about Behavior through Instrumentation
-----------------------------------------------

We will include the ``spy_on`` decorator from the miros library, then we will
use it to decorate our state functions:
  
.. code-block:: python
  :emphasize-lines: 8, 22, 31

   import time

   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on  # enables the live_trace/live_spy capabilities
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     # the event processor is asking us about events called INIT_SIGNAL
     if(e.signal == signals.INIT_SIGNAL):
       # we are transitioning to inner_state
       # we let the trans method, set temp.fun and our return status
       status = chart.trans(inner_state)
     # we do this for any other event
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on  # enables the live_trace/live_spy capabilities
   def inner_state(chart, e):
     # we do this for all events
     chart.temp.fun = outer_state
     status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject('ao')
     ao.live_trace = True  # so we can see what is happening
     # Create a thread and start our state machine
     ao.start_at(outer_state)
     # Run our main program so that the state machine's thread
     # can do some stuff.
     # The state machine's thread will be stopped when our main thread stops
     time.sleep(0.01)

The ``@spy_on`` decorators enables the live_trace and live_spy instrumentation
capabilities of the statechart library.

So if I run the above code I will see something like this in my terminal:

.. code-block:: python
  
  [2019-07-22 12:22:34.050461] [ao] e->start_at() top->inner_state

Now that we know how to instrument a statechart, let's look at how to add some
state entry conditions.

.. _recipes-entry-conditions-and-handled-events:

Entry Conditions and Handled Events
-----------------------------------

We will add some entry code to both the outer_state and inner_state functions:

.. image:: _static/state_recipe_3.svg
    :target: _static/state_recipe_3.pdf
    :align: center

The above diagram is saying, when we enter the ``outer_state``, run a print
statement.  Then settle, which will cause an init transition into the
``inner_state``.  When we enter the ``inner_state`` run a different print
statement.  If a state function receives an entry event, we don't want to change
our active state and we don't want to describe our super state.  We just want to
run some code, then tell the event processor that the event was handled so it
will stop trying to figure out what to do with it.

Here is the code:

.. code-block:: python
  :emphasize-lines: 14-16, 30-32
  
   # simple_state_3.py
   import time

   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     # the event process automatically sends
     # an event named ENTRY_SIGNAL when a state is entered
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from outer_state")
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       print("init")
       status = chart.trans(inner_state)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     # the event process automatically sends
     # an event named ENTRY_SIGNAL when a state is entered
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from inner_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject('ao')
     ao.live_trace = True
     ao.start_at(outer_state)
     time.sleep(0.01)

If we run the code we see something like this:

.. code-block:: bash
  
   hello from outer_state
   init
   hello from inner_state
   [2019-07-22 12:22:34.050461] [ao] e->start_at() top->inner_state

So far we have been talking about signals that are included within the
miros library: INIT_SIGNAL, ENTRY_SIGNAL.

Let's adjust our design to use another internal signal, EXIT_SIGNAL.

.. _recipes-exit-conditions:


Exit Conditions
---------------

.. image:: _static/state_recipe_4.svg
    :target: _static/state_recipe_4.pdf
    :align: center

Our new design describes some code that will run when we exit either state.  But
how would we ever exit?  There is nothing on our diagram that can cause an exit,
we can only climb into the inner_state, then sit their forever.

To add some more behavior, we will have to invent a signal.  

.. _recipes-inventing-your-own-signals:

Inventing your own Signals: External events
-------------------------------------------

Let's invent a signal and call it ``Reset``, because it will reset the chart, or
put it back into the state it was when we first started it at the
``outer_state``.  Any signal that is not an internal signal, like INIT_SIGNAL,
ENTRY_SIGNAL, EXIT_SIGNAL.. is called an external signal.  In this case our
external signal ``Reset`` will be invented the moment we write it into the code;
it is automatically declared.

So, how do we invent an event and give it a signal name and send it at our
chart?  Well, the chart runs in a thread and it has a set of queues that it
watches for events.  To send this chart information we just have to make an
event, assign it to a signal, then post it into one of these queues.  Here is
the code that will do this:

.. code-block:: python
  :emphasize-lines: 49
  
   # simple_state_5.py
   import time
   from collections import namedtuple

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from outer_state")
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       print("init")
       status = chart.trans(inner_state)
     elif(e.signal == signals.Reset):
       print("resetting the chart")
       status = chart.trans(outer_state)
     elif(e.signal == signals.EXIT_SIGNAL):
       print("exiting outer_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from inner_state")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       print("exiting inner_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject("ao")
     ao.live_trace = True
     ao.start_at(outer_state)
     ao.post_fifo(Event(signal=signals.Reset))
     # let the thread catch up before we exit main
     time.sleep(0.01)

If we run this code we see the following:

.. code-block:: text
  
   hello from outer_state
   init
   hello from inner_state
   [2019-07-22 12:44:29.470827] [ao] e->start_at() top->inner_state
   resetting the chart
   exiting inner_state
   exiting outer_state
   hello from outer_state
   init
   hello from inner_state
   [2019-07-22 12:44:29.471806] [ao] e->Reset() inner_state->inner_state


It behaves in a sensible way.  But there is something interesting going on.  The
state machine was in the ``inner_state`` when it got our ``Reset`` signal.  It
ran the print statement associated with this signal, while it was still in the
``inner_state`` before it climbed out of the ``outer_state`` and the
``inner_state``, only to climb back into where it was.

.. note::
  
   Another way to think about internal and external signals is that internal
   signals are sent from the event processor to the state functions without the
   user explicitly asking it to do so.  But, external signals are only sent to the
   chart when a user explicitely posts the event into the statechart.

So the event processor needed to follow some rules.  It needed to figure out how
and when to post each event to our two simple state functions.  It needed to
figure out, who was the super state of ``inner_state`` so it could call it's
state function with the ``Reset`` event to see what it should do.

The event processor does this work, and it keeps you from having to write code
to solve these types of topological problems.  You just need to write simple
state functions, which act as a behavioral specification and then connect this
to an ``ActiveObject``, start it, and then post events to it.

.. note::
  
   The code that is on the init arrow in our diagram and the code that is listed
   under entry and exit signals is run while the event processor is trying to
   figure out what to do next.  The event processor is not aware of this code,
   the code is run as a side-effect of its efforts to search the graph then act
   upon its results.

What would have happened had our ``Reset`` ``elif`` clause just returned
``return_status.HANDLED``?  There wouldn't have been a state transition.
When an event is caught this way it is called a hook.

.. _recipes-hooks:

Hooks
-----

Hook code can be run when you sent an event to the state or any of it's
substates which has the name of that hook.  You are using the search feature of
the event processor to do work for you, without asking it to change the state of
your statechart as it reacts to your hook event.  This is easier to understand
with a picture.

.. image:: _static/state_recipe_6.svg
    :target: _static/state_recipe_6.pdf
    :align: center

Here is the code, with the hook highlighted

.. code-block:: python
  :emphasize-lines: 20-22
  
   # simple_state_6.py
   import time
   from collections import namedtuple

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from outer_state")
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       print("init")
       status = chart.trans(inner_state)
     elif(e.signal == signals.Hook):
       print("run some code, but don't transition")
       status = return_status.HANDLED
     elif(e.signal == signals.Reset):
       print("resetting the chart")
       status = chart.trans(outer_state)
     elif(e.signal == signals.EXIT_SIGNAL):
       print("exiting outer_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       print("hello from inner_state")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       print("exiting inner_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject("ao")
     ao.live_trace = True
     ao.start_at(outer_state)
     ao.post_fifo(Event(signal=signals.Hook))
     ao.post_fifo(Event(signal=signals.Reset))
     # let the thread catch up before we exit main
     time.sleep(0.01)

If you run this code you will see something like this:

.. code-block:: text
  
   hello from outer_state
   init
   hello from inner_state
   [2019-07-22 13:13:59.860092] [ao] e->start_at() top->inner_state
   run some code, but don't transition
   resetting the chart
   exiting inner_state
   exiting outer_state
   hello from outer_state
   init
   hello from inner_state
   [2019-07-22 13:13:59.861465] [ao] e->Reset() inner_state->inner_state


We see that the "``run some code, but don't transition``" print output occurred
between the ``start_at`` call and the posting of the ``Reset`` event.  But there
is no mention of this hook in the time-stamped trace output.  This is because
the trace instrumentation only presents high level state transition information.
The trace intentionally hides details.

Print statements are useful if you want to see if something is working; but you
don't always want them cluttering up your code.

.. _recipes-comprehensive-instrumentation-with-the-live_spy:

Comprehensive Instrumentation with the live_spy and scribble
------------------------------------------------------------

The miros library provides a second kind of instrumentation when you wrap your
state functions inside of the ``@spy_on`` decorators.  You can turn on the
``live_spy`` instrumentation to spy on everything your event processor is
doing.  Instead of printing, you can inject your messages into this spy stream,
by using the ``scribble`` call.  Let's change our design a bit to demonstrate
these features:

.. image:: _static/state_recipe_7.svg
    :target: _static/state_recipe_7.pdf
    :align: center

Here is the code:

.. code-block:: python
  :emphasize-lines: 15, 18, 21, 24, 27, 38, 41, 50
  
   # simple_state_7.py
   import time
   from collections import namedtuple

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.scribble("hello from outer_state")
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       chart.scribble("init")
       status = chart.trans(inner_state)
     elif(e.signal == signals.Hook):
       chart.scribble("run some code, but don't transition")
       status = return_status.HANDLED
     elif(e.signal == signals.Reset):
       chart.scribble("resetting the chart")
       status = chart.trans(outer_state)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.scribble("exiting outer_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.scribble("hello from inner_state")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.scribble("exiting inner_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

   if __name__ == '__main__':
     ao = ActiveObject("ao")
     ao.live_spy = True
     ao.start_at(outer_state)
     ao.post_fifo(Event(signal=signals.Hook))
     ao.post_fifo(Event(signal=signals.Reset))
     # let the thread catch up before we exit main
     time.sleep(0.01)

If we run it we will see (I have highlighted the scribble statements):

.. code-block:: text
  :emphasize-lines: 4, 6, 9, 14, 19, 21, 24, 26, 28, 31
  
   START
   SEARCH_FOR_SUPER_SIGNAL:outer_state
   ENTRY_SIGNAL:outer_state
   hello from outer_state
   INIT_SIGNAL:outer_state
   init
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   ENTRY_SIGNAL:inner_state
   hello from inner_state
   INIT_SIGNAL:inner_state
   <- Queued:(0) Deferred:(0)
   Hook:inner_state
   Hook:outer_state
   run some code, but don't transition
   Hook:outer_state:HOOK
   <- Queued:(1) Deferred:(0)
   Reset:inner_state
   Reset:outer_state
   resetting the chart
   EXIT_SIGNAL:inner_state
   exiting inner_state
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   EXIT_SIGNAL:outer_state
   exiting outer_state
   ENTRY_SIGNAL:outer_state
   hello from outer_state
   INIT_SIGNAL:outer_state
   init
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   ENTRY_SIGNAL:inner_state
   hello from inner_state
   INIT_SIGNAL:inner_state
   <- Queued:(0) Deferred:(0)

You can interleave the trace information into the spy information
by turning on both the ``live_spy`` and the ``live_trace``.  This would result in
this output:

.. code-block:: text
  
   [2019-07-26 06:29:33.774768] [ao] e->start_at() top->inner_state
   START
   SEARCH_FOR_SUPER_SIGNAL:outer_state
   ENTRY_SIGNAL:outer_state
   hello from outer_state
   INIT_SIGNAL:outer_state
   init
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   ENTRY_SIGNAL:inner_state
   hello from inner_state
   INIT_SIGNAL:inner_state
   <- Queued:(0) Deferred:(0)
   Hook:inner_state
   Hook:outer_state
   run some code, but don't transition
   Hook:outer_state:HOOK
   <- Queued:(1) Deferred:(0)
   [2019-07-26 06:29:33.776462] [ao] e->Reset() inner_state->inner_state
   Reset:inner_state
   Reset:outer_state
   resetting the chart
   EXIT_SIGNAL:inner_state
   exiting inner_state
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   EXIT_SIGNAL:outer_state
   exiting outer_state
   ENTRY_SIGNAL:outer_state
   hello from outer_state
   INIT_SIGNAL:outer_state
   init
   SEARCH_FOR_SUPER_SIGNAL:inner_state
   ENTRY_SIGNAL:inner_state
   hello from inner_state
   INIT_SIGNAL:inner_state
   <- Queued:(0) Deferred:(0)

This kind of feedback will become more and more important to you as you build
more and more complex systems.

The attachment point between the ``ActiveObject`` and the HSM in the diagram
serves double duty.  It shows that there is an event processor that is using
these two state functions and it shows where the HSM is started.  An
``ActiveObject`` has its own thread and all of the state machines memory is held
within it.  The functions merely describe how and when different memory
operations should be performed, but the functions do not have their own memory.
For this reason, you can attach more than one ``ActiveObject`` to the same HSM.

.. _recipes-attaching-more-than-one-active-object-to-an-hsm:

Attaching More than one ActiveObject to an HSM
----------------------------------------------

Here we see two different ``ActiveObject`` objects attached to the same HSM.  

.. image:: _static/state_recipe_8.svg
    :target: _static/state_recipe_8.pdf
    :align: center

.. note::
  
   Technically speaking, the above UML diagram is incorrect.  A class should not
   be drawn on a UML diagram more than once.  I'm drawing it twice to make a
   point.

.. note::

  miros runs in python3.5 and above, so I am not using fstrings, since they were
  not included in python3.5

Here is the code:

.. code-block:: python
  
  # simple_state_8.py
  import time
  from collections import namedtuple
  
  from miros import Event
  from miros import spy_on
  from miros import signals
  from miros import ActiveObject
  from miros import return_status
  
  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("{}: hello from outer_state".format(chart.name))
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      print("{}: init".format(chart.name))
      status = chart.trans(inner_state)
    elif(e.signal == signals.Hook):
      print("{}: run some code, but don't transition".format(chart.name))
      status = return_status.HANDLED
    elif(e.signal == signals.Reset):
      print("{}: resetting the chart".format(chart.name))
      status = chart.trans(outer_state)
    elif(e.signal == signals.EXIT_SIGNAL):
      print("{}: exiting outer_state".format(chart.name))
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status
  
  @spy_on
  def inner_state(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("{}: hello from inner_state".format(chart.name))
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      print("{}: exiting inner_state".format(chart.name))
      status = return_status.HANDLED
    else:
      chart.temp.fun = outer_state
      status = return_status.SUPER
    return status
  
  if __name__ == '__main__':
    ao1 = ActiveObject("ao1")
    ao1.live_trace = True
    ao1.start_at(outer_state)
    ao1.post_fifo(Event(signal=signals.Hook))
    ao1.post_fifo(Event(signal=signals.Reset))
  
    ao2 = ActiveObject("ao2")
    ao2.live_trace = True
    ao2.start_at(inner_state)
    ao2.post_fifo(Event(signal=signals.Hook))
    ao2.post_fifo(Event(signal=signals.Reset))
    # let the thread catch up before we exit main
    time.sleep(0.01)

We have placed our print statements back into the state functions and we have
created two different ``ActiveObjects`` starting the first in the outer_state
and starting the second in the inner_state.  Then we send the ``Hook`` and
``Reset`` events to both active objects.

Since each ``ActiveObject`` runs in it's own thread they will process their
events independent of each other; here is the output of this little program:

.. code-block:: text
  
   ao1: hello from outer_state
   ao1: init
   ao1: hello from inner_state
   [2019-07-26 07:41:53.077229] [ao1] e->start_at() top->inner_state
   ao2: hello from outer_state
   ao2: hello from inner_state
   ao1: run some code, but don't transition
   [2019-07-26 07:41:53.080259] [ao2] e->start_at() top->inner_state
   ao1: resetting the chart
   ao1: exiting inner_state
   ao1: exiting outer_state
   ao1: hello from outer_state
   ao1: init
   ao1: hello from inner_state
   [2019-07-26 07:41:53.080885] [ao1] e->Reset() inner_state->inner_state
   ao2: run some code, but don't transition
   ao2: resetting the chart
   ao2: exiting inner_state
   ao2: exiting outer_state
   ao2: hello from outer_state
   ao2: init
   ao2: hello from inner_state
   [2019-07-26 07:41:53.082678] [ao2] e->Reset() inner_state->inner_state

We can see that our output is kind of messy.  The print messages are interleaved
because we have two ActiveObjects running in parallel, each in their own
thread.  It turns out that the ``print`` function is not thread safe, but the
Python logger is.  

.. _recipes-over-riding-the-live-instrumentation-to-the-python-logger:

Making the Live Instrumentation use the Python Logger
-----------------------------------------------------

Let's adjust our design a bit so that our live_trace and our live_spy will write
to the Python logger instead of the terminal's output.


.. image:: _static/state_recipe_9.svg
    :target: _static/state_recipe_9.pdf
    :align: center

We subclass the ``Activeobject`` into a class which "has a" logger.  This class will
have two custom instrumentation callbacks, one for our trace and one for our
spy.  We will instantiate the class twice, and start one of the statecharts in
the ``outer_state`` and the other in the ``inner_state``.  Then we will send the
``Hook`` and ``Reset`` events to both statecharts.

Here is the code:

.. code-block:: python
  
   # simple_state_9.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.scribble("hello from outer_state")
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       chart.scribble("init")
       status = chart.trans(inner_state)
     elif(e.signal == signals.Hook):
       chart.scribble("run some code, but don't transition")
       status = return_status.HANDLED
     elif(e.signal == signals.Reset):
       chart.scribble("resetting the chart")
       status = chart.trans(outer_state)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.scribble("exiting outer_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.scribble("hello from inner_state")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.scribble("exiting inner_state")
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status
       
   class ActiveObjectInstrumentToLog(ActiveObject):

     def __init__(self, name, filename=None):
       super().__init__(name)
       if filename is None:
         filename = 'simple_state_9.log'

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=filename,
         level=logging.DEBUG)

       # ActiveObject has a register_live_trace_callback and a
       # register_live_spy_callback interface, which can be used to
       # change the live_trace and live_spy behavior.  To use these
       # registration methods, you write a function which accepts a
       # string argument, provide this function as the input argument
       # to the registration method and your custom function will
       # stored, and then called each time a trace/spy string is
       # generated from within the ActiveObject's instrumentation
       # functions.  By providing your own functions, you can log
       # trace/spy information, or send it out over the network or do
       # whatever you like with it.

       # The register functions do not accept methods, they only accept
       # functions that take a single argument.  So we use the
       # functool.partial to create a function with the self baked into
       # it before it is passed into the register function. This way
       # when miros calls this function with a string, we do not get a
       # runtime error resulting from sending our customer function it
       # too few arguments.
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))

   if __name__ == '__main__':

     ao1 = ActiveObjectInstrumentToLog("ao1")
     ao1.live_trace = True
     ao1.live_spy = True

     ao2 = ActiveObjectInstrumentToLog("ao2")
     ao2.live_trace = True
     ao2.live_spy = True

     ao1.start_at(outer_state)
     ao1.post_fifo(Event(signal=signals.Hook))
     ao1.post_fifo(Event(signal=signals.Reset))

     ao2.start_at(inner_state)
     ao2.post_fifo(Event(signal=signals.Hook))
     ao2.post_fifo(Event(signal=signals.Reset))

     # let the threads catch up before we exit main
     time.sleep(0.01)


The log file created by this program would look something like this:

.. code-block:: text

   2019-07-26 11:37:22,674 DEBUG:T: [ao1] e->start_at() top->inner_state
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] START
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] ENTRY_SIGNAL:outer_state
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] hello from outer_state
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] INIT_SIGNAL:outer_state
   2019-07-26 11:37:22,675 DEBUG:S: [ao1] init
   2019-07-26 11:37:22,676 DEBUG:S: [ao1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,676 DEBUG:S: [ao1] ENTRY_SIGNAL:inner_state
   2019-07-26 11:37:22,676 DEBUG:S: [ao1] hello from inner_state
   2019-07-26 11:37:22,676 DEBUG:S: [ao1] INIT_SIGNAL:inner_state
   2019-07-26 11:37:22,676 DEBUG:S: [ao1] <- Queued:(0) Deferred:(0)
   2019-07-26 11:37:22,678 DEBUG:T: [ao2] e->start_at() top->inner_state
   2019-07-26 11:37:22,678 DEBUG:S: [ao2] START
   2019-07-26 11:37:22,678 DEBUG:S: [ao2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] ENTRY_SIGNAL:outer_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] hello from outer_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] ENTRY_SIGNAL:inner_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] hello from inner_state
   2019-07-26 11:37:22,679 DEBUG:S: [ao2] INIT_SIGNAL:inner_state
   2019-07-26 11:37:22,680 DEBUG:S: [ao1] Hook:inner_state
   2019-07-26 11:37:22,680 DEBUG:S: [ao2] <- Queued:(0) Deferred:(0)
   2019-07-26 11:37:22,680 DEBUG:S: [ao1] Hook:outer_state
   2019-07-26 11:37:22,681 DEBUG:S: [ao1] run some code, but don't transition
   2019-07-26 11:37:22,681 DEBUG:S: [ao1] Hook:outer_state:HOOK
   2019-07-26 11:37:22,681 DEBUG:S: [ao1] <- Queued:(1) Deferred:(0)
   2019-07-26 11:37:22,682 DEBUG:T: [ao1] e->Reset() inner_state->inner_state
   2019-07-26 11:37:22,682 DEBUG:S: [ao1] Reset:inner_state
   2019-07-26 11:37:22,682 DEBUG:S: [ao1] Reset:outer_state
   2019-07-26 11:37:22,682 DEBUG:S: [ao1] resetting the chart
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] EXIT_SIGNAL:inner_state
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] exiting inner_state
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] EXIT_SIGNAL:outer_state
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] exiting outer_state
   2019-07-26 11:37:22,683 DEBUG:S: [ao1] ENTRY_SIGNAL:outer_state
   2019-07-26 11:37:22,684 DEBUG:S: [ao2] Hook:inner_state
   2019-07-26 11:37:22,684 DEBUG:S: [ao1] hello from outer_state
   2019-07-26 11:37:22,684 DEBUG:S: [ao2] Hook:outer_state
   2019-07-26 11:37:22,684 DEBUG:S: [ao1] INIT_SIGNAL:outer_state
   2019-07-26 11:37:22,684 DEBUG:S: [ao2] run some code, but don't transition
   2019-07-26 11:37:22,684 DEBUG:S: [ao1] init
   2019-07-26 11:37:22,685 DEBUG:S: [ao2] Hook:outer_state:HOOK
   2019-07-26 11:37:22,685 DEBUG:S: [ao1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,685 DEBUG:S: [ao2] <- Queued:(1) Deferred:(0)
   2019-07-26 11:37:22,685 DEBUG:S: [ao1] ENTRY_SIGNAL:inner_state
   2019-07-26 11:37:22,686 DEBUG:T: [ao2] e->Reset() inner_state->inner_state
   2019-07-26 11:37:22,687 DEBUG:S: [ao1] hello from inner_state
   2019-07-26 11:37:22,687 DEBUG:S: [ao2] Reset:inner_state
   2019-07-26 11:37:22,687 DEBUG:S: [ao1] INIT_SIGNAL:inner_state
   2019-07-26 11:37:22,687 DEBUG:S: [ao2] Reset:outer_state
   2019-07-26 11:37:22,687 DEBUG:S: [ao1] <- Queued:(0) Deferred:(0)
   2019-07-26 11:37:22,688 DEBUG:S: [ao2] resetting the chart
   2019-07-26 11:37:22,688 DEBUG:S: [ao2] EXIT_SIGNAL:inner_state
   2019-07-26 11:37:22,688 DEBUG:S: [ao2] exiting inner_state
   2019-07-26 11:37:22,688 DEBUG:S: [ao2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,688 DEBUG:S: [ao2] EXIT_SIGNAL:outer_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] exiting outer_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] ENTRY_SIGNAL:outer_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] hello from outer_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] INIT_SIGNAL:outer_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] init
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-26 11:37:22,689 DEBUG:S: [ao2] ENTRY_SIGNAL:inner_state
   2019-07-26 11:37:22,690 DEBUG:S: [ao2] hello from inner_state
   2019-07-26 11:37:22,690 DEBUG:S: [ao2] INIT_SIGNAL:inner_state
   2019-07-26 11:37:22,690 DEBUG:S: [ao2] <- Queued:(0) Deferred:(0)
 
That's a lot of information. Suppose we just wanted to see the ``ao1`` trace:

.. code-block:: bash
  
  cat simple_state_9.log | grep T:*.a01

This would result in the following output:

.. code-block:: python
  
  2019-07-26 11:37:22,674 DEBUG:T: [ao1] e->start_at() top->inner_state
  2019-07-26 11:37:22,682 DEBUG:T: [ao1] e->Reset() inner_state->inner_state

If you wanted to see the spy of ``a02``, you could grep ``S:*.a02``... etc.

So far we have seen how to create state functions, how to link them to an
``Activeobject``, which collectively makes a statechart.  If you would like to
see a comprehensive example of all of the signal pathways supported by the Miro
Samek event processor, look at this :ref:`example <comprehensive-comprehensive>`.

.. _recipes-making-a-statechart-from-a-class:

Making a Statechart from a class
--------------------------------

Is there a way to just make a statechart by instantiating a class?

Yes, this is what the ``Factory`` class is for.  It links a set of signals to
static methods; and assigns this linked collection to a state.  You do this once
per state, then you nest the states within one another; and the resulting object
is a statechart.  To start it's thread, you call it's start_at method, just as
you would with an ``ActiveObject``.

Let's rebuild our previous example using the ``miros.Factory`` class.

.. image:: _static/state_recipe_10.svg
    :target: _static/state_recipe_10.pdf
    :align: center

.. note::

   The above image is probably breaking the UML specification, since I'm packing an
   HSM diagram into a class icon.  But I don't care, since I have found that this
   is a compact way of drawing my design intentions.

The diagram is saying that the ``FactoryInstrumentationToLog`` class has a
logging object and is inherited from the ``Factory`` class, and the ``Factory``
class is inherited from the ``ActiveObject`` class.  It has two attributes,
``live_spy`` and ``live_trace`` and three methods, ``trace_callback``,
``spy_callback`` and ``start_at``.

I don't know how to draw UML to describe that I want this class to start it's
statemachine in two different ways, so I write the ``start_at`` code onto the
diagram to remind myself that I'm thinking this way.

Within the class, we see the same state machine we described in the
``simple_state_9.py`` code listing.

Here is the above design in code:

.. code-block:: python
  
   # simple_state_10.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)

       self.live_trace = \
         False if live_trace == None else live_trace
       self.live_spy = \
         False if live_spy == None else live_spy

       self.log_file_name = \
         'simple_state_10.log' if log_file_name == None else log_file_name

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=self.log_file_name,
         level=logging.DEBUG)
     
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.inner_state_entry_signal). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.inner_state_exit_signal). \
         to_method()

       self.nest(self.outer_state, parent=None). \
         nest(self.inner_state, parent=self.outer_state)

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))
     
     @staticmethod
     def outer_state_entry_signal(chart, e):
       chart.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     @staticmethod
     def outer_state_init_signal(chart, e):
       chart.scribble("init")
       status = chart.trans(chart.inner_state)
       return status

     @staticmethod
     def outer_state_hook(chart, e):
       status = return_status.HANDLED
       chart.scribble("run some code, but don't transition")
       return status

     @staticmethod
     def outer_state_reset(chart, e):
       status = chart.trans(chart.outer_state)
       return status

     @staticmethod
     def outer_state_exit_signal(chart, e):
       status = return_status.HANDLED
       chart.scribble("exiting the outer_state")
       return status

     @staticmethod
     def inner_state_entry_signal(chart, e):
       status = return_status.HANDLED
       chart.scribble("hello from inner_state")
       return status

     @staticmethod
     def inner_state_exit_signal(chart, e):
       status = return_status.HANDLED
       chart.scribble("exiting inner_state")
       return status

   if __name__ == '__main__':

     f1 = FactoryInstrumentationToLog(
       "f1",
       live_trace=True,
       live_spy=True
     )

     f2 = FactoryInstrumentationToLog(
       "f2",
       live_trace=True,
       live_spy=True
     )

     f1.start_at(f1.outer_state)
     f1.post_fifo(Event(signal=signals.Hook))
     f1.post_fifo(Event(signal=signals.Reset))

     f2.start_at(f2.inner_state)
     f2.post_fifo(Event(signal=signals.Hook))
     f2.post_fifo(Event(signal=signals.Reset))

     # let the threads catch up before we exit main
     time.sleep(0.01)

The benefit of programming a statechart this way is in it's containment.  You
don't have functions drifting in your package's name space, they are nicely
contained as static methods within your statechart's class.  In addition to
this, you no longer have to manipulate the ``temp.fun`` attribute of the event
processor, this complexity is hidden within the ``Factory`` object's
state-function-manufacturing process.  To move the state functions into a class,
you can just add a ``@staticmethod`` decorator on top of them.  Any static
method is just a function forced into a class.

If you like, you can point the ``handler`` of the Factory's ``create`` method to
a method instead of a function (or staticmethod).  To write the code this way
only slightly changes our diagram, we need to replace all ``chart`` variables
with ``self``:

.. image:: _static/state_recipe_11.svg
    :target: _static/state_recipe_11.pdf
    :align: center

To write this design, our state functions become state methods (this feature
was added in miros 4.1.2):

.. code-block:: python
  
   # simple_state_11.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)

       self.live_trace = \
         False if live_trace == None else live_trace
       self.live_spy = \
         False if live_spy == None else live_spy

       self.log_file_name = \
         'simple_state_11.log' if log_file_name == None else log_file_name

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=self.log_file_name,
         level=logging.DEBUG)
     
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.inner_state_entry_signal). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.inner_state_exit_signal). \
         to_method()

       self.nest(self.outer_state, parent=None). \
         nest(self.inner_state, parent=self.outer_state)

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))
     
     def outer_state_entry_signal(self, e):
       self.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     def outer_state_init_signal(self, e):
       self.scribble("init")
       status = self.trans(self.inner_state)
       return status

     def outer_state_hook(self, e):
       status = return_status.HANDLED
       self.scribble("run some code, but don't transition")
       return status

     def outer_state_reset(self, e):
       status = self.trans(self.outer_state)
       return status

     def outer_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting the outer_state")
       return status

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("hello from inner_state")
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting inner_state")
       return status

   if __name__ == '__main__':

     f1 = FactoryInstrumentationToLog(
       "f1",
       live_trace=True,
       live_spy=True
     )

     f2 = FactoryInstrumentationToLog(
       "f2",
       live_trace=True,
       live_spy=True
     )

     f1.start_at(f1.outer_state)
     f1.post_fifo(Event(signal=signals.Hook))
     f1.post_fifo(Event(signal=signals.Reset))

     f2.start_at(f2.inner_state)
     f2.post_fifo(Event(signal=signals.Hook))
     f2.post_fifo(Event(signal=signals.Reset))

     # let the threads catch up before we exit main
     time.sleep(0.01)

.. note::
  
   It's nice to look at code that looks like a typical python class.  But be
   warned, the methods you assigned to your create handlers will actually be run in
   a separate thread from your ``__init__`` and ``start_at`` methods.  The
   ``trace_callback`` and ``spy_callback`` and all of your state handler methods
   will run in the statechart's thread.  This mostly isn't a problem, unless you
   are trying to get data from your statechart into your main program.  We will see
   how to do this shortly

If we ran the code and looked at it's log file we would see:

.. code-block:: text
  
   2019-07-30 06:25:43,725 DEBUG:T: [f1] e->start_at() top->inner_state
   2019-07-30 06:25:43,726 DEBUG:S: [f1] START
   2019-07-30 06:25:43,726 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-07-30 06:25:43,726 DEBUG:S: [f1] ENTRY_SIGNAL:outer_state
   2019-07-30 06:25:43,726 DEBUG:S: [f1] hello from outer_state
   2019-07-30 06:25:43,726 DEBUG:S: [f1] INIT_SIGNAL:outer_state
   2019-07-30 06:25:43,726 DEBUG:S: [f1] init
   2019-07-30 06:25:43,726 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,727 DEBUG:S: [f1] ENTRY_SIGNAL:inner_state
   2019-07-30 06:25:43,727 DEBUG:S: [f1] hello from inner_state
   2019-07-30 06:25:43,727 DEBUG:S: [f1] INIT_SIGNAL:inner_state
   2019-07-30 06:25:43,727 DEBUG:S: [f1] <- Queued:(0) Deferred:(0)
   2019-07-30 06:25:43,729 DEBUG:T: [f2] e->start_at() top->inner_state
   2019-07-30 06:25:43,729 DEBUG:S: [f2] START
   2019-07-30 06:25:43,729 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] ENTRY_SIGNAL:outer_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] hello from outer_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] ENTRY_SIGNAL:inner_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] hello from inner_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] INIT_SIGNAL:inner_state
   2019-07-30 06:25:43,730 DEBUG:S: [f2] <- Queued:(0) Deferred:(0)
   2019-07-30 06:25:43,731 DEBUG:S: [f2] Hook:inner_state
   2019-07-30 06:25:43,731 DEBUG:S: [f2] Hook:outer_state
   2019-07-30 06:25:43,731 DEBUG:S: [f2] run some code, but don't transition
   2019-07-30 06:25:43,732 DEBUG:S: [f2] Hook:outer_state:HOOK
   2019-07-30 06:25:43,732 DEBUG:S: [f2] <- Queued:(1) Deferred:(0)
   2019-07-30 06:25:43,733 DEBUG:T: [f2] e->Reset() inner_state->inner_state
   2019-07-30 06:25:43,733 DEBUG:S: [f2] Reset:inner_state
   2019-07-30 06:25:43,733 DEBUG:S: [f2] Reset:outer_state
   2019-07-30 06:25:43,733 DEBUG:S: [f2] EXIT_SIGNAL:inner_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] exiting inner_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] EXIT_SIGNAL:outer_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] exiting the outer_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] ENTRY_SIGNAL:outer_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] hello from outer_state
   2019-07-30 06:25:43,734 DEBUG:S: [f2] INIT_SIGNAL:outer_state
   2019-07-30 06:25:43,735 DEBUG:S: [f2] init
   2019-07-30 06:25:43,735 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,735 DEBUG:S: [f2] ENTRY_SIGNAL:inner_state
   2019-07-30 06:25:43,735 DEBUG:S: [f2] hello from inner_state
   2019-07-30 06:25:43,735 DEBUG:S: [f2] INIT_SIGNAL:inner_state
   2019-07-30 06:25:43,736 DEBUG:S: [f1] Hook:inner_state
   2019-07-30 06:25:43,736 DEBUG:S: [f2] <- Queued:(0) Deferred:(0)
   2019-07-30 06:25:43,736 DEBUG:S: [f1] Hook:outer_state
   2019-07-30 06:25:43,736 DEBUG:S: [f1] run some code, but don't transition
   2019-07-30 06:25:43,736 DEBUG:S: [f1] Hook:outer_state:HOOK
   2019-07-30 06:25:43,737 DEBUG:S: [f1] <- Queued:(1) Deferred:(0)
   2019-07-30 06:25:43,738 DEBUG:T: [f1] e->Reset() inner_state->inner_state
   2019-07-30 06:25:43,738 DEBUG:S: [f1] Reset:inner_state
   2019-07-30 06:25:43,738 DEBUG:S: [f1] Reset:outer_state
   2019-07-30 06:25:43,738 DEBUG:S: [f1] EXIT_SIGNAL:inner_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] exiting inner_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] EXIT_SIGNAL:outer_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] exiting the outer_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] ENTRY_SIGNAL:outer_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] hello from outer_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] INIT_SIGNAL:outer_state
   2019-07-30 06:25:43,739 DEBUG:S: [f1] init
   2019-07-30 06:25:43,740 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-07-30 06:25:43,740 DEBUG:S: [f1] ENTRY_SIGNAL:inner_state
   2019-07-30 06:25:43,740 DEBUG:S: [f1] hello from inner_state
   2019-07-30 06:25:43,740 DEBUG:S: [f1] INIT_SIGNAL:inner_state
   2019-07-30 06:25:43,740 DEBUG:S: [f1] <- Queued:(0) Deferred:(0)
   2019-08-01 06:28:10,237 DEBUG:T: [f1] e->start_at() top->inner_state
   2019-08-01 06:28:10,238 DEBUG:S: [f1] START
   2019-08-01 06:28:10,238 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-08-01 06:28:10,238 DEBUG:S: [f1] ENTRY_SIGNAL:outer_state
   2019-08-01 06:28:10,238 DEBUG:S: [f1] hello from outer_state
   2019-08-01 06:28:10,238 DEBUG:S: [f1] INIT_SIGNAL:outer_state
   2019-08-01 06:28:10,238 DEBUG:S: [f1] init
   2019-08-01 06:28:10,239 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,239 DEBUG:S: [f1] ENTRY_SIGNAL:inner_state
   2019-08-01 06:28:10,239 DEBUG:S: [f1] hello from inner_state
   2019-08-01 06:28:10,239 DEBUG:S: [f1] INIT_SIGNAL:inner_state
   2019-08-01 06:28:10,239 DEBUG:S: [f1] <- Queued:(0) Deferred:(0)
   2019-08-01 06:28:10,241 DEBUG:T: [f2] e->start_at() top->inner_state
   2019-08-01 06:28:10,241 DEBUG:S: [f1] Hook:inner_state
   2019-08-01 06:28:10,241 DEBUG:S: [f2] START
   2019-08-01 06:28:10,242 DEBUG:S: [f1] Hook:outer_state
   2019-08-01 06:28:10,242 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,242 DEBUG:S: [f1] run some code, but don't transition
   2019-08-01 06:28:10,242 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:outer_state
   2019-08-01 06:28:10,242 DEBUG:S: [f1] Hook:outer_state:HOOK
   2019-08-01 06:28:10,243 DEBUG:S: [f2] ENTRY_SIGNAL:outer_state
   2019-08-01 06:28:10,243 DEBUG:S: [f1] <- Queued:(1) Deferred:(0)
   2019-08-01 06:28:10,243 DEBUG:S: [f2] hello from outer_state
   2019-08-01 06:28:10,245 DEBUG:T: [f1] e->Reset() inner_state->inner_state
   2019-08-01 06:28:10,245 DEBUG:S: [f2] ENTRY_SIGNAL:inner_state
   2019-08-01 06:28:10,245 DEBUG:S: [f1] Reset:inner_state
   2019-08-01 06:28:10,245 DEBUG:S: [f2] hello from inner_state
   2019-08-01 06:28:10,245 DEBUG:S: [f1] Reset:outer_state
   2019-08-01 06:28:10,246 DEBUG:S: [f2] INIT_SIGNAL:inner_state
   2019-08-01 06:28:10,246 DEBUG:S: [f1] EXIT_SIGNAL:inner_state
   2019-08-01 06:28:10,246 DEBUG:S: [f2] <- Queued:(0) Deferred:(0)
   2019-08-01 06:28:10,246 DEBUG:S: [f1] exiting inner_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] EXIT_SIGNAL:outer_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] exiting the outer_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] ENTRY_SIGNAL:outer_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] hello from outer_state
   2019-08-01 06:28:10,247 DEBUG:S: [f1] INIT_SIGNAL:outer_state
   2019-08-01 06:28:10,248 DEBUG:S: [f1] init
   2019-08-01 06:28:10,248 DEBUG:S: [f1] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,248 DEBUG:S: [f1] ENTRY_SIGNAL:inner_state
   2019-08-01 06:28:10,248 DEBUG:S: [f1] hello from inner_state
   2019-08-01 06:28:10,248 DEBUG:S: [f1] INIT_SIGNAL:inner_state
   2019-08-01 06:28:10,248 DEBUG:S: [f1] <- Queued:(0) Deferred:(0)
   2019-08-01 06:28:10,249 DEBUG:S: [f2] Hook:inner_state
   2019-08-01 06:28:10,249 DEBUG:S: [f2] Hook:outer_state
   2019-08-01 06:28:10,249 DEBUG:S: [f2] run some code, but don't transition
   2019-08-01 06:28:10,249 DEBUG:S: [f2] Hook:outer_state:HOOK
   2019-08-01 06:28:10,250 DEBUG:S: [f2] <- Queued:(1) Deferred:(0)
   2019-08-01 06:28:10,251 DEBUG:T: [f2] e->Reset() inner_state->inner_state
   2019-08-01 06:28:10,251 DEBUG:S: [f2] Reset:inner_state
   2019-08-01 06:28:10,251 DEBUG:S: [f2] Reset:outer_state
   2019-08-01 06:28:10,251 DEBUG:S: [f2] EXIT_SIGNAL:inner_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] exiting inner_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] EXIT_SIGNAL:outer_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] exiting the outer_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] ENTRY_SIGNAL:outer_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] hello from outer_state
   2019-08-01 06:28:10,252 DEBUG:S: [f2] INIT_SIGNAL:outer_state
   2019-08-01 06:28:10,253 DEBUG:S: [f2] init
   2019-08-01 06:28:10,253 DEBUG:S: [f2] SEARCH_FOR_SUPER_SIGNAL:inner_state
   2019-08-01 06:28:10,253 DEBUG:S: [f2] ENTRY_SIGNAL:inner_state
   2019-08-01 06:28:10,253 DEBUG:S: [f2] hello from inner_state
   2019-08-01 06:28:10,253 DEBUG:S: [f2] INIT_SIGNAL:inner_state
   2019-08-01 06:28:10,253 DEBUG:S: [f2] <- Queued:(0) Deferred:(0)

You can see as much information as you like about your statechart dynamics.
Typically I only turn on the spy when I'm debugging a problem; and I'll leave
the trace on when I'm trying to see how a statechart behaves.

.. _recipes-communication-between-statecharts:

Communication between Statecharts
---------------------------------

To have two different statecharts communicate with one another we use the
publish and subscribe methods (available in the ActiveObject and its
subclasses).  Let's adjust our example a bit so that we can send a Broadcast
event to one statechart, which will cause both charts to act.

.. image:: _static/state_recipe_12.svg
    :target: _static/state_recipe_12.pdf
    :align: center

Here is the code (highlighting pub/sub/action code):

.. code-block:: python
  :emphasize-lines: 46-49, 76, 91-94, 96-99, 142
  
   # simple_state_12.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)

       self.live_trace = \
         False if live_trace == None else live_trace
       self.live_spy = \
         False if live_spy == None else live_spy

       self.log_file_name = \
         'simple_state_12.log' if log_file_name == None else log_file_name

       # clear our log every time we run this program
       with open(self.log_file_name, "w") as fp:
         fp.write("")

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=self.log_file_name,
         level=logging.DEBUG)
     
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Send_Broadcast, \
           handler=self.outer_state_send_broadcast). \
         catch(signal=signals.BROADCAST, \
           handler=self.outer_state_broadcast). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.inner_state_entry_signal). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.inner_state_exit_signal). \
         to_method()

       self.nest(self.outer_state, parent=None). \
         nest(self.inner_state, parent=self.outer_state)

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))
     
     def outer_state_entry_signal(self, e):
       self.subscribe(Event(signal=signals.BROADCAST))
       self.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     def outer_state_init_signal(self, e):
       self.scribble("init")
       status = self.trans(self.inner_state)
       return status

     def outer_state_hook(self, e):
       status = return_status.HANDLED
       self.scribble("run some code, but don't transition")
       return status

     def outer_state_send_broadcast(self, e):
       status = return_status.HANDLED
       self.publish(Event(signal=signals.BROADCAST))
       return status

     def outer_state_broadcast(self, e):
       status = return_status.HANDLED
       self.scribble("received broadcast")
       return status

     def outer_state_reset(self, e):
       status = self.trans(self.outer_state)
       return status

     def outer_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting the outer_state")
       return status

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("hello from inner_state")
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting inner_state")
       return status

   if __name__ == '__main__':

     f1 = FactoryInstrumentationToLog(
       "f1",
       live_trace=True,
       live_spy=True
     )

     f2 = FactoryInstrumentationToLog(
       "f2",
       live_trace=True,
       live_spy=True
     )

     f1.start_at(f1.outer_state)
     f1.post_fifo(Event(signal=signals.Hook))
     f1.post_fifo(Event(signal=signals.Reset))

     f2.start_at(f2.inner_state)
     f2.post_fifo(Event(signal=signals.Hook))
     f2.post_fifo(Event(signal=signals.Reset))

     f1.post_fifo(Event(signal=signals.Send_Broadcast))

     # let the threads catch up before we exit main
     time.sleep(0.02)

The above code posts a ``Send_Broadcast`` event to f1, which in turn, publishes
the ``Broadcast`` event.  Since both charts subscribed to this event, they will
react to the ``Broadcast`` event.  The ``Broadcast`` signal is attached to both
charts as a hook in their ``outer_state``, which means this hook's reactive
behavior will be common for the outer_state and the inner_state.  The "received
broadcast" message will be written into the spy log via the ``scribble`` method,
if a ``Broadcast`` event is received in either state.  No state transition will
occur as a result of the reaction to a ``Broadcast`` event; ``Broadcast`` is a
hook and hooks don't cause state transitions.

If we run our code, then filter its log file through a grep search pattern, we
will see that both charts received the ``BROADCAST`` event:

.. code-block:: text
  :emphasize-lines: 1
  :linenos:
  
  python simple_state_12.py ; cat simple_state_12.log | grep broadcast
  2019-08-02 07:03:17,352 DEBUG:S: [f1] received broadcast
  2019-08-02 07:03:17,355 DEBUG:S: [f2] received broadcast

So now we know how:

* to build a statechart within a class
* to tie the statechart instrumentation features to the logging system (or whatever you want)
* to have two or more statecharts communicate with one another
* to map the statechart features into functions of static methods or methods.

Can we program our states by difference?

.. _recipes-overload-a-state-in-a-subclass:

Overload a State in a Subclass
------------------------------
Suppose our specification poses a problem that can be broken into two or more
subdesigns, and these designs are very similar.  Since we know how to tie our
event handlers to methods in a class, we can just subclass one statechart and
overload the event handlers that we need to change.

Here is how to draw this as a UML diagram.  The F1 class is our first completed
subdesign and F2 is just like F1, except we change the behavior of the
inner_state's entry and exit conditions:

.. image:: _static/state_recipe_13.svg
    :target: _static/state_recipe_13.pdf
    :align: center

The diagram mostly tells us what is going on, and I have added a few notes to
belabor the point.  Here is the code, I have highlighted the
statechart-by-difference part of the design:

.. code-block:: python
  :emphasize-lines: 120-122, 124-127, 129-132
  
   # simple_state_13.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class F1(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)

       self.live_trace = \
         False if live_trace == None else live_trace
       self.live_spy = \
         False if live_spy == None else live_spy

       self.log_file_name = \
         'simple_state_13.log' if log_file_name == None else log_file_name

       # clear our log every time we run this program
       with open(self.log_file_name, "w") as fp:
         fp.write("")

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=self.log_file_name,
         level=logging.DEBUG)
     
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Send_Broadcast, \
           handler=self.outer_state_send_broadcast). \
         catch(signal=signals.BROADCAST, \
           handler=self.outer_state_broadcast). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.inner_state_entry_signal). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.inner_state_exit_signal). \
         to_method()

       self.nest(self.outer_state, parent=None). \
         nest(self.inner_state, parent=self.outer_state)

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))
     
     def outer_state_entry_signal(self, e):
       self.subscribe(Event(signal=signals.BROADCAST))
       self.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     def outer_state_init_signal(self, e):
       self.scribble("init")
       status = self.trans(self.inner_state)
       return status

     def outer_state_hook(self, e):
       status = return_status.HANDLED
       self.scribble("run some code, but don't transition")
       return status

     def outer_state_send_broadcast(self, e):
       status = return_status.HANDLED
       self.publish(Event(signal=signals.BROADCAST))
       return status

     def outer_state_broadcast(self, e):
       status = return_status.HANDLED
       self.scribble("received broadcast")
       return status

     def outer_state_reset(self, e):
       status = self.trans(self.outer_state)
       return status

     def outer_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting the outer_state")
       return status

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("hello from inner_state")
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting inner_state")
       return status

   class F2(F1):
     def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("hello from new inner_state")
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting new inner_state")
       return status

   if __name__ == '__main__':

     f1 = F1(
       "f1",
       live_trace=True,
       live_spy=True
     )

     f2 = F2(
       "f2",
       live_trace=True,
       live_spy=True
     )

     f1.start_at(f1.outer_state)
     f1.post_fifo(Event(signal=signals.Hook))
     f1.post_fifo(Event(signal=signals.Reset))

     f2.start_at(f2.inner_state)
     f2.post_fifo(Event(signal=signals.Hook))
     f2.post_fifo(Event(signal=signals.Reset))

     f1.post_fifo(Event(signal=signals.Send_Broadcast))

     # let the threads catch up before we exit main
     time.sleep(0.02)

This kind of abstraction requires a lot of understanding on the part of the
maintenance developer.  Statechart code is already hard enough to understand
without a diagram, but now parts of our diagram are missing too: to understand
one diagram we need to reference another.

If you find that your subdesign requirements change a lot you might want to just
copy its superclass's code into a flat, easy-to-read/easy-to-change form,
at the cost of repeating yourself a bit.  Then copy your diagram as a second
stand-alone design artifact.  Subclassing is software coupling, so you will have
to weigh the engineering-trade-offs as you build up your system.


.. _recipes-one-shots-and-heartbeats:

One-Shots, Multi-Shots and Heartbeats
-------------------------------------

We have seen that we can post events using the ``post_fifo`` (first in first
out) method call.  If your event needs to push itself to the front of the event
queue (force itself to have the highest priority), you would use the
``post_lifo`` (last in first out) method.

The miros library can be used to send events at regular time intervals.  The
number of times these events are sent and the regular time duration between
these events are configurable.  To keep the library's api simple, the
``post_fifo`` and ``post_lifo`` methods are used for this feature.  If you just
give a posting method an event it will put it into the event queue.  But if you
give the posting method additional timing information, it will create a
background thread and program that thread to post your event to your statechart
using your timing specification.

To demonstrate this feature, I'll adjust the design so that between the
outer_state and inner_state there will be a middle_state.  The purpose of the
middle_state will be to add a one second delay between the transition into the
inner_state from the outer_state.  The code to make a delayed event work this
way is called a one-shot  (if it fired more than once it would be called a
multishot, if it fired at a regular interval forever, it would be called a
heartbeat).

.. image:: _static/state_recipe_14.svg
    :target: _static/state_recipe_14.pdf
    :align: center

.. note::
  
   Our ``F2`` statechart is blissfully unaware the we have made this change to it,
   as it only has visibility to the inner_state event handlers.

In our design we use the ``post_fifo`` method to make the one-shot.

The ``post_fifo``/``post_lifo`` time features can be used within, or outside of,
a statechart.  In the following code example I show a one shot within (Ready)
and outside of (Reset for f1) of a statechart.  The code that has been changed
from the previous example has been highlighted.

.. code-block:: python
  :emphasize-lines: 24, 58-65, 75-76, 95, 122-129, 142-144, 131-133, 135-138, 182-187, 195
  
   # simple_state_14.py
   import re
   import time
   import logging
   from functools import partial

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class F1(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)

       self.live_trace = \
         False if live_trace == None else live_trace
       self.live_spy = \
         False if live_spy == None else live_spy

       self.times_in_inner = 0

       self.log_file_name = \
         'simple_state_14.log' if log_file_name == None else log_file_name

       # clear our log every time we run this program
       with open(self.log_file_name, "w") as fp:
         fp.write("")

       logging.basicConfig(
         format='%(asctime)s %(levelname)s:%(message)s',
         filename=self.log_file_name,
         level=logging.DEBUG)
     
       self.register_live_spy_callback(partial(self.spy_callback))
       self.register_live_trace_callback(partial(self.trace_callback))

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Send_Broadcast, \
           handler=self.outer_state_send_broadcast). \
         catch(signal=signals.BROADCAST, \
           handler=self.outer_state_broadcast). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

       self.middle_state = self.create(state="middle_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.middle_state_entry_signal). \
         catch(signal=signals.Ready,
           handler=self.middle_state_ready). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.middle_state_exit_signal). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.inner_state_entry_signal). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.inner_state_exit_signal). \
         to_method()

       self.nest(self.outer_state, parent=None). \
         nest(self.middle_state, parent=self.outer_state). \
         nest(self.inner_state, parent=self.middle_state)

     def trace_callback(self, trace):
       '''trace without datetime-stamp'''
       trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
       logging.debug("T: " + trace_without_datetime)

     def spy_callback(self, spy):
       '''spy with machine name pre-pended'''
       logging.debug("S: [{}] {}".format(self.name, spy))
     
     def outer_state_entry_signal(self, e):
       self.subscribe(Event(signal=signals.BROADCAST))
       self.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     def outer_state_init_signal(self, e):
       self.scribble("init")
       status = self.trans(self.middle_state)
       return status

     def outer_state_hook(self, e):
       status = return_status.HANDLED
       self.scribble("run some code, but don't transition")
       return status

     def outer_state_send_broadcast(self, e):
       status = return_status.HANDLED
       self.publish(Event(signal=signals.BROADCAST))
       return status

     def outer_state_broadcast(self, e):
       status = return_status.HANDLED
       self.scribble("received broadcast")
       return status

     def outer_state_reset(self, e):
       status = self.trans(self.outer_state)
       return status

     def outer_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting the outer_state")
       return status

     def middle_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("arming one-shot")
       self.post_fifo(Event(signal=signals.Ready),
         times=1,
         period=1.0,
         deferred=True)
       return status

     def middle_state_ready(self, e):
       status = self.trans(self.inner_state)
       return status

     def middle_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.cancel_events(Event(signal=signals.Ready))
       return status

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.times_in_inner += 1
       self.scribble(
         "hello from inner_state {}".format(self.times_in_inner))
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting inner_state")
       return status

   class F2(F1):
     def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)

     def inner_state_entry_signal(self, e):
       status = return_status.HANDLED
       self.scribble("hello from new inner_state")
       return status

     def inner_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting new inner_state")
       return status

   if __name__ == '__main__':

     f1 = F1(
       "f1",
       live_trace=True,
       live_spy=True,
     )

     f2 = F2(
       "f2",
       live_trace=True,
       live_spy=True,
     )

     f1.start_at(f1.outer_state)
     f1.post_fifo(Event(signal=signals.Hook))
     f1.post_fifo(
       Event(signal=signals.Reset),
       times=1,
       period=2.0,
       deferred=True
       )

     f2.start_at(f2.inner_state)
     f2.post_fifo(Event(signal=signals.Hook))
     f2.post_fifo(Event(signal=signals.Reset))
     f1.post_fifo(Event(signal=signals.Send_Broadcast))

     # delay long enough so we can see how the program behaves in time
     time.sleep(4.00)

Let's look at the design again prior to running our program:

.. image:: _static/state_recipe_14.svg
    :target: _static/state_recipe_14.pdf
    :align: center

The diagram describes how the different charts are started, but there is no
mention of the 2 second delay before we post the ``Reset`` event to our f1 chart
from our main thread.  We can see that in the exit condition of the f1
middle_state the ``Reset`` one-shot is canceled.  There is a good reason for
this: imagine that we didn't cancel the one-shot and that we were 0.5 seconds
into our 1 second wait when a ``Reset`` event was fired at our chart from the
main thread.  This would mean that the task managing the ``Ready`` event would
continue to run for another 0.5 seconds, then fire the ``Ready`` event.  The
``Ready`` event would appear to fire 0.5 seconds too early; then it would fire
again 0.5 seconds after that (from the arming of the next one-shot event).  This
is weird behavior that defies the spirit of our diagram.  As a rule, cancel your
one-shots in the exit conditions of the state that created them.

We have configured our live instrumentation in an NSA style: log everything so
you can query it later if you feel like it.  After running our program we
can take a look at the different aspects, like, what the f1 trace looks like:

.. code-block:: text
  :emphasize-lines: 1
  
  python simple_state_14.py ; cat simple_state_14.log | grep T:.*f1

  2019-08-05 12:18:37,055 DEBUG:T: [f1] e->start_at() top->middle_state
  2019-08-05 12:18:38,056 DEBUG:T: [f1] e->Ready() middle_state->inner_state
  2019-08-05 12:18:39,060 DEBUG:T: [f1] e->Reset() inner_state->middle_state
  2019-08-05 12:18:40,061 DEBUG:T: [f1] e->Ready() middle_state->inner_state

Here we see that 1 second after starting, the ``Ready`` one-shot is fired and
the statechart transitions from the middle_state into the inner_state.  Then 1
second later, it receives the ``Reset`` event putting it back into the
middle_state.  Then 1 second after that, the ``Ready`` one-shot is fired again
causing a transition into the inner_state.  The ``Ready`` one shot appears to be
working as designed.

What about our new ``times_in_inner`` code in F1?  We would expect to see that
it has written to the spy scribble twice:

.. code-block:: text
  :emphasize-lines: 1,2

  python simple_state_14.py ; \
    cat simple_state_14.log | grep S:.*f1 | grep "hello from inner"

  2019-08-05 12:23:23,054 DEBUG:S: [f1] hello from inner_state 1
  2019-08-05 12:23:25,059 DEBUG:S: [f1] hello from inner_state 2

There we go, the code works.  How about F2?  What is its inner state saying?

.. code-block:: text
  :emphasize-lines: 1,2

  python simple_state_14.py ; \
    cat simple_state_14.log | grep S:.*f2 | grep "hello from new inner"

  2019-08-05 12:29:55,678 DEBUG:S: [f2] hello from new inner_state
  2019-08-05 12:29:56,686 DEBUG:S: [f2] hello from new inner_state

So our update to F1's inner_state was not seen by the F2 statechart.  This
indicates that the inheritance structure is working.  How does F2 run
differently from F1?

.. code-block:: text
  :emphasize-lines: 1
  
  python simple_state_14.py ; cat simple_state_14.log | grep T:.*f2

  2019-08-05 12:32:08,195 DEBUG:T: [f2] e->start_at() top->inner_state
  2019-08-05 12:32:08,200 DEBUG:T: [f2] e->Reset() inner_state->middle_state
  2019-08-05 12:32:09,201 DEBUG:T: [f2] e->Ready() middle_state->inner_state

We see that the F2 statechart immediately transitions into the inner_state.
This is because we asked it to do so, the 1 second time delay offered by the
``Ready`` one-shot is by-passed, though it is still armed.  But this first
``Ready`` one-shot is never given a chance to fire, since the ``Reset`` is sent
to f2 immediately after it is in the inner_state.  This cancels the one-shot
event.  The ``Reset`` eventually causes a transition into the middle_state,
which re-arms the ``Ready`` one-shot, and we see a transition into the
inner_state about 1 second after the middle_state was entered.

.. _recipes-getting-information-out-of-your-statechart:

Creating thread-safe class Attributes
-------------------------------------

..
  Creating thread-safe class Attributes
  -------------------------------------
  A statechart is running in a separate thread from our main program; so how do we
  reach into it and read/write a variable?  We can't assume that it's thread
  won't be halfway through changing the variable we want to read/write at the moment we
  are trying to access it.
  
  To solve this problem we can use a thread safe queue.  If we use the
  ``collections.deque`` from the Python standard library, we can build a little ring
  buffer.  The statechart can post information to it, and the main thread can
  read information from it.  If we wrap the deque in a ``@property``, our exposed
  variable will just look like an attribute from outside of the class.
  
  Here is an example design of where we turn the ``times_in_inner`` attribute into a
  thread-safe property.
  
  .. image:: _static/state_recipe_15.svg
      :target: _static/state_recipe_15.pdf
      :align: center
  
  There is no UML drawing syntax for creating a Python property, so I just add a
  comment on the diagram after the ``times_in_inner`` attribute about what it
  really is.
  
  We can see how to make the ``times_in_inner`` thread safe attribute below (see
  the highlighted code):
  
  .. code-block:: python
    :emphasize-lines: 25-27, 81-83, 85-87, 153, 209, 210
    
     # simple_state_15.py
     import re
     import time
     import logging
     from functools import partial
     from collections import deque
  
     from miros import Event
     from miros import signals
     from miros import Factory
     from miros import return_status
  
     class F1(Factory):
  
       def __init__(self, name, log_file_name=None,
           live_trace=None, live_spy=None):
  
         super().__init__(name)
  
         self.live_trace = \
           False if live_trace == None else live_trace
         self.live_spy = \
           False if live_spy == None else live_spy
  
         # set up a thread safe ring buffer of size 1
         self._times_in_inner = deque(maxlen=1)
         self._times_in_inner.append(0)
  
         self.log_file_name = \
           'simple_state_15.log' if log_file_name == None else log_file_name
  
         # clear our log every time we run this program
         with open(self.log_file_name, "w") as fp:
           fp.write("")
  
         logging.basicConfig(
           format='%(asctime)s %(levelname)s:%(message)s',
           filename=self.log_file_name,
           level=logging.DEBUG)
       
         self.register_live_spy_callback(partial(self.spy_callback))
         self.register_live_trace_callback(partial(self.trace_callback))
  
         self.outer_state = self.create(state="outer_state"). \
           catch(signal=signals.ENTRY_SIGNAL,
             handler=self.outer_state_entry_signal). \
           catch(signal=signals.INIT_SIGNAL,
             handler=self.outer_state_init_signal). \
           catch(signal=signals.Hook,
             handler=self.outer_state_hook). \
           catch(signal=signals.Send_Broadcast, \
             handler=self.outer_state_send_broadcast). \
           catch(signal=signals.BROADCAST, \
             handler=self.outer_state_broadcast). \
           catch(signal=signals.Reset,
             handler=self.outer_state_reset). \
           catch(signal=signals.EXIT_SIGNAL,
             handler=self.outer_state_exit_signal). \
           to_method()
  
         self.middle_state = self.create(state="middle_state"). \
           catch(signal=signals.ENTRY_SIGNAL,
             handler=self.middle_state_entry_signal). \
           catch(signal=signals.Ready,
             handler=self.middle_state_ready). \
           catch(signal=signals.EXIT_SIGNAL,
             handler=self.middle_state_exit_signal). \
           to_method()
  
         self.inner_state = self.create(state="inner_state"). \
           catch(signal=signals.ENTRY_SIGNAL,
             handler=self.inner_state_entry_signal). \
           catch(signal=signals.EXIT_SIGNAL,
             handler=self.inner_state_exit_signal). \
           to_method()
  
         self.nest(self.outer_state, parent=None). \
           nest(self.middle_state, parent=self.outer_state). \
           nest(self.inner_state, parent=self.middle_state)
  
       @property
       def times_in_inner(self):
         return self._times_in_inner[-1]
  
       @times_in_inner.setter
       def times_in_inner(self, value):
         self._times_in_inner.append(value)
  
       def trace_callback(self, trace):
         '''trace without datetime-stamp'''
         trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
         logging.debug("T: " + trace_without_datetime)
  
       def spy_callback(self, spy):
         '''spy with machine name pre-pended'''
         logging.debug("S: [{}] {}".format(self.name, spy))
       
       def outer_state_entry_signal(self, e):
         self.subscribe(Event(signal=signals.BROADCAST))
         self.scribble("hello from outer_state")
         status = return_status.HANDLED
         return status
  
       def outer_state_init_signal(self, e):
         self.scribble("init")
         status = self.trans(self.middle_state)
         return status
  
       def outer_state_hook(self, e):
         status = return_status.HANDLED
         self.scribble("run some code, but don't transition")
         return status
  
       def outer_state_send_broadcast(self, e):
         status = return_status.HANDLED
         self.publish(Event(signal=signals.BROADCAST))
         return status
  
       def outer_state_broadcast(self, e):
         status = return_status.HANDLED
         self.scribble("received broadcast")
         return status
  
       def outer_state_reset(self, e):
         status = self.trans(self.outer_state)
         return status
  
       def outer_state_exit_signal(self, e):
         status = return_status.HANDLED
         self.scribble("exiting the outer_state")
         return status
  
       def middle_state_entry_signal(self, e):
         status = return_status.HANDLED
         self.scribble("arming one-shot")
         self.post_fifo(Event(signal=signals.Ready),
           times=1,
           period=1.0,
           deferred=True)
         return status
  
       def middle_state_ready(self, e):
         status = self.trans(self.inner_state)
         return status
  
       def middle_state_exit_signal(self, e):
         status = return_status.HANDLED
         self.cancel_events(Event(signal=signals.Ready))
         return status
  
       def inner_state_entry_signal(self, e):
         status = return_status.HANDLED
         self.times_in_inner += 1
         self.scribble(
           "hello from inner_state {}".format(self.times_in_inner))
         return status
  
       def inner_state_exit_signal(self, e):
         status = return_status.HANDLED
         self.scribble("exiting inner_state")
         return status
  
     class F2(F1):
       def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
  
       def inner_state_entry_signal(self, e):
         status = return_status.HANDLED
         self.scribble("hello from new inner_state")
         return status
  
       def inner_state_exit_signal(self, e):
         status = return_status.HANDLED
         self.scribble("exiting new inner_state")
         return status
  
     if __name__ == '__main__':
  
       f1 = F1(
         "f1",
         live_trace=True,
         live_spy=True,
       )
  
       f2 = F2(
         "f2",
         live_trace=True,
         live_spy=True,
       )
  
       f1.start_at(f1.outer_state)
       f1.post_fifo(Event(signal=signals.Hook))
       f1.post_fifo(
         Event(signal=signals.Reset),
         times=1,
         period=2.0,
         deferred=True
         )
  
       f2.start_at(f2.inner_state)
       f2.post_fifo(Event(signal=signals.Hook))
       f2.post_fifo(Event(signal=signals.Reset))
       f1.post_fifo(Event(signal=signals.Send_Broadcast))
  
       # delay long enough so we can see how the program behaves in time
       time.sleep(4.00)
  
       # read information from other threads
       print("f1 was in its inner state {} times".format(f1.times_in_inner))
       print("f2 was in its inner state {} times".format(f2.times_in_inner))
  
  Running this program will provide the following output:
  
  .. code-block:: python
    
    f1 was in its inner state 2 times
    f2 was in its inner state 0 times
  
  The f1 statechart properly reports how many times it was in its inner_state.
  The f2 inner_state doesn't write to the ``times_in_inner`` property, so it's
  output only shows how that property was initialized.
  
  Let's look at the property code in isolation from the rest of the statechart:
  
  .. code-block:: python
    :emphasize-lines: 1
    :linenos:
  
    # INITIALIZATION CODE TAKEN FROM __init__
    # set up a thread safe ring buffer of size 1
    self._times_in_inner = deque(maxlen=1)
    self._times_in_inner.append(0)
    # ...
    # PROPERTY methods used to control the deque
    @property
    def times_in_inner(self):
      return self._times_in_inner[-1]
  
    @times_in_inner.setter
    def times_in_inner(self, value):
      self._times_in_inner.append(value)
    # ...
    # CODE FROM WITHIN STATECHART using the property
    def inner_state_entry_signal(self, e):
      status = return_status.HANDLED
      self.times_in_inner += 1
      self.scribble(
        "hello from inner_state {}".format(self.times_in_inner))
      return status
    # ...
    # CODE OUTSIDE OF STATECHART accessing the property
    print("f1 was in its inner state {} times".format(f1.times_in_inner))
  
  The initialization code on lines 3-4 of this listing, creates a private deque
  ring-buffer which can hold one item, then pushes a zero into this queue.  Since
  our ``_time_in_inner`` deque is a ring buffer of size 1, when we ``append`` new
  information into it, it's old information is shifted out of the ring (deleted).
  
  We see this kind of ``append`` taking place in the ``times_in_inner`` setter
  method on lines 12 to 13.  The value is shifted into the deque and the old information
  is pushed out.  This is a thread safe activity; if more than one thread is
  accessing this method at once, they don't both get to perform the action at the
  same time.  One will get its turn, then the other will get its turn.
  
  The ``times_in_inner`` getter method described in lines 7-9 of the listing
  shows us how we can access our information from within or outside of our
  statechart's thread.  We only read the latest member of the deque.  Since our
  deque is of size one, there is only one thing to read in it anyway.
  
  We can see how this property is used within the statechart's thread on line 18.  The
  ``self.times_in_inner += 1`` calls the getter method 8-9, adds one to the result
  then calls the setter method (12-13) which appends the result into the deque,
  shifting the old information out.
  
  We can see how the ``times_in_inner`` property is accessed outside of the
  statechart thread on line 24.  The main thread accesses the getter method 8-9, and
  reports its returned value in a print statement.
  
  As of miros 4.1.3, you could create the same thread-safe-attribute like
  this:
  
  .. code-block:: python
  
     from miros import Factory
     # ...
     from miros import ThreadSafeAttributes
  
     class F1(Factory, ThreadSafeAttributes):
        _attribute = ['times_in_inner']
  
       def __init__(self, name, log_file_name=None,
           live_trace=None, live_spy=None):
         # ...
  
  The ThreadSafeAttributes class contains code which automatically makes the
  deque, initializes and wraps the deque within a property.  To build such
  attributes, we place the thread-safe-attribute names in a list and assign it to
  ``_attributes``, as seen above.  If you would like to read more about this,
  consider:
  
  * :ref:`Sharing attributes between threads (ActiveObjects) <recipes-sharing-attributes-between-threads-activeobjects>` 
  * :ref:`Sharing attributes between threads (Factories)<recipes-sharing-attributes-between-threads-factories>`

----

Here is a collection of tiny programs that each demonstrate how to do things in miros.

.. _recipes-states:

States
^^^^^^

.. contents:: 
   :local:

A lot of Python developers are moving away from using its object oriented
features and writing most of their code within functions which call each other.
This kind of programming is supported by miros.  You can build up your
statechart by constructing a set of state functions, attaching one of them to a
``miros.ActiveObject``, then using that active object as the thing to post
events to.  The functions and the active object work together to form a
statechart.  If you intend on porting your designs to the ``qp`` framework, I
recommend that you write your code this way.

You can also build a statechart directly within one class, by inheriting from
the ``miros.Factory``.  Within the ``__init__`` method of the derived class, you
describe the states, link signals to state methods then add hierarchy using
the ``nest`` method.

The state recipes will be broken down into two groups, state function recipes
and state method recipes.

.. _recipes-state-function-recipes:

State Function Recipes
----------------------

.. _recipes-boiler-plate-state-function-code:

Boiler-plate State Function Code
""""""""""""""""""""""""""""""""

.. code-block:: python

  from miros import Event
  from miros import spy_on
  from miros import signals
  from miros import return_status

  @spy_on
  def <your_state_method_name>(chart, e):
    # if your state method doesn't know what to do, it should return this
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
      # call your entry application code

      # make sure you tell the event processor you handled this event
      status = return_status.HANDLED
    elif e.signal == signals.INIT_SIGNAL:
      # call your initialization (big black dot) application code

      # make sure you tell the event processor you handled this event
      status = return_status.HANDLED

    #
    # Write your custom
    # event handlers in here as their own elif clauses
    #

    elif e.signal == signals.EXIT_SIGNAL:
      # call your exit application code

      # make sure you tell the event processor you handled this event
      status = return_status.HANDLED
    else:
      # this logic will run when your event processor sends an event with the
      # SEARCH_FOR_SUPER_SIGNAL name

      # 1) place your parent state method into the self.temp.fun
      # 1.1) if this is the top-most state, use ``chart.top`` as your
      #      <your_parent_state_method>
      chart.temp.fun = <your_parent_state_method>

      # 2) make sure you return this value
      status = return_status.SUPER
    # return the status value
    return status
    
If your state method didn't include handling for the ``ENTRY_SIGNAL``,
``INIT_SIGNAL`` or ``EXIT_SIGNAL``, the event processor will just assume it did
and returned return_state.HANDLED.

To see factory boiler plate go, see :ref:`this<recipes-creating-a-state-method-from-a-factory>`

.. _recipes-describing-your-parent-state-function:

Describing your Parent State Function
"""""""""""""""""""""""""""""""""""""
To describe your parent state:

1. setting the ``temp.fun`` attribute of the first argument to point at their
   parent state.
2. return the value of ``return_state.SUPER``

Generally speaking this is how it is done:

.. code-block:: python
  :emphasize-lines: 5,6

  def <state_method_name>(chart, e):
    # .
    # .
    else:
      status = return_status.SUPER
      chart.temp.fun = <parent_state_of_this_state_method>
    return status.

If you need to define your parent state as the outermost state of your diagram, you would
set the ``<parent_state_of_this_state_method>`` to the ``top`` attribute of the
first argument provided to your state method:

.. code-block:: python
  :emphasize-lines: 6

  def <state_method_name>(chart, e):
    # .
    # .
    else:
      status = return_status.SUPER
      chart.temp.fun = chart.top
    return status.

To read more about why you structure your state methods this way, read :ref:`this.<recipes-what-a-state-does-and-how-to-structure-it>`

To see how to define a parent state with a factory, read :ref:`this<recipes-factory-5>`

.. _recipes-passing-events-to-the-parent-state-function:

Passing events to the Parent State Function
"""""""""""""""""""""""""""""""""""""""""""

The easiest way to pass an event outward in your statechart is not to handle it
in your ``if-elif`` clauses and let your ``else``
:ref:`clause<recipes-describe-a-parent-state>` handle it.

.. code-block:: python

  # Sending Event(signal=signals.B) to c1 would cause
  # the parent state c to be called with this event,
  # since it is not handled in the ``if-elif``
  # logic structure or c1.
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = trans(c2)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

Another way to pass an event out to your parent state is to handle the event in
the ``if-elif`` clause, then return ``return_status.UNHANDLED`` to the event
processor.  When it sees that your state method couldn't handle the event it
will call it again to find it's parent state and then call that parent state
method with the event that you want to trickle outward in your diagram.

.. code-block:: python
  :emphasize-lines: 12

  # Sending Event(signal=signals.B) to c1 would cause
  # the parent state c to be called with this event,
  # since c1 returns a `UNHANDLED` value to the event
  # processor
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.B):
      print("saw signal B, but letting it trickle through to my parent")
    elif(e.signal == signals.A):
      status = trans(c2)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

.. _recipes-transition-to-another-state-function:

Transition to another State Function
""""""""""""""""""""""""""""""""""""
To transition to another state, use the ``trans`` method:

.. code-block:: python
  :emphasize-lines: 8,9

  # Sending Event(signal=signals.A) will cause a transition to c2
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = trans(c2)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

Make sure that you return the result of the call to your ``trans`` method, or
the event processor will break.

.. _recipes-state-function-entry-code:

State Function Entry Code
"""""""""""""""""""""""""
To have your application code run when a state is entered place it in the
``ENTRY_SIGNAL`` clause of your state's if-elif structure.  An entry event will
occur anytime the event processor detects a transition from the outside to the
inside of your state method's boundary.

.. code-block:: python
  :emphasize-lines: 4-6

  # Running application code when the state is entered
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("Running my entry application code here")
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

.. _recipes-state-function-initialization-code:

State Function Initialization Code
""""""""""""""""""""""""""""""""""
To have your application code run when a state is initialized place it in the
``INIT_SIGNAL`` clause of your state's if-elif structure.  An init event will
occur after the entry event, if a transition is moving from the outside to the
inside of your state method's boundary.  It will also occur if there is a
transition into this state from one of its child states.

.. code-block:: python
  :emphasize-lines: 6-9

  # Running application code when the state is initialized
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    # BIG BLACK DOT ON DIAGRAM
    elif(e.signal == signals.INIT_SIGNAL):
      print("Running my init application code here")
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

:NOTE:  If you only want to run initialization code and do not want your state
        to immediately transition into another state, make sure you return
        ``HANDLED`` after running your application code, otherwise your
        statechart will not behave properly.

The ``INIT_SIGNAL`` handler is often used as the place where your state can
immediately transition into another state.  To do this, just use the
:ref:`trans <recipes-transition-to-another-state>` method and return its result
from your state method call:

.. code-block:: python
  :emphasize-lines: 6-10

  # Running application code when the state is initialized
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    # BIG BLACK DOT ON DIAGRAM
    elif(e.signal == signals.INIT_SIGNAL):
      print("Running my init application code here")
      # now transition into the c2 state
      status = self.trans(c2)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

.. warning::
  If you use an init signal to transition out of your parent state an
  ``HsmTopologyException`` will be issued.  Init signals should only be used to
  run code with no transitions or to transition deeper into your statechart.
  If you absolutely need to leave a state after entering  you can post an
  :term:`artificial event<Artificial Event>` into the fifo/lifo.  This will
  cause this signal to be caught on the next :term:`rtc<Run To Completion>`
  process and your statechart will behave as you want it to (though, you should
  probably re-visit your design).


.. _recipes-state-function-exit-code:

State Function Exit Code
"""""""""""""""""""""""""
To have your application code run when a state is exited place it in the
``EXIT_SIGNAL`` clause of your state's if-elif structure.  An exit event will
occur anytime the event processor detects a transition from the inside to the
outside of of your state method's boundary.

.. code-block:: python
  :emphasize-lines: 8-10

  # Running application code when the state is entered
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      print("Running my exit application code here")
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.c
    return status

.. _recipes-creating-a-hook-in-a-state-function:

Creating a Hook in a State function
"""""""""""""""""""""""""""""""""""
A hook is some application code that is shared between your state method and
all of its child state method's.

Here we will create a hook in the c1 state, linking some application code to an
event with the signal name ``MY_HOOK``.

.. code-block:: python
  :emphasize-lines: 9-11

  # Sending Event(signal=signals.A) will cause a transition to c2
  def c1(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED

    elif(e.signal == signals.MY_HOOK):
      print("running the code defined in c1")
      status = return_status.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      self.temp.fun = self.top
    return status

Now we will make a child state.

.. code-block:: python

  # Create a child state of c1
  def c11(self, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      chart.temp.fun = self.c1
    return status

We will start up our state chart, in c11 and send the ``MY_HOOK`` event:

.. code-block:: python

  ao = ActiveObject()
  ao.start_at(c11)
  # run code in c1 from c11 by using a hook
  ao.post_fifo(Event(signal=signals.MY_HOOK)) 
    # => "running the code from defined in c1"
  # demonstrate the state didn't change
  assert(ao.state.fun.__name__ == 'c11')

In the above code we see evidence that our statechart ran some application code
contained in the parent state (``c1``) while it stayed within its child state
(``c11``).

The child state received an event called ``MY_HOOK`` which it didn't know what
to do with.  So the event processor searched the parent state and saw that there was a
handler for this event in ``c1``.  The ``MY_HOOK`` handler (the if-elif
clause) returned ``return_status.HANDLED``.  Upon seeing this value, the event
processor determined that no transition is needed and it stopped running.

.. image:: _static/hook1.svg
    :target: _static/hook1.pdf
    :align: center

In this way hook code is run in the search phase of the search-then-transition
part of the event processor algorithm.

The ``c1`` state method, "hooks" the ``MY_HOOK`` event, by capturing it, running
its application code and returning the ``HANDLED`` value.  It stops the
``MY_HOOK`` event from falling off the edge of the map and returns control to
the state that originally experienced the event.

.. _recipes-catch-and-release-in-a-state-function:

Catch and Release in a State function
"""""""""""""""""""""""""""""""""""""

The catch and release recipe is similar to the
:ref:`hook<recipes-create-a-hook>` recipe in that you are using the search phase
of the event processor algorithm to run your code.

Instead of hooking the code with an ``HANDLED`` response, your state method
returns an ``UNHANDLED`` status.  This causes the event processor, to query it
again to find its parent, then dispatch the event to that state method.

.. image:: _static/catchandrelease1.svg
    :target: _static/catchandrelease1.pdf
    :align: center

Here we create the state in the picture, notice that ``inner`` and ``middle``
do not return ``HANDLED`` when they see the ``BUBBLED`` signal.

.. code-block:: python
  :emphasize-lines: 3-5, 12-14, 21-23, 30, 37

  def outer(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BUBBLED):
      print("hooked by the outer state")
      status = return_status.HANDLED
    else:
      status = return_status.SUPER
      chart.temp.fun = chart.top
    return status

  def middle(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BUBBLED):
      print("processed in middle")
    else:
      status = return_status.SUPER
      chart.temp.fun = outer
    return status

  def inner(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BUBBLED):
      print("processed in inner")
    else:
      status = return_status.SUPER
      chart.temp.fun = outer
    return status

  ao = ActiveObject()
  ao.start_at(inner)
  # run each state's application code for the bubble event
  ao.post_fifo(Event(signal=signals.BUBBLED)) 
    # => "processed in inner"
    #    "processed in middle"
    #    "hooked by the outer state"
  # demonstrate the state didn't change
  assert(ao.state.fun.__name__ == 'inner')

.. _recipes-state-method-recipes:

State Method Recipes
--------------------
A statechart can be made using the ``miros.Factory`` class.  To see how to do
this :ref:`look here <recipes-making-a-statechart-from-a-class>`.

.. _recipes-boiler-plate-state-handler-method:

Boiler-plate State Method
"""""""""""""""""""""""""
A state method is constructed by using the ``create``, ``catch`` and ``to_method``
interface of the ``miros.Factory`` object.

Consider the outer_state of :ref:`this example <recipes-making-a-statechart-from-a-class>`:

.. image:: _static/state_recipe_10.svg
    :target: _static/state_recipe_10.pdf
    :align: center

Your outer_state state method code (highlighted) would look like this:

.. code-block:: python
  :emphasize-lines: 9-20
  
   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)
       # ..

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         catch(signal=signals.Reset,
           handler=self.outer_state_reset). \
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

      # ..

The ``self.outer_state`` method construction is started with a call to the
``miros.Factory`` ``create`` method.  Then the ``catch`` method is chained once
for every signal your state needs to handle.  The ``catch`` method requires a
signal and a reference to a method which will be called when an event of this
signal is passed to your state method. To end the chain, the ``to_method`` is
called, which converts the state into a state method.

The ``self.outer_state`` method does not describe it's parent, this is
done separately with the ``miros.Factory``'s ``nest`` interface.

.. _recipes-boiler-plate-state-handler-method:

Boiler-plate State Handler Method
"""""""""""""""""""""""""""""""""

When you use the ``miros.Factory`` to build a statechart, you assign one state
handler to each signal of the state.  This means that you can have multiple state
handlers per state.

A state method tends to have the following form:

.. code-block:: python
  
  def <name_of_state_name_of_event>(self, e):
    status = return_status.HANDLED
    # .. code to handle specific event
    return status

Here is an example of the outer_state method's entry event handler taken from
:ref:`this example <recipes-making-a-statechart-from-a-class>`:

.. code-block:: python

  def outer_state_entry_signal(self, e):
    self.scribble("hello from outer_state")
    status = return_status.HANDLED
    return status

.. _recipes-describing-your-parent-state-method:

Describing your Parent State using the Factory
""""""""""""""""""""""""""""""""""""""""""""""

A state method does not describe its parent state, this is done with the
``nest`` method which follows the state definition descriptions in the
``__init__`` of your derived factory class.

If we were to add the hierarchy information for the following design:

.. image:: _static/state_recipe_10.svg
    :target: _static/state_recipe_10.pdf
    :align: center

The code would look like this:

.. code-block:: python
  
  self.nest(self.outer_state, parent=None). \
    nest(self.inner_state, parent=self.outer_state)

To see the full example, reference: :ref:`making a statechart from a class <recipes-making-a-statechart-from-a-class>`.

.. _recipes-passing-events-to-the-parent-state-method:

Passing Events to the Parent State Method
"""""""""""""""""""""""""""""""""""""""""
By default a state method will pass an event outward to its super state if it is
not handled by any of its handlers.

.. _recipes-transition-to-another-state-method:

Transition to another State Method
""""""""""""""""""""""""""""""""""

To transition to another state, use the ``trans`` method:

.. code-block:: python
  
  def outer_state_init_signal(self, e):
    self.scribble("init")
    status = self.trans(self.middle_state)
    return status

To see the full example, reference: :ref:`making a statechart from a class
<recipes-making-a-statechart-from-a-class>`.

.. _recipes-state-method-entry-code:

State Handlers for Entry/Exit and Initialization Signals
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. image:: _static/state_recipe_10.svg
    :target: _static/state_recipe_10.pdf
    :align: center

We would create the outer_state and its entry/exit/initialization handlers
this way:

.. code-block:: python
  :emphasize-lines: 12-15, 17, 18, 23-27, 29-32, 34-37

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status
  
   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):
       # ...
       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         # ...
         catch(signal=signals.EXIT_SIGNAL,
           handler=self.outer_state_exit_signal). \
         to_method()

         # ...

     def outer_state_entry_signal(self, e):
       self.subscribe(Event(signal=signals.BROADCAST))
       self.scribble("hello from outer_state")
       status = return_status.HANDLED
       return status

     def outer_state_init_signal(self, e):
       self.scribble("init")
       status = self.trans(self.middle_state)
       return status

     def outer_state_exit_signal(self, e):
       status = return_status.HANDLED
       self.scribble("exiting the outer_state")
       return status

To see the full example, reference: :ref:`making a statechart from a class
<recipes-making-a-statechart-from-a-class>`.

.. _recipes-creating-a-hook-in-a-state-method:

Creating a Hook in a State Handler
""""""""""""""""""""""""""""""""""

.. image:: _static/state_recipe_10.svg
    :target: _static/state_recipe_10.pdf
    :align: center

We would create the outer_state and its Hook handlers this way:

.. code-block:: python
  :emphasize-lines: 11-12, 18-20
  
   class FactoryInstrumentationToLog(Factory):

     def __init__(self, name, log_file_name=None,
         live_trace=None, live_spy=None):

       super().__init__(name)
       # ..

       self.outer_state = self.create(state="outer_state"). \
         # ..
         catch(signal=signals.Hook,
           handler=self.outer_state_hook). \
         # ..
         to_method()

      # ..

     def outer_state_hook(self, e):
       self.scribble("run some code, but don't transition")
       return return_status.HANDLED


To see the full example, reference: :ref:`making a statechart from a class
<recipes-making-a-statechart-from-a-class>`.

.. _recipes-events-and-signals:

Events And Signals
^^^^^^^^^^^^^^^^^^

* :ref:`Subscribing to an event posted by another Activeobject and Factories<recipes-subscribing-to-an-event-posted-by-another-active-object>`
* :ref:`Publishing events to other Activeobjects and Factories<recipes-publishing-event-to-other-active-objects>`

.. _recipes-creating-an-event:

Creating an Event
-----------------
An event is something that will be passed into your statechart, it will be
reacted to, then removed from memory.

.. code-block:: python

  from miros import Event
  from miros import signals

  event_1 = Event(signal="name_of_signal")
  # or 
  event_2 = Event(signal=signals.name_of_signal)

.. _recipes-creating-a-signal:

Creating a Signal
-----------------
A signal is the name of an event.  Many different events can have the same
name, or signal.  When a signal is created, it is given a number which is one
higher than the oldest signal that was within your program.  You shouldn't have
to worry about what a signal number is, they are only used to speed up the
event processor. (it is faster to compare two numbers than two strings)

When you create a signal it will not be removed from memory until your program
finishes.  They are created at the moment they are referenced, so you don't
have to explicitly define them.

.. code-block:: python
  :emphasize-lines: 6

  from miros import Event
  from miros import signals
  
  # signal named "name_of_signaL" invented
  # here and given a unique number
  event_1 = Event(signal="name_of_signal")
  # the signal number of this event will have
  # the same number as in line 6
  event_2 = Event(signal=signals.name_of_signal)

Notice that the signal was invented on line **6** then re-used on line **9**.

The signals are shared across your whole program.  To see reflect upon your
signals read :ref:`this<recipes_seeing_your_signals>`.


.. _posting_events:

Posting Events
--------------
The Active Object ``post_fifo``, ``post_lifo``, ``defer`` and ``recall``
methods are use to feed events to the statechart.  An Event can be thought of
as a kind of named marble that is placed onto a topological map.  If a
particular elevation doesn't know what to do with the marble, it rolls the
marble to the next lower elevation, or state.  If the lowest elevation is
reached and the program doesn't know what to do, it just ignores the event, or
lets the marble fall out of play.

The name of the marble is the signal name. An event can have a payload, but it
doesn't have to.  An event can only be posted to a chart after the chart has
started.  Otherwise the behavior of the active object is undefined.

The state methods typically react to the names of a event, or the signal names.
This means that the if-else structures that you write will use the signal names
in their logic.

If you use the chart's post event methods within the chart, the chart will not
concern itself with *where* you initiated that event.  It will post its events
into its queue as if they were provided by the outside world.  In this way
these events are called *artificial*; instead of the world creating the event,
the chart does.  There are a number of situations where it makes sense to do
this, they will be described in the patterns section.

.. _recipes-posting-an-event-to-the-fifo:

Posting an Event to the Fifo
----------------------------
To post an event to the active object first-in-first-out (fifo) buffer, you
must have first started your statechart.  Here is a simple example:

.. code-block:: python

  ao = ActiveObject()
  # start at 'outer' for the sake of our example
  ao.start_at(outer)

  # Send an event with the signal name 'mary'
  ao.post_fifo(Event(signal=signals.mary))

The signal names used by the events are common across the entire system.  You
do not need to declare them.  If the system had not seen the ``signals.mary``
signal code before in our above example, this name would be added and assigned
a unique number automatically.

.. _recipes-posting-an-event-to-the-lifo:

Posting an Event to the LIFO
----------------------------

To post an event to the active object last-in-first-out (lifo) buffer, you
must have first started your statechart.  Here is a simple example:

.. code-block:: python

  ao = ActiveObject()
  # start at 'outer' for the sake of our example
  ao.start_at(outer)

  # Now say we want to send an event with
  # th the signal name of 'mary' to the chart
  ao.post_lifo(Event(signal=signals.mary))

You would post to the 'lifo' buffer if you needed your event to be moved to the
front of the active object's collection of unprocessed events.  You might want
to do this with a timing heart beat or for any event that needs to be processed
with a greater priority than other events.

.. _recipes-create-a-guard:

Create a Guard
--------------
There will be situations where you only would like an event to cause a
transition between two states if a condition is true.  This is called a guard,
in UML it looks like this:

.. image:: _static/guard.svg
    :target: _static/guard.pdf
    :align: center

The logic between the square brackets must be true for this event to work.  In
this case the ``T`` event is guarded, it can only cause a transition if the the
function ``g()`` returns ``True``, otherwise nothing will happen.

The ``t()`` function is a function that runs if the ``g()`` returns True.

To implement a guard in your state method is very straight forward, you use an
if statement:

.. code-block:: python
  :emphasize-lines: 2

  elif(e.signal == signals.T):
    if g():
      t()
      chart.trans(<state_to_transition_to)

The highlighted code is the guard.

To learn more about guards read the
:ref:`hacking to learn example.<scribbleexample-hacking-to-learn-the-deeper-dynamics>`

.. _recipes-creating-a-one-shot-event:

Creating a One-Shot Event
-------------------------

.. include:: i_create_a_one_shot.rst 

.. _recipes-creating-a-multishot-event:

Creating a Multishot Event
--------------------------
.. include:: i_create_a_multishot.rst

Canceling a Specific Event Source
---------------------------------
The requests to the ``post_fifo`` and ``post_lifo`` methods, where ``times`` are
specified, can be thought of as event sources.  This is because they create
background threads which track time and periodically post events to the active
object.

There are two different ways to cancel event sources.  You can cancel a
specific event source, or you can cancel all event sources that create a
specific signal name (easier).  Read the
:ref:`recipes-cancelling-event-source-by-signal-name` recipe to see how to do
this.

To cancel a specific signal source, you need to track the thread id which was
created when it was made, then use that id to cancel the event.  Since a state
method can be used by many different active objects, you don't want to store
this id on the method itself, or in its variable name space.  Instead, you can
markup the name of the chart that is using the method, this ``chart`` object is
passed to the state method as the first argument.


.. code-block:: python

    # Here define a middle state the creates a multi-shot event called
    # three_pulse.  The same three_pulse signal is captured
    # by the middle state and used to transition into the inner state
    #
    # We want to cancel this specific event source when we are exiting this
    # state
    @spy_on
    def middle(chart, e):
      status = state.UNHANDLED
      if(e.signal == signals.ENTRY_SIGNAL):
        multi_shot_thread = \
          chart.post_fifo(Event(signal=signals.three_pulse),
                          times=3,
                          period=1.0,
                          deferred=True)
        # We graffiti the provided chart object with this id
        chart.augment(other=multi_shot_thread,
                      name='multi_shot_thread')
        status = state.HANDLED

      elif(e.signal == signals.EXIT_SIGNAL):
        chart.cancel_event(chart.multi_shot_thread)

        # remove our graffiti
        del(chart.multi_shot_thread)
        status = state.HANDLED

      if(e.signal == signals.INIT_SIGNAL):
        status = state.HANDLED
      elif(e.signal == signals.three_pulse):
        status = chart.trans(inner)
      else:
        status, chart.temp.fun = state.SUPER, outer
      return status

The ``augment`` api is used to graffiti our chart upon entering the state.
We write the event-source id onto the ``multi_shot_thread`` chart attribute,
so that we can use it later.  By marking this specific ``chart`` object, the
middle state method handler can be shared by other active objects.

You would use this method of canceling an event source if you need the
three_pulse signal name elsewhere in your statechart.  If you do not intend on
re-using this signal name you can just cancel event sources using a much
simpler api: the ``cancel_event``.

.. _recipes-cancelling-event-source-by-signal-name:

Canceling Event Source By Signal Name
-------------------------------------
If you would like to re-use your event source signal names through your chart,
then you can use the :ref:`recipes-cancelling-a-specific-event-source` recipe
to cancel a specific source and leave your other event sources running.
Otherwise, you can use the simpler ``cancel_sources`` api provided by the
Active Object:

.. code-block:: python

    # Here we define a middle state the creates a multi-shot event called
    # three_pulse.  The same three_pulse signal is captured
    # by the middle state and used to transition into the inner state
    #
    # We want to cancel this specific event source when we are exiting this
    # state
    @spy_on
    def middle(chart, e):
      status = state.UNHANDLED
      if(e.signal == signals.ENTRY_SIGNAL):
        chart.post_fifo(Event(signal=signals.three_pulse),
                        times=3,
                        period=1.0,
                        deferred=True)
        status = state.HANDLED

      elif(e.signal == signals.EXIT_SIGNAL):
        # cancel all event sources with the signal named three_pulses
        chart.cancel_events(Event(signal=signals.three_pulse))
        status = state.HANDLED

      if(e.signal == signals.INIT_SIGNAL):
        status = state.HANDLED
      elif(e.signal == signals.three_pulse):
        status = chart.trans(inner)
      else:
        status, chart.temp.fun = state.SUPER, outer
      return status

There is no need to keep a thread id for the event source, since the Active
Object can just look at all of the event source threads and kill any of them
that have this signal name provided to the ``cancel_events`` call.

.. _recipes-deferring-an-event:

Deferring and Recalling an Event
--------------------------------

.. include:: i_defer_and_recall.rst 

.. _recipes-adding-a-payload-to-an-event:

Adding a Payload to an Event
-----------------------------
To add a payload to your event:

.. code-block:: python

  e = Event(signal=signals.YOUR_SIGNAL_NAME, payload="My Payload")

If you are creating a payload that will be shared across statecharts put it
within an immutable object like a namedtuple before you send it out.  Then draw
the named tuple onto your diagrams, because the structure of the payload will
become extremely important when you are trying to understand your design later.

.. note::

  We want to use an immutable object when sharing data between threads to avoid
  nasty multi-threading bugs.  If you can't change the object in two different
  locations at the same time, then you can't accidently create this kind of bug.

Here is an example of a payload picture, taken from the miros-random project:

.. image:: _static/named_tuple_payload.svg
    :target: _static/named_tuple_payload.pdf
    :align: center

You can see, it's just the code used to make it, placed within a UML note.

Here is the code to make this payload's class:

.. code-block:: python
 
  # collections are in the Python standard library
  from collections import namedtuple

  # create a structured immutable object that has useful names related
  # to your problem
  PioneerRequestSpec = namedtuple(
    'PioneerRequestSpec', ['cells_per_generation', 'deque_depth')

Here is how you would create an event with this payload class:

.. code-block:: python
  
  # There is often a relationship between your signal names and your payload
  # name
  e = Event(signal=signals.PioneerRequest,
        payload=PioneerRequestSpec(
          cells_per_generation=45,
          queue_depth=11)

Here is how you would access the payload elsewhere in your design:

.. code-block:: python
  
  # to get access to the payload information when you receive this event in one
  # of your event handlers:
  e.payload.cells_per_generation  # => 45
  e.payload.queue_depth  # => 11

I would recommend that you always place your payloads in immutable objects,
even if you aren't intending to share them between statecharts.

.. _recipes-determining-if-an-event-has-a-payload:

Determining if an Event Has a Payload
-------------------------------------
To determine if an event has a payload:

.. code-block:: python

  e1 = Event(signal=signals.YOUR_SIGNAL_NAME, event="My Payload")
  e2 = Event(signal=signals.YOUR_SIGNAL_NAME)

  assert(e1.has_payload() == True)
  assert(e2.has_payload() == False)


.. _recipes-subscribing-to-an-event-posted-by-another-active-object:

Subscribing to an Event Posted by Another Active Object
-------------------------------------------------------
Your active object can subscribe to the events published by other active objects:

.. code-block:: python
  
  subscribing_ao = ActiveObject()
  subscribing_ao.subscribe(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT))

An active object can set how the ActiveFabric (the infrastructure connecting all
of your statecharts together) posts events to it.  If it would like a message to
take priority over all other events waiting to be managed, you would use the
``lifo`` technique:

.. code-block:: python

  subscribing_ao = ActiveObject()
  subscribing_ao.subscribe(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT),
    queue_type='lifo')

This approach would make sense if you were subscribed to a timed heart beat
being sent out by another active object, or if this event was some sort of
safety related thing.

In most situations you can use the subscription defaults:

.. code-block:: python

  subscribing_ao = ActiveObject()
  subscribing_ao.subscribe(signals.THING_SUBSCRIBING_AO_CARES_ABOUT)
  # which is the same as writing
  subscribing_ao.subscribe(
    signals.THING_SUBSCRIBING_AO_CARES_ABOUT, queue_type='fifo')

It may seem a little bit strange to subscribe to an event, since an event is a
specific thing, which contains a general thing; the signal.  But the ``subscribe``
method supports subscribing to events so that it's method signature looks like
the other method signatures in the library.  (Less things for you to remember)

If you chose to subscribe to events and not directly to signals, think of your
call as saying, "I would like to subscribe to this type of event".

.. code-block:: python

  # subscribing to a `type` of event
  subscribing_ao.subscribe(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT),
    queue_type='fifo')

.. _recipes-publishing-event-to-other-active-objects:

Publishing events to other Active Objects
-----------------------------------------
Your active object can send data to other active objects in the system by
publishing events.  

But your active object can only control *how it talks to others*, not *who
listens to it*; so, if another active object wants to receive a published event
it must subscribe to it first.

If you would like to publish data that will be used by another ActiveObject,
copy your data into some sort of immutable object before you publish it:
namedtuple objects are perfect for these situations:

.. code-block:: python

  from collections import namedtuple

  # draw these payloads on your statechart diagram
  MyPayload = namedtuple('MyPayload', ['name_of_item_1', 'name_of_item2'])

  publishing_ao = ActiveObect()

  # This is how you can send an 'THING_SUBSCRIBING_AO_CARES_ABOUT' event
  # to anything that has subscribed to it
  publishing_ao.publish(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT,
      payload=MyPayload(
        name_of_item_1='something',
        name_of_item_2='something_else'
      )
    )
  )

Here is how to publish an event with a specific priority:

.. code-block:: python

  publishing_ao = ActiveObect()
  publishing_ao.publish(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT))

  # or you can set the priority (1 is the highest priority see note):
  publishing_ao.publish(
    Event(signal=signals.THING_SUBSCRIBING_AO_CARES_ABOUT),
    priority=1)

.. note::
  
   The priority numbering scheme is counter-intuitive: low numbers mean high
   priority while high numbers mean low priority.  The highest published event
   priority is 1.  By default all published events are given a priority of 1000.
   If two events have the same priority the queue will behave like a first in
   first out queue.
.. _recipes-activeobjects-and-factories:

ActiveObjects
^^^^^^^^^^^^^
To build a statechart, you can create an ``ActiveObject`` and connect it to one of
your state functions using the ``start_at`` method.  Together, the
``ActiveObject`` and the state functions work as a statechart.

.. contents::
  :local:

.. _recipes-starting-an-activeojbect-or-factory:

Starting an ActiveObject
------------------------
Once you have created an Activeobject you can start its statemachine and thread
with its ``start_at`` method.

There is a set of queues and threads which connect *all of your ActiveObjects
together* (the ActiveFabric), if it hasn't been started yet, the ``start_at``
method will turn on this infrastructure as well.

Here is a simple example:

.. image:: _static/start_at.svg
    :target: _static/start_at.pdf
    :align: center

The ``start_at`` method can start the statechart in any of its states.

Here is the code:

.. code-block:: python
  :emphasize-lines: 47

  import time
  from miros import spy_on
  from miros import ActiveObject
  from miros import signals, Event, return_status

  @spy_on
  def c(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
      print("c1 entered")
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(c1)
    elif(e.signal == signals.B):
      status = chart.trans(c)
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def c1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c2)
    else:
      chart.temp.fun = c
      status = return_status.SUPER
    return status

  @spy_on
  def c2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("c2 entered")
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      chart.temp.fun = c
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    ao = ActiveObject('start_example')
    print("calling: start_at(c2)")
    ao.start_at(c2)

    time.sleep(0.2)
    print(ao.trace()) # print what happened from the start_at call
    ao.clear_trace()  # clear our instrumentation

    print("sending B, then A, then A:")
    ao.post_fifo(Event(signal=signals.B))
    ao.post_fifo(Event(signal=signals.A))
    ao.post_fifo(Event(signal=signals.A))
    time.sleep(0.2)
    print(ao.trace()) # print what happened

When we run this code we will see this result:

.. code-block:: python
 
   calling: start_at(c2)
   c1 entered
   c2 entered
   [2019-06-21 06:05:36.234137] [start_example] e->start_at() top->c2

   sending B, then A, then A
   c1 entered
   c2 entered
   [2019-06-21 06:05:36.435853] [start_example] e->B() c2->c1
   [2019-06-21 06:05:36.436074] [start_example] e->A() c1->c2
   [2019-06-21 06:05:36.436228] [start_example] e->A() c2->c1


.. _recipes-stopping-an-activeobject-or-factory:

Stopping an ActiveObject
------------------------
If you would like to stop an ``ActiveObject`` you can use its ``stop`` method.

This will stop its thread, and it will stop all of that ``ActiveObject``'s slave
threads (constructed by the post_fifo or post_lifo heartbeat constructors).  The
``stop`` method sets the ``ActiveObject``'s ActiveFabric-facing queue to None, so that
the ActiveFabric will not post items to it anymore.

.. note::
     
   Calling the ``stop`` method will not stop the ActiveFabric.  But the
   ActiveFabric, like all threads in miros, is a daemonic thread, so it will stop
   running when your program has stopped running.

.. _recipes-markup-your-event-processor:

Augmentng your ActiveObject
---------------------------

It is a bad idea to add variables to the state methods, instead augment your
active objects using the ``augment`` command.

.. code-block:: python
  
  chart = ActiveObect()
  chart.augment(other=0, name='counter')
  assert(chart.counter == 0)

.. note::
    
   An even better idea would be to include the attributes in a subclass of an
   Activeobject or Factory.

.. _recipes-sharing-attributes-between-threads-activeobjects:

..
  Sharing Attributes between Threads (ActiveObjects)
  --------------------------------------------------
  As of miros version v4.1.3, you can create thread safe attributes in your
  derived ``ActiveObect`` class by also inheriting the ``ThreadSafeAttributes``.
  
  To create one or more thread safe attribute, you add them to the list defined
  ``_attributes``:
    
  .. code-block:: python
    :emphasize-lines: 8, 10, 19-20, 24, 35, 40, 51, 56, 68-69, 72
    :linenos:
    
    from miros import Event
    from miros import spy_on
    from miros import signals
    from miros import ActiveObject
    from miros import return_status
    from miros import ThreadSafeAttributes
    
    class ThreadSafeAttributesInActiveObject(ThreadSafeAttributes, ActiveObject):
  
      _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']
  
      def __init__(self, name):
        super().__init__(name)
  
     @spy_on
     def c(chart, e):
       status = return_status.UNHANDLED
       if(e.signal == signals.ENTRY_SIGNAL):
         chart.thread_safe_attr_1 = False
         chart.thread_safe_attr_2 = False
       elif(e.signal == signals.INIT_SIGNAL):
         status = chart.trans(c1)
       elif(e.signal == signals.B):
         chart.thread_safe_attr_1 = True
         status = chart.trans(c)
       else:
         chart.temp.fun = chart.top
         status = return_status.SUPER
       return status
  
     @spy_on
     def c1(chart, e):
       status = return_status.UNHANDLED
       if(e.signal == signals.ENTRY_SIGNAL):
         chart.thread_safe_attr_1 = True
         status = return_status.HANDLED
       elif(e.signal == signals.A):
         status = chart.trans(c2)
       elif(e.signal == signals.EXIT_SIGNAL):
         chart.thread_safe_attr_1 = False
         status = return_status.HANDLED
       else:
         chart.temp.fun = c
         status = return_status.SUPER
       return status
  
     @spy_on
     def c2(chart, e):
       status = return_status.UNHANDLED
       if(e.signal == signals.ENTRY_SIGNAL):
         chart.thread_safe_attr_2 = True
         status = return_status.HANDLED
       elif(e.signal == signals.A):
         status = chart.trans(c1)
       elif(e.signal == signals.EXIT_SIGNAL):
         chart.thread_safe_attr_2 = False
         status = return_status.HANDLED
       else:
         chart.temp.fun = c
         status = return_status.SUPER
       return status
     
     if __name__ == '__main__':
        ao = ThreadSafeAttributesInActiveObject("ao")
        ao.start_at(c)
        # Change the ActiveObject's attributes while it is starting it's thread
        # and starting its statemachine
        ao.thread_safe_attr_1 = True
        ao.thread_safe_attr_2 = False
        ao.post_fifo(Event(signal=signals.A)
        # Main thread can access attribute used by the ActiveObject's thread
        print(ao.thread_safe_attr_2)



Factories
^^^^^^^^^
You can build a statechart within a class by using the ``miros.Factory`` class.
The ``miros.Factory`` lets you build state methods, state handlers and start the
chart in whichever state you need.

.. _recipes-creating-a-statechart-inside-of-a-class:

Creating a Statechart Inside of a Class
---------------------------------------
You can create a class that has a statechart within it.  Here are some of the benefits
of programming this way:

   * it is easy to draw using a mixture of class and statechart UML
   * state names can be re-used in the same file
   * provides a clear synchronous interface (methods)
   * provides a clear asynchronous interface (post_fifo/post_lifo/publish/subscribe)
   * packages all of your states, transitions and starting code within a single
     location in your file, within its class.
   * the start_at code is held within the class's ``__init__`` method
   * hides the state complexity from the rest of your code base
   * effortlessly provides multi-threading without its dangers
   * complicated ``else`` clauses in state callback handlers are avoided
   * it is trivial for main to inject asynchronous information
   * it is not hard for main to :ref:`extract asynchronous information<recipes-getting-information-from-your-statecchart>`
   * it is easy to build lots of these different kinds of objects and have them work as a
     federation. (systems programming)
   * it is easy to document federations (systems design)
   * it is not hard to network your federations with other federations across
     the internet (`systems of systems: miros-rabbitmq <https://aleph2c.github.io/miros-rabbitmq/index.html>`_)

To program this way we use the :ref:`Factory <recipes-creating-a-state-method-from-a-factory>` class from miros.

Here is a simple example of a statechart within an object:

.. image:: _static/factory_in_class_simple.svg
    :target: _static/factory_in_class_simple.pdf
    :align: center

Familiar stuff first:  The ``ClassWithStatechartInIt`` inherits from
``Factory``, it has three attributes and two methods.

The ``ClassWithStatechartInIt`` also has an asynchronous statechart (blue),
which is attached to an event processor, and it starts in the
``common_behaviors`` state.

Let's bring this design to life with some code (we will highlight the
asynchronous aspects of the program):

.. code-block:: python
  :emphasize-lines: 57, 63-66, 68-73, 75-80, 82-85, 87-92, 94-97, 99-102, 104-109, 111-116, 118-119, 121-122

  import time

  from miros import Event
  from miros import signals
  from miros import Factory
  from miros import return_status

  class ClassWithStatechartInIt(Factory):
    Default_Name = 'default_name'
    def __init__(self, name=None, live_trace=None, live_spy=None):
      # call the Factory ctor
      super().__init__(
        ClassWithStatechartInIt.Default_Name if name == None else name
      )
      # determine how this object will be instrumented
      self.live_spy = False if live_spy == None else live_spy
      self.live_trace = False if live_trace == None else live_trace
      
      # define our states and their statehandlers
      self.common_behaviors = self.create(state="common_behaviors"). \
        catch(signal=signals.INIT_SIGNAL,
          handler=self.common_behaviors_init). \
        catch(signal=signals.hook_1,
          handler=self.common_behaviors_hook_1). \
        catch(signal=signals.hook_2,
          handler=self.common_behaviors_hook_2). \
        catch(signal=signals.reset,
          handler=self.common_behaviors_reset). \
        to_method()

      self.a1 = self.create(state="a1"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.a1_entry). \
        catch(signal=signals.to_b1,
          handler=self.a1_to_b1). \
        to_method()

      self.b1 = self.create(state="b1"). \
        catch(signal=signals.INIT_SIGNAL,
          handler=self.b1_init). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.b1_entry). \
        catch(signal=signals.EXIT_SIGNAL,
          handler=self.b1_exit). \
        to_method()

      self.b11 = self.create(state="b11"). \
        to_method()

      # nest our states within other states
      self.nest(self.common_behaviors, parent=None). \
          nest(self.a1, parent=self.common_behaviors). \
          nest(self.b1, parent=self.common_behaviors). \
          nest(self.b11, parent=self.b1)

      # start our statechart, which will start its thread
      self.start_at(self.common_behaviors)

      # let the internal statechart initialize before you give back control
      # to the synchronous part of your program
      time.sleep(0.001)

    @staticmethod
    def common_behaviors_init(chart, e):
      status = chart.trans(chart.a1)
      return status

    @staticmethod
    def common_behaviors_hook_1(chart, e):
      status = return_status.HANDLED
      # call the ClassWithStatechartInIt work2 method
      chart.worker1()
      return status

    @staticmethod
    def common_behaviors_hook_2(chart, e):
      status = return_status.HANDLED
      # call the ClassWithStatechartInIt work2 method
      chart.worker2()
      return status

    @staticmethod
    def common_behaviors_reset(chart, e):
      status = chart.trans(chart.common_behaviors)
      return status

    @staticmethod
    def a1_entry(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves
      chart.post_fifo(Event(signal=signals.to_b1))
      return status

    @staticmethod
    def a1_to_b1(chart, e):
      status = chart.trans(chart.b1)
      return status

    @staticmethod
    def b1_init(chart, e):
      status = return_status.HANDLED
      return status

    @staticmethod
    def b1_entry(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves
      chart.post_fifo(Event(signal=signals.hook_1))
      return status

    @staticmethod
    def b1_exit(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves
      chart.post_fifo(Event(signal=signals.hook_2))
      return status

    def worker1(self):
      print('worker1 called')

    def worker2(self):
      print('worker2 called')

  if __name__ == '__main__':
    chart = ClassWithStatechartInIt(name='chart', live_trace=True)
    chart.post_fifo(Event(signal=signals.reset))
    time.sleep(1)

This will result in the following output:

.. code-block:: python

   [2019-06-19 06:16:02.662672] [chart] e->start_at() top->a1
   [2019-06-19 06:16:02.662869] [chart] e->to_b1() a1->b1
   worker1 called
   [2019-06-19 06:16:02.664588] [chart] e->reset() b1->a1
   worker2 called
   [2019-06-19 06:16:02.665011] [chart] e->to_b1() a1->b1
   worker1 called

Here is something a bit weirder, a concurrent statechart:

.. image:: _static/factory_in_class.svg
    :target: _static/factory_in_class.pdf
    :align: center

Above we define a class that contains a statechart that subscribes to, and
publishes events to other statecharts.  The class will be used to create three
objects which will message each other.

Upon starting, there is a 2/5 chance the statechart within
``ClassWithStatechartInIt`` will end up within ``b11`` state.  If a chart ends
up in this state, it will publish the ``OTHER_INNER_MOST`` signal to any chart
that has subscribed to the signal_name.

The chart sending the ``OTHER_INNER_MOST`` event ignores it, and all other
charts will respond by re-entering their ``common_behaviors`` state if they are
not in the ``b11`` state.

.. note::

  The red and green dots are not UML.  They are markers that act to highlight
  the important parts of a concurrent statechart design.
  
  I put the red dot on the part of the chart that is publishing an
  event.  It is red because once an item is published, it is put in a queue and the
  message flows stops momentarily.

  I put the green dot beside events that have been subscribed to and have been
  posted to the chart.  They are green, because they have been extracted from a
  queue by a thread and are being posted to the event processor attached to the
  chart.

We will make three of these charts, turn on some instrumentation, run them in
parallel and see what happens.

Here is the code (asynchronous parts highlighted):

.. code-block:: python
  :emphasize-lines: 67, 73-76, 78-82, 84-89, 91-96, 98-101, 103-106, 108-114, 116-119, 121-124, 126-131, 133-138, 140-144, 146-150, 152-155, 157-158, 160-161

  import time
  import random

  from miros import Event
  from miros import signals
  from miros import Factory
  from miros import return_status

  class ClassWithStatechartInIt(Factory):
    def __init__(self, name, live_trace=None, live_spy=None):

      # call the Factory ctor
      super().__init__(name)

      # determine how this object will be instrumented
      self.live_spy = False if live_spy == None else live_spy
      self.live_trace = False if live_trace == None else live_trace
      
      # define our states and their statehandlers
      self.common_behaviors = self.create(state="common_behaviors"). \
        catch(signal=signals.INIT_SIGNAL,
          handler=self.common_behaviors_init). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.common_behaviors_entry). \
        catch(signal=signals.hook_1,
          handler=self.common_behaviors_hook_1). \
        catch(signal=signals.hook_2,
          handler=self.common_behaviors_hook_2). \
        catch(signal=signals.reset,
          handler=self.common_behaviors_reset). \
        catch(signal=signals.OTHER_INNER_MOST,
          handler=self.common_behaviors_other_inner_most). \
        to_method()

      self.a1 = self.create(state="a1"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.a1_entry). \
        catch(signal=signals.to_b1,
          handler=self.a1_to_b1). \
        to_method()

      self.b1 = self.create(state="b1"). \
        catch(signal=signals.INIT_SIGNAL,
          handler=self.b1_init). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.b1_entry). \
        catch(signal=signals.EXIT_SIGNAL,
          handler=self.b1_exit). \
        to_method()

      self.b11 = self.create(state="b11"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.b11_entry). \
        catch(signal=signals.inner_most,
          handler=self.b11_inner_most). \
        catch(signal=signals.OTHER_INNER_MOST,
          handler=self.b11_other_inner_most). \
        to_method()

      # nest our states within other states
      self.nest(self.common_behaviors, parent=None). \
          nest(self.a1, parent=self.common_behaviors). \
          nest(self.b1, parent=self.common_behaviors). \
          nest(self.b11, parent=self.b1)

      # start our statechart, which will start its thread
      self.start_at(self.common_behaviors)

      # let the internal statechart initialize before you give back control
      # to the synchronous part of your program
      time.sleep(0.01)

    @staticmethod
    def common_behaviors_init(chart, e):
      status = chart.trans(chart.a1)
      return status

    @staticmethod
    def common_behaviors_entry(chart, e):
      status = return_status.HANDLED
      chart.subscribe(Event(signal=signals.OTHER_INNER_MOST))
      return status

    @staticmethod
    def common_behaviors_hook_1(chart, e):
      status = return_status.HANDLED
      # call the ClassWithStatechartInIt work2 method
      chart.worker1()
      return status

    @staticmethod
    def common_behaviors_hook_2(chart, e):
      status = return_status.HANDLED
      # call the ClassWithStatechartInIt work2 method
      chart.worker2()
      return status

    @staticmethod
    def common_behaviors_reset(chart, e):
      status = chart.trans(chart.common_behaviors)
      return status

    @staticmethod
    def common_behaviors_other_inner_most(chart, e):
      status = chart.trans(chart.b11)
      return status

    @staticmethod
    def a1_entry(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves 2/5 of the time
      if random.randint(1, 5) <= 3:
        chart.post_fifo(Event(signal=signals.to_b1))
      return status

    @staticmethod
    def a1_to_b1(chart, e):
      status = chart.trans(chart.b1)
      return status

    @staticmethod
    def b1_init(chart, e):
      status = chart.trans(chart.b11)
      return status

    @staticmethod
    def b1_entry(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves
      chart.post_fifo(Event(signal=signals.hook_1))
      return status

    @staticmethod
    def b1_exit(chart, e):
      status = return_status.HANDLED
      # post an event to ourselves
      chart.post_fifo(Event(signal=signals.hook_2))
      return status

    @staticmethod
    def b11_entry(chart, e):
      status = return_status.HANDLED
      chart.post_fifo(Event(signal=signals.inner_most))
      return status

    @staticmethod
    def b11_inner_most(chart, e):
      status = return_status.HANDLED
      chart.publish(Event(signal=signals.OTHER_INNER_MOST))
      return status

    @staticmethod
    def b11_other_inner_most(chart, e):
      status = return_status.HANDLED
      return status

    def worker1(self):
      print('{} worker1 called'.format(self.name))

    def worker2(self):
      print('{} worker2 called'.format(self.name))

  if __name__ == '__main__':
    chart1 = ClassWithStatechartInIt(name='chart1', live_trace=True)
    chart2 = ClassWithStatechartInIt(name='chart2', live_trace=True)
    chart3 = ClassWithStatechartInIt(name='chart3', live_trace=True)
    # send a reset event to chart1
    chart1.post_fifo(Event(signal=signals.reset))
    time.sleep(0.2)

There is a probabilistic aspect to this program, so it could behave differently
every time you run it.  Here is what I saw when I ran it for the first time:

.. code-block:: python
  
  [2019-06-19 12:03:17.949042] [chart1] e->start_at() top->a1
  [2019-06-19 12:03:17.949227] [chart1] e->to_b1() a1->b11
  chart1 worker1 called
  [2019-06-19 12:03:17.962356] [chart2] e->start_at() top->a1
  [2019-06-19 12:03:17.962482] [chart2] e->to_b1() a1->b11
  chart2 worker1 called
  [2019-06-19 12:03:17.975225] [chart3] e->start_at() top->a1
  [2019-06-19 12:03:17.985577] [chart1] e->reset() b11->a1
  chart1 worker2 called
  [2019-06-19 12:03:17.986041] [chart1] e->to_b1() a1->b11
  chart1 worker1 called
  [2019-06-19 12:03:17.986845] [chart3] e->OTHER_INNER_MOST() a1->b11
  chart3 worker1 called

The diagram describing this concurrent statechart is very compact and detailed,
but we may want an even smaller version which hides the specifics of how the
statechart behaves.

Typically class diagrams are suppose to describe the attributes and the
``messages`` (methods) which can be received by an object instantiated from the
class.  When you pack a statechart into a class, the idea of a message brakes
into two things: 

   * synchronous messages (methods), and
   * asynchronous messages (events)

The asynchronous messages should be more nuanced: broken into events intended
only for one statechart (using post_fifo/post_lifo) and events that are intended
to be published into other statecharts which have subscribed to their signal
names.

As far as I know there is no standard way of describing how to do this, so I'll
show you how I do it:

.. image:: _static/factory_in_class_compact.svg
    :target: _static/factory_in_class_compact.pdf
    :align: center

We see that the ``ClassWithStatechartInIt`` state inherits from the ``Factory``
and that it has three attributes: ``name``, ``live_spy`` and ``live_trace``.  It
has two methods, ``worker1`` and ``worker2``.

The rest of the diagram is non-standard:  I put an ``e`` in front of the
internal (e)vents from the chart, the ``to_b1`` and the ``reset`` then I mark the
asynchronous interface, by placing red and green dots on the compact form of a
state icon.  Then place the signal names beside arrows showing how they publish or
subscribe to these signal names.

UML isn't descriptive enough to actually capture a design's intention, so I
never hesitate to mark up a diagram with code.  In this case, my code is
saying, let's make three of these things and run them together.

As you become more experienced building statecharts that work in concert, you
will notice that you stop paying any attention to what attributes or methods a
specific class has.  You don't care about it's internal events and you don't
care about from what it was inherited.  You only care about what published
events it consumes and what events it publishes:

.. image:: _static/factory_in_class_compact_2.svg
    :target: _static/factory_in_class_compact_2.pdf
    :align: center

Then to draw a federation:

.. image:: _static/federation_drawing.svg
    :target: _static/federation_drawing.pdf
    :align: center


There is probably a much better way to do this, since it looks like three
classes are working together rather than three instantiated objects from the
same class.  UML really falls-over in describing object interactions.

If you have any suggestions about how to draw this better, email me.

.. _recipes-sharing-attributes-between-threads-factories:

..
  Sharing Attributes between Threads (Factories)
  ----------------------------------------------
  As of miros version v4.1.3, you can create thread safe attributes in your
  derived ``Factory`` class by inheriting from ``ThreadSafeAttributes``.
  
  To create one or more thread safe attribute, you add them to the list defined
  ``_attributes`` within the class body before the ``__init__`` method is defined.
  See below:
  
  .. code-block:: python
  
    from miros import Event
    from miros import signals
    from miros import Factory
    from miros import return_status
    from miros import ThreadSafeAttributes
  
    # By inheriting from ThreadSafeAttributes, you can define as many thread safe
    # attributes you need by assigning their names as strings to the
    # `_attributes` list.
    class Example2(Factory, ThreadSafeAttributes):
  
      _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']
  
    def __init__(self, name, live_trace=None, live_spy=None):
  
      super().__init__(name=name)
      self.thread_safe_attr_1 = True  # .. you can access this from main or other
                                      # threads in the same way
  
      # ... define states, link them to their signals
      # ... nesting code, etc.
  
      # statechart thread is created and started when `start_at` is called
      self.start_at(self.c)  # 

    # ... state methods defined here
  
    if __name__ == "__main__":
  
      statechart = Example2('example2')     # thread is started and is running
                                            # because `start_at` called within
                                            # the `__init__` method.
  
      print(statechart.thread_safe_attr_1)  # you can access the attribute which
                                            # is being used by the statechart's
                                            # thread, since it's wrapped
                                            # by a thread-safe datastructure
  
  
  By inheriting from the ``ThreadSafeAttributes`` class, we get access to the
  ``_attributes`` feature.  By assigning a list of strings to this ``_attributes``
  class attribute, a set of thread safe attributes are created an initialized in
  the background before the Example2 ``__init__`` method is called.
  
  In this example, we have created two thread safe attributes, which in reality
  are deque objects of size one, initialized with ``None``, wrapped within a class
  supporting the `descriptor protocal
  <https://docs.python.org/3/howto/descriptor.html>`_.  As a user of this feature,
  you don't have to care about these details, you can just access
  ``thread_safe_attr_1`` and ``thread_safe_attr_2`` as if they were regular
  attributes.  However, unlike other attributes, you *can safely use them* from
  inside or from outside the thread running your Factory derived statechart.
  
  To see a full example look `here
  <https://github.com/aleph2c/miros/blob/master/examples/thread_safe_attributes_in_factory.py>`_.

.. _recipes-multiple-statecharts:

Multiple Statecharts
^^^^^^^^^^^^^^^^^^^^
Break your design down into different interacting charts by using the
ActiveFabric.

The active fabric is a set of background tasks which act together to dispatch
events between the active objects in your system.

As a user of the software you wouldn't touch the active fabric directly, but
instead would use your active object's ``publish`` and ``subscribe`` methods.  The
active fabric has two different priority queues and two different tasks which
pend upon them.  One is for managing subscriptions in a first in first (fifo)
out manner, the other is for managing messages in a last in first out (lifo)
manner.  By having two different queues and two different tasks an active
object is given the option to subscribe to another active object's published
events, using one of two different strategies:

1.  If it subscribes to an event using the ``fifo`` strategy, the active fabric
    will post events to it using its :ref:`post_fifo<recipes-posting-an-event-to-the-fifo\>` method.
2.  If it subscribes in a ``lifo`` way it will post using the :ref:`post_lifo<recipes-posting-an-event-to-the-lifo>` method.

You can also set the priority of the event while it is in transit within the
active fabric.  This would only be useful if you are expecting contention
between various events being dispatched across your system.

.. _recipes-building-workers:

Building and Destroying Workers
-------------------------------
If you have a long running task that has to access blocking IO or connect to a
slow API, you can wrap it up into a worker.  Unlike stateless architectures,
with miros you can make your workers as complicated as you want, sending them
events as they sit or pend; change their behaviors in response to unexpected
things, or even have rich communications with them prior to having them destroy
themselves.

A worker can be thought of as some code sitting in a parallel thread, which will
do work, then post the results of this work back to their federation before they
prepare themselves for garbage collection.

.. _recipes-seeing-what-is-:

Seeing What is Going On
^^^^^^^^^^^^^^^^^^^^^^^

.. _recipes-determining-the-current-state:

Determining the Current State
-----------------------------

.. include:: i_determining_the_current_state.rst 

.. _recipes-seeing-what-signals-you-have-in-your-system:

Seeing what Signals You Have In Your System
-------------------------------------------

.. _recipes_seeing_your_signals:

.. include:: i_seeing_your_signals.rst 

.. _recipes-using-the-trace:

Using the Trace
---------------

.. include:: i_trace_reactive.rst

.. _recipes-using-the-spy:

Using the Spy
-------------

.. include:: i_spy_reactive.rst


.. _recipes-add-timing-information-to-the-spy:

Add Timing Information to the Spy
---------------------------------
The spy doesn't contain timing information, if you would like to mark it up
with time so that you can compare it with the trace output:

.. code-block:: python

  from datetime import datetime
  # .
  # .
  # In your state method or callback code write:
  chart.scribble("{} at {}". \
      format(e.signal_name, datetime.now().strftime("%M:%S:%f")))

.. _recipes-tracing-live:

Tracing Live
------------
There are situations where you would like to see what an active object is doing
while it is running.  Each active object has an attribute called
``live_trace``.  By setting this attribute to ``True`` the active object will
output it's trace information to the terminal while it reacts to events:

To turn on/off the live trace:

.. code-block:: python
  :emphasize-lines: 3,8

  ao1 = ActiveObject()
  # turn on the live trace
  ao1.live_trace = True
  # your code and state interactions here
  # live trace information will be displayed on the terminal

  # turn off the live trace
  ao1.live_trace = False

.. _recipes-spying-live:

Spying Live
-----------

There are situations where you would like to see what an active object is doing
while it is running.  Each active object has an attribute called
``live_spy``.  By setting this attribute to ``True`` the active object will
output it's spy information to the terminal while it reacts to events:

To turn on/off the live spy:

.. code-block:: python
  :emphasize-lines: 3,8

  ao1 = ActiveObject()
  # turn on the live spy
  ao1.live_spy = True
  # your code and state interactions here
  # live spy information will be displayed on the terminal

  # turn off the live spy
  ao1.live_spy = False

.. _recipes-scribble-on-the-spy:

Scribble On the Spy
-------------------

.. include:: i_scribble_on_the_spy.rst


.. _recipes-flatting-a-state-method:

Flatting a State Method
-----------------------
If you have created a state method using either a ``template`` or a ``Factory``
and you would like to see it's code as if it where written by hand, use the
``to_code`` call.

Let's first look how to flatten a template state method:

.. code-block:: python
  :emphasize-lines: 20

  from miros import state_method_template
  from miros import ActiveObject
  from miros import signals, Event, return_status

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  # create a state method using a template
  fc = state_method_template('fc')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state method
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  ao.register_parent(fc, ao.top)

  # to see how fc would be written as a flat method:
  print(ao.to_code(fc)) # ->
    # @spy_on                                                                                   
    # def fc(chart, e):                                                                         
    #   status = return_status.UNHANDLED                                                        
    #   if(e.signal == signals.ENTRY_SIGNAL):                                                   
    #     status = return_status.HANDLED                                                        
    #   elif(e.signal == signals.INIT_SIGNAL):                                                  
    #     status = trans_to_fc1(chart, e)                                                       
    #   elif(e.signal == signals.BB):                                                           
    #     status = trans_to_fc(chart, e)                                                        
    #   elif(e.signal == signals.EXIT_SIGNAL):                                                  
    #     status = return_status.HANDLED                                                        
    #   else:                                                                                   
    #     status, chart.temp.fun = return_status.SUPER, chart.top                               
    #   return status                                                                           

Above we see that the state method is flattened using the ``to_code`` method of
the active object.  You could copy this and drop it into your design for
debugging purposes.

The same process applies for a state method built using the ``Factory``:

.. code-block:: python
  :emphasize-lines: 16
  
  from miros import ActiveObject
  from miros import signals, Event, return_status
  from miros import Factory

  # create the specific behavior we want in our state chart
  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  chart = Factory('factory_class_recipe_example')

  fc = chart.create(state='fc').                             \
    catch(signal=signals.BB, handler=trans_to_fc).           \
    catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
    to_method()

  chart.to_code(fc) # =>
    # @spy_on                                                                                   
    # def fc(chart, e):                                                                         
    #   status = return_status.UNHANDLED                                                        
    #   if(e.signal == signals.ENTRY_SIGNAL):                                                   
    #     status = return_status.HANDLED                                                        
    #   elif(e.signal == signals.INIT_SIGNAL):                                                  
    #     status = trans_to_fc1(chart, e)                                                       
    #   elif(e.signal == signals.BB):                                                           
    #     status = trans_to_fc(chart, e)                                                        
    #   elif(e.signal == signals.EXIT_SIGNAL):                                                  
    #     status = return_status.HANDLED                                                        
    #   else:                                                                                   
    #     status, chart.temp.fun = return_status.SUPER, chart.top                               
    #   return status                                                                           

To see how to unwind an auto-generated statechart read
:ref:`unwinding a state method<towardsthefactoryexample-unwinding-a-factory-state-method>`

.. _recipes-describing-your-work:

Describing your Work
^^^^^^^^^^^^^^^^^^^^

.. _recipes-drawing-a-statechart:

Drawing a StateChart
--------------------
The Harel formalism was consumed by the UML standard.

The UML standards were not properly curated and became overly-complicated and
full of contradictions.  As a result, they are largely disregarded by the
software community, so most of the open source drawing tool projects
have been abandoned.  

A lot of the commercial drawing tools have tried to keep up with the overly
complicated UML standards, so you end up fighting with the tools when you just
want to draw a simple picture.  The point of the picture is to be expressive
enough to explain something to someone else.

So in many ways UML has become a kind of anti-brand but it has it's good parts.
Skip the class diagrams and use the :ref:`sequence
diagram<recipes-drawing-a-sequence-diagram>` and the statecharts.

A statechart drawing tool only needs to provide the following features:

1. zoom in and out of a diagram.
2. draw the basic Harel statemachine building blocks.  
3. draw arrows and the other useful parts of UML.  
4. mark up the diagram with code
5. be simple to change a design

Pencil and paper are great for drawing your designs.  It is good to work on
them over and over again without the impediment of the computer interface
getting in your way.

Once you think you have it figured out you can transfer the picture into
something digital using a free tool called `umlet`_.

There is also an online version of the tool, which is called `umletino`_.

It is easy to use and it has a lot of youtube training videos.  It doesn't
provide the zooming features asked for by the original Harel paper (1987), but
this could be implemented using HTML/SVG if you have a lot of spare time.

If you want to drop an ASCII art picture into your code (which you will see in
the examples) you can use the `drawit`_ vim plugin, or something like it for
your text editor.  If you don't know how to do it yet, look up vertical
editing, this is required if you are going to sketch in meaningful pictures.

.. _recipes-drawing-a-sequence-diagram:

Drawing a Sequence Diagram
--------------------------

.. include:: i_making_sequence_diagrams_from_trace.rst


.. _recipes-testing:

Testing
^^^^^^^

.. _recipes-using-a-trace-as-a-test-target:

Using a Trace As a Test Target
------------------------------

.. include:: i_test_with_trace.rst

Using a Spy as a Test Target
----------------------------

.. include:: i_test_with_spy.rst

.. raw:: html

  <a class="reference internal" href="examples.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="patterns.html"><span class="std std-ref">next</span></a>

.. _umlet: http://www.umlet.com/
.. _umletino: http://www.umlet.com/umletino/umletino.html
.. _OMG: https://en.wikipedia.org/wiki/Object_Management_Group
.. _mandala: https://en.wikipedia.org/wiki/Sand_mandala
.. _drawit: https://github.com/vim-scripts/DrawIt
