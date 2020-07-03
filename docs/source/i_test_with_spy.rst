.. included from recipes
.. included from reflection

A trace does not tell the full story about what your system is doing.  For
instance it is blind to hooks, deferred events and many other things that might
happen in the dynamics of your active object.  If you need to look at the
`exact` behavior of your system, you can:

1. Run your program and print your spy to the output.
2. Copy the spy as your target behavior.
3. Compare the target with the results.

Here is an example:

.. code-block:: python
  :emphasize-lines: 1-3
  :linenos:

  # pp(tazor.spy())
  # import pdb.set_trace()
  assert(tazor.spy() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:arming',
     'SEARCH_FOR_SUPER_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:arming',
     'INIT_SIGNAL:arming',
     '<- Queued:(0) Deferred:(0)',
     'BATTERY_CHARGE:arming',
     'SEARCH_FOR_SUPER_SIGNAL:armed',
     'ENTRY_SIGNAL:armed',
     'POST_DEFERRED:CAPACITOR_CHARGE',
     'INIT_SIGNAL:armed',
     '<- Queued:(0) Deferred:(1)'])

On line **1** we have a commented pretty print command ready to go for when we
need to rebuild our test specification.  When the test fails in the future,
which it will because this is a tightly coupled test, we will uncomment lines
**1-2** then re-run the test.

This will drop us into a debugging session just after our next spy output has
been printed to the screen.  At this point we would carefully determine if it
actually describes the new behavior we are looking for. If it wasn't, we would
fix the issue, otherwise we over-write lines **4-16** with this new
specification.

We would re-comment lines **1-2** and re-run our tests.
