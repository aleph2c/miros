.. included by reflection
.. included by recipes
If you would like to see what your active object was doing from a **very high
level**, you can look at it's `trace` instrumentation.  The trace will only
create a log item if a state transition has occurred. Each line in the `trace`
will contain:

1. A datetime stamp between square brackets
2. The active object name, between square brackets
3. The event that caused the transition, its signal number and its payload 
4. The starting state
5. The ending state

If you haven't named your active object, a unique identifier is given to it,
and the first 5 characters of this unique identifier will be used in the trace.
The reason that an identifier is given to it is so that the trace outputs, from
multiple active objects, can be distinguished from one another.

Suppose you have built the tazor active object described in the :ref:`second
example<examples-tazor-example>`. Suppose you named this active object `tazor`:
To see the trace you would type:

.. code-block:: python

  tazor.trace()

This would output the following trace:

.. code-block:: python
  :emphasize-lines: 1

  [2017-11-06 08:34:28.268873] [75c8c] e->start_at() top->arming
  [2017-11-06 08:34:26.312241] [75c8c] e->BATTERY_CHARGE() arming->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BATTERY_CHARGE() armed->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BATTERY_CHARGE() armed->armed

Notice that on line one, the signal is called `start_at`.  There is no signal
called `start_at`, here the trace is actually using the method name `start_at`
to indicate how the chart was started.

A trace can be used with the `sequence` project to generate a sequence diagram,
more about that is described :ref:`here.<reflection-creating-a-sequence-diagram>`

.. _reflection-an-extremely-detailed-view:
