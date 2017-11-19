.. _recipes:

Recipes
=======

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. _recipes-states:

States
------
In the miros frame work, your state methods act as places to link your
application code into designed behavior.

States need to:

1. React to events and run your application code.
2. Describe their parent state.
3. Describe how they should transition to non-parent states.

There are different ways to create states with miros:

1. You can create a hand-coded state method. [flat states]

2. You can have the library generate a state method for you, then register
   callback responses to specific events and set a parent at runtime.
   [factory states]

3. You can use a fusion technique.  You can hand write a state and use context
   managers within the method so that the miros package can register callbacks
   for specific signals, or even change it's parent at run time. [fusion
   states]

.. _recipes-what-a-state-does-and-how-to-structure-it:

What a State Does and How to Structure it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Your state methods represent the rounded rectangles in your statechart diagram.
They contain information about how a state should react to an event and they
contain information about how they relate to other states.  They do not
explicitly create the behavior that you expect from your statechart, this is
done by an event processor.  An event processor is created when you instantiate
an active object. It is the thing that calls the state methods over and over
again to enact the expected behavior of your design.

When an active object uses its ``start_at`` method, it connects your state
method to its event processor.  

An event processor never actually learns or remembers the full nature of how
your state methods are linked to one another, it only remembers it's current
state and where it would like to transition within the diagram on its next
pass.  It always searches them as it reacts to whatever event you have provided
it.  So, your design is discovered as the event processor reacts to events.  Your
state method's can be used by many different event processors, they're
polyamorous:

.. image:: _static/eventprocessors.svg
    :align: center

In the diagram above we see that two different active objects can use the same
statechart structure.  Each active object can be in a different state, even
though they are using the same diagram.   ``ao1`` starts it's interpretation of
the statechart in state ``c`` and ``ao2`` starts it's interpretation of the
statechart in state ``c2``.  As someone building this design you would create
two different active objects, and you would define three different state
methods, then you would start the different active objects with a ``start_at``
call.

You don't explicitly call an event processor while using the miros api, it is
called in the background when you use methods like ``start_at``, ``post_fifo``
or ``post_lifo``.

The event processor treats a state method as if it was defined within its own
class.  It does this by using its ``self`` variable in the first argument in
the state method call.  It then injects the event into the second argument to
see what the state method will do about it.  The state method communicates
back, by adjusting internal attributes on the ``self`` variable of the thing
searching it and by returning a status value as it reacts to the events.

This means that state methods themselves are stateless.  They do not keep
internal variables, they only react and tweak the variable states of the
objects that were given to them as input arguments.  It is the ``self``
variable of the outside caller that has new information impressed upon it.
This is how state methods stay polyamorous.

The states contain a place to anchor your application code.  They also provide
information about the design topology of your chart.  They describe their
parent state, and they describe how some events can cause transitions to other
state methods. That's it.  There is no full picture described in a table or in
any other data structure.  The picture is actually written into the interaction
between your state method descriptions and the event processor's reaction to
them.

The event processor remembers which state method is it's current state.  When
it is given an event, it calls this state method with the event and listens to
its response.  If the state method returns an ``UNHANDLED`` result, the event
processor will call it again to find it's parent state.  Then it will call the
parent state with the original event.  This process continues until the event
is handled, or the event processor falls off the edge of the map.

The event processor uses the ``SEARCH_FOR_SUPER_SIGNAL`` named event to ask for
a parent state.  When a state method hears this event it is expected to do two
things:

1.  set ``self.temp.fun`` to point to it's parent state method
2.  return the value of ``return_status.SUPER``

It is easier to just have an ``else`` clause in your state method rather than
adding ``SEARCH_FOR_SUPER_SIGNAL`` explicits to an ``elif`` clause:

.. image:: _static/stateapplicationcode1.svg
    :align: center

For the outermost state of your state chart you set the parent to ``self.top``.
This state method is actually defined within the event processor and when it
sees this state it knows that it is about to fall of the edge of your map.

If your parent state isn't the outer most state, you would just set the
``self.temp.fun`` to whatever state is:

.. image:: _static/stateapplicationcode2.svg
    :align: center

Here we see how the state method ``c1`` would tell the event processor that
it's parent state is ``c``.

In the case that you would like your chart to transition to another state, you
would use the ``trans`` method.

.. image:: _static/stateapplicationcode3.svg
    :align: center

Now let's look at the full code for this diagram:

.. image:: _static/eventprocessors.svg
    :align: center

First you would describe state's ``c``, ``c1`` and ``c2``:

.. code-block:: python

  from miros.hsm import spy_on
  from miros.activeobject import ActiveObject
  from miros.event import signals, return_status, Event

  def c(self, e):
    status = signals.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      # call c's entry code
      status = signals.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = self.trans(c1)
    elif(e.signal == signals.B):
      status = self.trans(c)
    elif(e.signal == signals.EXIT_SIGNAL):
      # call c's exit code
      status = signals.HANDLED
    else:
      status = return_status.SUPER
      chart.temp.fun = self.top
    return status

  def c1(self, e):
    status = signals.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = signals.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = signals.HANDLED
    elif(e.signal == signals.A):
      status = trans(c2)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = signals.HANDLED
    else:
      status = return_status.SUPER
      chart.temp.fun = self.c
    return status

  def c2(self, e):
    status = signals.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = signals.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = signals.HANDLED
    elif(e.signal == signals.A):
      status = trans(c1)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = signals.HANDLED
    else:
      status = return_status.SUPER
      chart.temp.fun = self.c
    return status

To connect the state methods into the two different active objects, we would
create the active objects and then start them in their desired states:

.. code-block:: python

  ao1, ao2 = ActiveObject(), ActiveObject()
  ao1.start_at(c)
  ao2.start_at(c2)

``ao1`` would act as if it owned the map, and ``ao2`` would act as if it owned
the map.  Neither would know that `their` state methods were being used by more
than one active object.

Events And Signals
-----------------
.. _recipes-creating-an-event:

Creating an Event
^^^^^^^^^^^^^^^^^
An event is something that will be passed into your statechart, it will be
reacted to, then removed from memory.

.. code-block:: python
  :linenos:

    from miros.event import Event
    from miros.event import signals

    event_1 = Event(signal="name_of_signal")
    # or 
    event_2 = Event(signal=signals.name_of_signal)

.. _recipes-creating-a-signal:

Creating a Signal
^^^^^^^^^^^^^^^^^
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
  :linenos:

    from miros.event import Event
    from miros.event import signals
    
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
^^^^^^^^^^^^^^
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

Posting an Event to the Lifo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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


.. _recipes-creating-a-one-shot-event:

Creating a One-Shot Event
^^^^^^^^^^^^^^^^^^^^^^^^^
A one-shot event can be used to add some delay between state transitions.  You
can think of them as delayed **init** signals.  You might want to use a one-shot if
you need a system to settle down a bit before transitioning into an inner
state.

Generally speaking, you should cancel your one-shot events as your chart passes
control to outer states.  You don't need to do this, but if you don't your
outer states will be hit with one-shot messages that they don't care about
and your chart will needlessly search as it reacts to these events.

It is important to know that if your chart changes state, the event posted to
it will look like it came from outside of your statechart, even though it was
originally generated within a given state.  The construction of any event with
the ``fifo`` or ``lifo`` api behaves like this.

.. code-block:: python

    # Here define a middle state the creates a one-shot event called
    # delayed_one_second.  The same delayed_one_second signal is captured
    # by the middle state and used to transition into the inner state
    @spy_on
    def middle(ao, e):
      status = state.UNHANDLED

      # we have entered the state and we would like to delay one
      # second prior to entering the inner state
      if(e.signal == signals.ENTRY_SIGNAL):
          ao.post_fifo(
            Event(signal=signals.delay_one_second),
            times=1,
            period=1.0,
            deferred=True
          )
        status = state.HANDLED

      elif(e.signal == signals.EXIT_SIGNAL):
        # we are leaving this state for an outer state
        # so we cancel our one-shot in case it hasn't gone off yet
        ao.cancel_events(ao.delay_one_second)
        status = state.HANDLED

      # ignore our init
      if(e.signal == signals.INIT_SIGNAL):
        status = state.HANDLED

      # our one-shot has fired, one second has passed since
      # we transitioned into this state, now transition
      # to our desired target; 'inner'
      elif(e.signal == signals.delay_one_second):
        status = ao.trans(inner)

      else:
        status, ao.temp.fun = state.SUPER, outer
      return status

.. _recipes-creating-a-multishot-event:

Creating a Multishot Event
^^^^^^^^^^^^^^^^^^^^^^^^^^
A multi-shot event is just an extension of the one-shot idea.  Instead of only
being fired once on entry, it can be fired between 2 and an infinite number of
times.  You would use a multi-shot event if you would like to provide an inner
part of your chart with a heart beat that the outer part of your chart doesn't
need to know about.  In this way you could save cycles by avoiding unnecessary
event processing in the parts of the chart that don't need these heart beats.
This will also be useful while debugging your chart, your logs won't be filled
with unnecessary events.

You should cancel your multi-shot events in the exit handler of the state that
created them.

.. code-block:: python

    # Here define a middle state the creates a multi-shot event called
    # three_pulse.  The same three_pulse signal is captured
    # by the middle state and used to transition into the inner state
    @spy_on
    def middle(ao, e):
      status = state.UNHANDLED
      if(e.signal == signals.ENTRY_SIGNAL):
        multi_shot_thread = \
          ao.post_fifo(Event(signal=signals.three_pulse),
                          times=3,
                          period=1.0,
                          deferred=True)
        # We mark up the ao with this id, so that
        # state function can be used by many different aos
        ao.augment(other=multi_shot_thread,
                      name='multi_shot_thread')
        status = state.HANDLED

      elif(e.signal == signals.EXIT_SIGNAL):
        ao.cancel_event(ao.multi_shot_thread)
        status = state.HANDLED

      if(e.signal == signals.INIT_SIGNAL):
        status = state.HANDLED
      elif(e.signal == signals.three_pulse):
        status = ao.trans(inner)
      else:
        status, ao.temp.fun = state.SUPER, outer
      return status

By setting the ``times`` argument of the ``post_fifo`` to 0, you can create an
infinite multi-shot event.  This is how you could make an inner heart beat.

The ``post_lifo`` api can be used the same as the ``post_fifo`` api for
creating these types of repeating events.  You would use the ``post_lifo`` api
when you would need your heart beat event signal to barge ahead of all other
events waiting to be processed by the active object.


.. _recipes-cancelling-a-specific-event-source:

Cancelling a Specific Event Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

Cancelling Event Source By Signal Name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

Deferring and Recalling An Event
^^^^^^^^^^^^^^^^^^
There will be situations where you want to post a kind of artificial event into
a queue which won't immediately be acted upon by your startchart.  It is an
`artificial` event, because your chart is making it up, it isn't being given to
it by the outside world.  It is a way for your chart to build up a kind of
processing pressure that can be relieved when you have the cycles to work on
things.

This is a two stage process, one, deferring the event, and two, recalling the
event.  It is called a deferment of an event because we are holding off our
reaction to it.

.. code-block:: python

    # code to place in the state that is deferring the event:
    chart.defer(Event(signal=signals.signal_that_is_deferred)

    # code to place in the state where you would like the event reposted into
    # the chart's first in first out queue
    chart.recall() # posts our deferred event to the chart.

.. _seeing_what_is_going_on:

Seeing What is Going On
-----------------------

.. _recipes-determining-the-current-state:

Determining the Current State
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_determining_the_current_state.rst 

.. _recipes-seeing-what-signals-you-have-in-your-system:

Seeing what Signals You Have In Your System
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _recipes_seeing_your_signals:

.. include:: i_seeing_your_signals.rst 

.. _recipes-using-the-trace:

Using the Trace
^^^^^^^^^^^^^^^

.. include:: i_trace_reactive.rst

.. _recipes-using-the-spy:

Using the Spy
^^^^^^^^^^^^^

.. include:: i_spy_reactive.rst

.. _recipes-tracing-live:

Tracing Live
^^^^^^^^^^^^

.. _recipes-spying-live:

Spying Live
^^^^^^^^^^^

.. _recipes-scribble-on-the-spy:

Scribble On the Spy
^^^^^^^^^^^^^^^^^^^

.. include:: i_scribble_on_the_spy.rst

.. _recipes-describing-your-work:

Describing your Work
--------------------

.. _recipes-drawing-a-statechart:

Drawing a StateChart
^^^^^^^^^^^^^^^^^^^^
The Harel formalism was consumed by the UML standard.

The UML standards were not properly curated and became over-complicated.
As a result, they are largely disregarded by the software community, so most of
the open source drawing tool projects have been abandoned.

UML is still useful in that it provides a common way of describing software
systems.  There is no reason not to use the parts of it that you like and leave
the parts of it that you either don't understand or that are too complicated to
bother with. (This happens in C++ too)

To draw a statechart on a computer, you need a drawing tool.

For this tool to be useful, you need to be able to:

1. zoom in and out of a diagram. (asked for in 1987) 
2. draw the basic Harel statemachine building blocks.
3. draw arrows and the other useful parts of UML 
4. mark up the diagram with code 
5. quickly and easily change your design

I have yet to find an open source tool that doesn't get in the way of me trying
to draw a simple picture, with boxes and arrows, where I can zoom in and out,
and write blocks of code anywhere I like.

Visio can do this, but it's expensive and other people have to download a
viewer application in order to see your diagram.  The cheaper online alternatives,
force their own weird sub-versions of UML into their templates, so that once
again you start fighting with the tool.

Miro Samek wrote his own tool to deal with this problem and if you eventually
switch over to his code, you will be greatly appreciative of the speed and ease
in which you can manifest your ideas into pictures, then into running designs.
But his drawing tool is tightly coupled with his framework (as it should be),
so we can't use that here either.

Pencil and paper are great for drawing your designs.  It is good to work on
them over and over again without the impediment of the computer interface
getting in your way.  Once you think you have it figured out you can transfer
the picture into something digital using a free tool called `umlet`_.

There is also an online version of the tool, which is called `umletino`_.

The nice thing about this tool is that it is so simple to use.  It also makes
ugly pictures, which is a kind of good thing.

A UML diagram should be thought as graffiti on the wall, rather than a great
work of art.  It should be easy for you to change your design.  If it took you
5 hours to build a beautiful masterpiece you will feel a psychological
impediment to change it.  We don't want to get locked into our thinking.

.. _recipes-drawing-a-sequence-diagram:

Drawing a Sequence Diagram
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_making_sequence_diagrams_from_trace.rst


.. _recipes-testing:

Testing
-------

.. _recipes-using-a-trace-as-a-test-target:

Using a Trace As a Test Target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_test_with_trace.rst

Using a Spy as a Test Target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_test_with_spy.rst

.. _umlet: http://www.umlet.com/
.. _umletino: http://www.umlet.com/umletino/umletino.html
.. _OMG: https://en.wikipedia.org/wiki/Object_Management_Group
.. _mandala: https://en.wikipedia.org/wiki/Sand_mandala
