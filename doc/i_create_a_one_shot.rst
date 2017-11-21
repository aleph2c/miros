.. called from recipes.rst

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

