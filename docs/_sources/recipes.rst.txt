.. toctree::
   :caption: Contents:


.. _recipes:

Recipes
=======

How to do the small things you need to do with coding examples.

.. _posting_events:


Posting Events
--------------

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
to do this with a timing heart beat or for a events that needs to be processed
with a greater priority than over events.


.. _recipes-creating-a-one-shot-event:

Creating a One-Shot Event
^^^^^^^^^^^^^^^^^^^^^^^^^
A one-shot event can be used to add some delay between state transitions.  You
can think of them as delayed 'init' signals.  You might want to use a one-shot if
you need a system to settle down a bit before transitioning into an inner
state.

Generally speaking, you should cancel your one-shot events as your chart passes
control to outer states.  You don't need to do this, but if you don't your
outer states will be hit with one-shot messages that they don't care about
and your chart will needlessly search in reaction to these events.

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
--------------------------------------
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
