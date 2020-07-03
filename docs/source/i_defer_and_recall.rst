.. called from recipes

There will be situations where you want to post a kind of artificial event into
a queue which won't immediately be acted upon by your statechart.  It is an
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
