.. _recipes:

Recipes
=======

.. toctree::
   :maxdepth: 2
   :caption: Contents:


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

.. _recipes-describing-your-work:

Describing your Work
--------------------

.. _recipes-drawing-a-statechart:

Drawing a StateChart
^^^^^^^^^^^^^^^^^^^^
The Harel formalism was consumed by the UML standard.

Then the UML standards became over-complicated (OMG).  Various committees tried
to build a set of diagrams that could describe **all** software architecture.
It was a losing battle from the start.

Then something even stranger started to happen across the development
community, "architects" were compelled to hang onto outdated design pictures
(and the ideas underneath them) because they had spent so much time building
them in the first place.  This created a kind of cultural backlash against the
type of people who tried to dominate their technical communities with designs
that obviously didn't work anymore, who felt superior because they understood
some sort of arcane picturing that the practitioners in their community didn't
care about.

The UML committees were egged on by technical people to make the pictures
specific to what ever technical feature their language had, and there was an
over-emphasis on class oriented diagrams, with many many different types of
arrows that had to be use differently depending on the kind of drawing you were
using.  In the end it created a kind of priesthood of people who had arcane
drawings that were incomprehensible to the actual practitioners.

As a result, most drawing tools are full of garbage and formalisms that you
probably don't care about.  I have yet to find an open source tool that doesn't
get in the way of me trying to draw a simple picture, with boxes and arrows,
where I can zoom in and out, and to write blocks of code anywhere I like.

Visio can do this, but it is expensive and then other people have to download a
viewer application see your diagram (welcome to the 90s).  The cheaper online
alternatives, force their own weird sub-versions of UML into their templates so
that once again you start fighting with them too.

Miro Samek wrote his own tool to deal with this problem, and when you
eventually switch over to his code, you will be greatly appreciative of the
speed and ease in which you can manifest your ideas into running designs.  But
his drawing tool is tightly coupled with his framework, so we can't use that
here either.

Pencil and paper are great for drawing your designs.  It is good to work on
them over and over again without the impediment of the computer interface
getting in your way.  Once you have locked down a design, though, you can
transfer the picture into something digital using a free tool called `umlet`_.

There is also an online version of the tool, which is called `umletino`_.

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
