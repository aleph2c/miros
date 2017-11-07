.. included from recipes
.. included from reflection
If you need a **very detailed description** of your system's behavior you will want
to use the `spy` instrumentation.  The spy outputs:

1. All of the internal activity that is run by the event processor
2. How your chart reacts to the events it has received
3. Information about what happened between each of the rtc activities.
4. If a signal was hooked by a state
5. If and when a signal was :ref:`deferred<recipes-deferring-an-event>`
6. If and when a signal was :ref:`recalled<recipes-deferring-an-event>`
7. The number of events awaiting immediate processing after a specific rtc activity.
8. The number of events which have had their processing deferred.

If you don't understand what these terms mean, read the
:ref:`simple posting example<examples-simple-posting-example>`, since it
introduces all of these ideas.

To access the full spy:

.. code-block:: python

  # import a pretty printer (like print)
  from miros import pp

  # .. state charts and other code here

  # Assuming your active object is called `ao`
  # we use the pretty printer to write the
  # full spy log to the terminal
  pp(ao.spy())

This might output:

.. code-block:: python
  :emphasize-lines: 1,7,13,21,29,35,46,53,58
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'ENTRY_SIGNAL:middle',
   'INIT_SIGNAL:middle',
   '<- Queued:(0) Deferred:(0)',
   'A:middle',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(1)',
   'A:inner',
   'A:middle',
   'EXIT_SIGNAL:inner',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(2)',
   'A:inner',
   'A:middle',
   'EXIT_SIGNAL:inner',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(3)',
   'D:inner',
   'D:middle',
   'D:outer',
   'POST_FIFO:B',
   'D:outer:HOOK',
   '<- Queued:(1) Deferred:(2)',
   'B:inner',
   'B:middle',
   'B:outer',
   'EXIT_SIGNAL:inner',
   'EXIT_SIGNAL:middle',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'POST_FIFO:B',
   'RECALL:B',
   'INIT_SIGNAL:outer',
   '<- Queued:(1) Deferred:(1)',
   'B:outer',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'POST_FIFO:B',
   'RECALL:B',
   'INIT_SIGNAL:outer',
   '<- Queued:(1) Deferred:(0)',
   'B:outer',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'INIT_SIGNAL:outer',
   '<- Queued:(0) Deferred:(0)']
 
If you would like to understand in detail how to read this log, and how it
might have occurred, reference :ref:`the example from which it
came<examples-simple-posting-example>`.

The spy log is a ring buffer that contains 500 spots.  This is so your system
can run forever without using an infinite amount of memory.  Once the internal
spy log has run out of room, it will shift out the old data and write the new
data at the tail end of its log.

