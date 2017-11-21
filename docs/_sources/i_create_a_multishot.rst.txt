.. called from recipes.rst

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

