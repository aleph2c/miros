.. included from recipes
.. included from reflection
If you would like to sketch out the high level behavior of your statechart using
a trace output as the target for a regression test, you would:

1. Run your program and print your trace to the output.  
2. Copy this trace as the target behavior of your test.
3. Run this trace target and the future output of the statechart trace through
   the :ref:`stripped context manager<stripped_example>` to remove the date
   timestamp information.  
4. Compare your target with the results.

This should become clear with an example.

Consider a statechart that outputted the following at the point when you were
working on it.

.. code-block:: python

  [2017-11-05 21:31:56.098526] [tazor] e->start_at() top->arming
  [2017-11-05 21:31:56.200047] [tazor] e->BATTERY_CHARGE() arming->armed
  [2017-11-05 21:31:56.300974] [tazor] e->BATTERY_CHARGE() armed->armed
  [2017-11-05 21:31:56.401682] [tazor] e->BATTERY_CHARGE() armed->armed

You might have gotten this output with the following code:

.. code-block:: python

  print(tazor.trace())

It does a decent job describing what we want, but it has timestamps.  With the
`stripped` context manager we can turn the above into something that would look
like this:

.. code-block:: python

  [tazor] e->start_at() top->arming
  [tazor] e->BATTERY_CHARGE() arming->armed
  [tazor] e->BATTERY_CHARGE() armed->armed
  [tazor] e->BATTERY_CHARGE() armed->armed

That is something that shouldn't change over time, it looks like something we
could use as a test specification.  The only problem is that when we run the
code in the future and generate a new trace we get a trace with a pre-pended
date timestamp.  We can get around this issue like this:

.. _stripped_example:

.. code-block:: python
  :linenos:

  from miros.hsm import stripped

  target = \
  '''[2017-11-05 21:31:56.098526] [tazor] e->start_at() top->arming
     [2017-11-05 21:31:56.200047] [tazor] e->BATTERY_CHARGE() arming->armed
     [2017-11-05 21:31:56.300974] [tazor] e->BATTERY_CHARGE() armed->armed
     [2017-11-05 21:31:56.401682] [tazor] e->BATTERY_CHARGE() armed->armed
  '''
  with stripped(target) as stripped_target, \
       stripped(tazor.trace()) as stripped_trace_result:

    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

On line **1** we import the stripped context manager.

On lines **3-7** we define the target as just being the trace that we copied
when we were first designing our statechart.

On line **9**, we map this target to the ``stripped_target`` which contains the
same string with the date timestamps removed.  

On line **10**, we use the same stripped context manager to strip our tazor active
object's trace output of it's date timestamp information and place the result
into the ``stripped_trace_result`` variable.

Lines **12-13** are for testing each line of our output against our target.

If our design changes, it is easy to update the test, we just copy the new
trace of of new design into the target string and everything should be peachy.
