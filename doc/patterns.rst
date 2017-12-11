.. _patterns:

Patterns
========
The idea of software design patterns came from the architect Christopher
Alexander.  He wrote a book, a pattern language, about how different approaches
to architecture could be used across different scales (from the country to the
pantry) to help people feel better about living in their communities.  It's a
lovely book, a child can understand it yet it is still useful for professionals.

This can not be said for the book it inspired in computer science, "Design
Patterns: Elements of Reusable Object-Oriented Software"  This book *was not*
child friendly, in fact everyone I knew secretly hated it because of its
illegibility; but would make sure to have a copy of it on their shelf to look
like they were in the club.

The ideas within the book were great and the follow up books that translated it
into English were really useful.  Basically it described a set of techniques
for solving classes of problems that come up over and over again.  If you
haven't learned the patterns yet, find a copy of a patterns book written by a
practitioner in your language(s) and work through it.  You will level up.

In chapter 5 of "Practical UML STATECHARTS in C/C++" I was leveled up by Miro
Samek.  He describes 5 statechart patterns and made the bold claim that
**statecharts are a pattern of patterns**.  I completely agree with him.  So here
is my translation of his work into this library.  I'll start each pattern with
quotes from his book, then write about it within the context of this work.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. _patterns-ultimate-hook:

Ultimate Hook
^^^^^^^^^^^^^
Formal description:

    [The Ultimate Hook Pattern provides a] common facilities and policies for
    handling events but let clients override and specialize every aspect of the
    system's behavior.

    The semantics of state nesting provide the desired mechanism of handling
    all events, first in the context of the client code (the nested state) and
    of automatically forwarding of all unhandled events to the [parent state]
    (the default behavior). In that way, the client code intercepts every
    stimulus and can override every aspect of the behavior. To reuse the
    default behavior, the client simply ignores the event and lets the
    superstate handle it (the [child state] inherits behavior from the
    superstate) [#1]_

Makes sense to me.  Keep up!

To understand the ultimate hook pattern, you first have to understand what a
hook is.  It is just some code in an ``if-elif`` clause.   A hook is just some
code that catches an event, runs your :term:`client code<Client Code>` and then
returns something which tells the event processor to stop searching.  A hook
doesn't cause a state transition.  It is a way to get the event processor's
search algorithm to do work for you without changing state.

You see, anytime the event processor is trying to figure out what to do with an
event it needs to :ref:`search your
statechart<recipes-what-a-state-does-and-how-to-structure-it>`.  If it finds
that it needs to do a transition, it will enlist the heavy-duty parts of it's
algorithm to make sure that the :term:`Harel Formalism<Harel Formalism>`
occurs.  The hook has nothing to do with this, because it short circuits the
search before it does a transition, but not before it gets the search algorithm
to do some useful work.

If your if-else structure in your state method catches the signal name of an
event, runs your code, then returns the ``return_status.HANDLED`` back to the
event processor, no state transition will occur.  This is how you make a hook.
You make sure that part of your if-elif clause catches the event signal, runs
your :term:`client code<Client Code>` and returns the ``return_state.HANDLED``
value.

.. image:: _static/ultimate_hook1.svg
    :align: center

Here is a simple example which demonstrates a hook.  In this example we will
show that we can get some client code to run when we post an event with the
signal name of BEHAVIOR_NAME to your statechart:

.. code-block:: python
  :emphasize-lines: 10-13

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(outer_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

The highlighted code describes the hook.  We see that when the
BEHAVIOR_NAME signal is caught by this state method it runs your client
code then returns ``return_status.HANDLED``.

The :ref:`spy<recipes-using-the-spy>` output would look like this:

.. code-block:: python
  :emphasize-lines: 7
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'INIT_SIGNAL:outer_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:outer_state',
   'your outer_state code here',
   'BEHAVIOR_NAME:outer_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

Lines 1-5 describe the first :term:`rtc<Run To Completion>` event which occurs
when we start the statechart.  Lines 5-9 of the
:ref:`spy<recipes-using-the-spy>` log actually describe the hook behavior.  The
event processor ran, searching the statechart starting at the outer_state
method to see if it knew how to process the BEHAVIOR_NAME signal and it did:
the client code just scribbled something into our
:ref:`spy<recipes-using-the-spy>` log so we can see what happened.  On line 7
we see the result of this in the :ref:`spy<recipes-using-the-spy>` log.
Furthermore, no state transition occurred.

.. image:: _static/ultimate_hook2.svg
    :align: center

Now suppose we add another state within the outer state and start our active
object there.

.. code-block:: python
  :emphasize-lines: 20-29, 32
  :linenos:

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your inner_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = outer_state
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

Then look at the spy:

.. code-block:: python
  :emphasize-lines: 9
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:inner_state',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'ENTRY_SIGNAL:inner_state',
   'INIT_SIGNAL:inner_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:inner_state',
   'your inner_state code here',
   'BEHAVIOR_NAME:inner_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

Ok, no surprises.  The inner_state hooked the BEHAVIOR_NAME signal and
ran some client code.

.. image:: _static/ultimate_hook3.svg
    :align: center

Now let's remove the handling of the BEHAVIOR_NAME from our
inner state and see what happens when we start the active object in the
inner_state then send it an event with the BEHAVIOR_NAME.

.. code-block:: python
  :emphasize-lines: 28-29
  :linenos:
  
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    #if(e.signal == signals.BEHAVIOR_NAME):
    #  # your code would go here
    #  chart.scribble("your inner_state code here")
    #  status = return_status.HANDLED
    #else:
    #  chart.temp.fun = outer_state
    #  status = return_status.SUPER
    chart.temp.fun = outer_state
    status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

In the highlighted code you can see that I adjusted the inner_state to run as
if it's ``else`` method clause was always active.  I did this so that it would not
handle the BEHAVIOR_NAME signal.  Now we run the code and look at the trace.

.. code-block:: python
  :emphasize-lines: 8-11
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:inner_state',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'ENTRY_SIGNAL:inner_state',
   'INIT_SIGNAL:inner_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:inner_state',
   'BEHAVIOR_NAME:outer_state',
   'your outer_state code here',
   'BEHAVIOR_NAME:outer_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

The highlighted lines show how our event processor tried to determine what to
do with the event containing the BEHAVIOR_NAME signal.

It called the inner_state with the event (8), it wasn't handled, so it
called the parent outer_state with the same event (9) and we see on
line (10) that the outer_state client code was run.  Finally, on line (11)
the spy instrumentation tells us that it detected a hooked event.  When you see
this in the log it means there was no state transition.

So, the outer_state hook code caught an event that was sent to the
inner_state.  The :term:`Harel Formalism<Harel Formalism>` followed by the
event processor determines that when it has an event, it will search outward
from the current state, to the next parent state, then the next parent state
over and over until your event is handled or, it reaches the top most state of
your :term:`HSM<Hierarchical State Machine>`. This means that any inner state
method will automatically inherit the hook code of any outer state.  The outer
most state contains the ultimate hook; this is why the pattern is called what
it is.

.. image:: _static/ultimate_hook4.svg
    :align: center

You can overwrite the behavior of the outer state hooks simply by explicitly
handling the signal in an inner state.  These ideas are very similar to
inheritance and overloading in object oriented programming.

As a designer you would write default client code behavior in the outer states
of charts, and all of your inner states would get this behavior for free.  If
they needed to overwrite this behavior they would specifically handle the
event in their state methods.

.. image:: _static/ultimate_hook5.svg
    :align: center

.. _patterns-deferred-event:

Deferred Event
^^^^^^^^^^^^^^

.. _patterns-reminder:

Reminder
^^^^^^^^


.. _patterns-orthogonal-component:

Orthogonal Component
^^^^^^^^^^^^^^^^^^^^


.. _patterns-transition-to-history:

Transition To History
^^^^^^^^^^^^^^^^^^^^^


.. _patterns-multichart-race:

Multichart Race
^^^^^^^^^^^^^^^


.. _patterns-multichart-pend:

Multichart Pend
^^^^^^^^^^^^^^^

.. [#1] p.206 Practical UML STATECHARTS in C/C++, Second Edition

