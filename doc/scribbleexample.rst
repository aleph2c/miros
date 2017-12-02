
.. _scribbleexample-hacking-to-learn-the-deeper-dynamics:

Hacking to Learn
================

.. _scribbleexample-first-pass:

In this example I ask a small question about a statechart.  Then we will:

1. try to answer the question
2. build the chart in working code
3. test out our answer
4. learn something

A Picture and a Question
------------------------

.. image:: _static/scribble.svg

Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?

If you are unfamiliar with UML, this part of the diagram:

.. image:: _static/guard.svg
    :align: center

contains a **guard**.  Specifically, the code:

.. code-block:: python

  [g()] 

on the arrow is the **guard**.  

It is shorthand for: `if the logic between the square brackets is True then let
the event on the arrow pass through`.  The code that is after the guard on the
diagram, ``t()``, runs if the guard doesn't block it.  Now that we know how a
guard works, we can infer that:

.. image:: _static/guard2.svg
    :align: center

means:

1. When I see a `T` event, ask for permission from the guard to see if it can pass.
2. The `g` function is the guard
3. If `g` returns True, `T` can pass; it can run the `t` function then make the transition to state `s2` [#f1]_.
4. If `g` returns False the `T` event is ignored by the chart.

A Partial Answer
----------------

Now that we understand that, let's re-ask the question:

"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

Well, if we start in ``s11``, then we receive a ``T``, ``s11`` wouldn't know
what to do with ``T``, so it would pass it out to ``s1``.  ``s1`` *does know*
what to do with ``T``, it would try to pass it to ``s2``.  

Ok, now how do we get from ``s11`` to ``s2``?  We need to exit, ``s11``,
then we need to exit ``s1`` then we need to enter ``s2``.  Oh, and don't forget
to run ``g`` and ``t`` on the ``T`` event.  Here is a working theory:

1. ``a`` will run because ``s11`` needs to be exited.
2. ``b`` will run because ``s1`` needs to be exited.
3. ``g`` will run because it is the guard for the `T` event between the ``s1`` and ``s2`` states.
4. ``t`` will run (assuming that ``g`` returned true)
5. ``c`` will run because ``s2`` needs to be entered.

A Better Answer
---------------
Now that we have a partial answer, let's re-ask the question:

"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

If we look at the ``s2`` state, we see that it has an initialization event
(black dot) with another function ``d`` hanging on it .  After ``s2`` is
entered, we would expect the next thing to be a transition into the ``s21``
state, but first we would run the ``d`` function on the arrow tied to the black
dot, since it is outside of the ``s21`` state and we haven't entered it yet.
Let's add this to our working theory:

1. ``a`` will run because ``s11`` needs to be exited.
2. ``b`` will run because ``s1`` needs to be exited.
3. ``g`` will run because it is the guard for the `T` event between the ``s1`` and ``s2`` states.
4. ``t`` will run (assuming that ``g`` returned true)
5. ``c`` will run because ``s2`` needs to be entered.
6. ``d`` will run on the init transition event from ``s2`` to ``s21``
7. ``e`` will run because the ``s21`` needs to be entered.

Our First Working Hypothesis
----------------------------
"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

Ok, our thinking is a bit clearer now but let's tighten up our answer.  There are
actually two parts, because the guard can return True or False.  We will start with the
easy part of the answer, then explain the longer part of the answer:

1. If g() returns False, none of the functions are called.
2. If g() returns True, then...  wait ``g`` had to be called first? Hmm.. whatever, here is
   my theory so far:  ``a``, ``b``, ``g``, ``t``, ``c``, ``d``, ``e``.  It is
   easy to answer this way because my eyes work that way when I'm looking at
   the picture.

But, there is something nagging at me now: ``g`` had to be called first, otherwise
my answer doesn't really make any sense.  So, here is my answer:

1. If g() returns False, only ``g`` is called
2. If g() returns True, then ``g``, ``a``, ``b``, ``t``, ``c``, ``d``, ``e``.


We have our theory, but we are hackers not philosophers.  We have more work to
do.  Hackers ruthlessly deploy the scientific method to seek understanding
about things they care about.  Hackers do four hard things over and over again:

1. Think.
2. Move past technical boundaries
3. Destroy their own theories by seeking contrary evidence.
4. Learn from their mistakes

Now that I think I understand how the statechart works, I have performed the
first thing on the list.  To try and disprove my theory, I will need to build
up the statechart in the diagram and actually see what happens.

.. _scribbleexample-from-diagram-to-code,-first-pass:

Code, Make a Picture
--------------------

To begin with I will draw the picture in the code, so that as I work I can see
what I'm trying to build:

.. code-block:: python

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''
.. _scribbleexample-from-diagram-to-code,-second-pass:

Code, Required Imports
----------------------

Now I'll import the items I'll need to run my experiment:

.. code-block:: python
  :emphasize-lines: 16-19

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

.. _scribbleexample-from-diagram-to-code,-third-pass:

Code, Frame in the States
-------------------------

Now I will frame in the state methods:

.. code-block:: python
  :emphasize-lines: 20-22,24-26,28-30,32-34,36-38

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e)
    pass

  @spy_on
  def s1_state(chart, e)
    pass

  @spy_on
  def s11_state(chart, e)
    pass

  @spy_on
  def s2_state(chart, e)
    pass

  @spy_on
  def s21_state(chart, e)
    pass

.. _scribbleexample-from-diagram-to-code,-fourth-pass:

Code, Add Common Internal State Code
------------------------------------

Now I add the internal-event-handling code into each of the state
methods:

.. code-block:: python
  :emphasize-lines: 22-30, 34-42, 45-54, 58-66, 70-78

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e)
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def s1_state(chart, e)
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def s11_state(chart, e)
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def s2_state(chart, e)
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def s21_state(chart, e)
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

.. _scribbleexample-from-diagram-to-code,-fifth-pass:

Code, Add Hiearchy
------------------

Then I add the hierarchy:

.. code-block:: python
  :emphasize-lines: 30,44,58,71,84

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def s1_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      a(chart)
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s11_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status


  @spy_on
  def s2_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s21_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status

.. _scribbleexample-from-diagram-to-code,-sixth-pass:

Code, Add the T and Init events
-------------------------------

Now I'll add management for the ``T`` event in state ``s1`` event and the
``init`` event needed in ``s2``:

.. code-block:: python
  :emphasize-lines: 43-44, 71-72

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def s1_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      a(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.T):
      status = chart.trans(s2_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s11_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status


  @spy_on
  def s2_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(s21_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s21_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status

.. _scribbleexample-from-diagram-to-code,-eighth-pass:

Code, See if anything Runs
--------------------------

Now it is time to turn on this hierarchy by giving it to an active object and
seeing what happens:

.. code-block:: python
  :emphasize-lines: 
  :linenos:

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


  @spy_on
  def s1_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      a(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.T):
      status = chart.trans(s2_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s11_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status


  @spy_on
  def s2_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(s21_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s21_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status


  if __name__ == "__main__":
    ao = ActiveObject(name="T_question")
    ao.start_at(s11_state)
    time.sleep(0.1)
    pp(ao.spy())

Notice, we sleep for a very short time to let the active object thread detect that
it has received an instruction.

.. _scribbleexample-:


When we run this code it outputs:

  .. code-block:: python

    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:s11_state',
     'SEARCH_FOR_SUPER_SIGNAL:s1_state',
     'SEARCH_FOR_SUPER_SIGNAL:s_state',
     'ENTRY_SIGNAL:s_state',
     'ENTRY_SIGNAL:s1_state',
     'ENTRY_SIGNAL:s11_state',
     'INIT_SIGNAL:s11_state',
     '<- Queued:(0) Deferred:(0)']

Good, our start is structured well enough that it can run.  

.. _scribbleexample-from-diagram-to-code,-ninth-pass:

Code, Add the guard and t function
----------------------------------

Now lets add the guard function ``g`` and the ``t`` function into s1_state,
this will build this part of the picture:

.. image:: _static/guard.svg
    :align: center

.. code-block:: python
  :emphasize-lines: 37-42, 50-53

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def s_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def s1_state(chart, e):
    def g(chart):
      chart.scribble("Running g() -- the guard, which returns True")
      return True

    def t(chart):
      chart.scribble("Running t() -- function run on event T")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.T):
      if g(chart):
        t(chart)
        status = chart.trans(s2_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s11_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status


  @spy_on
  def s2_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(s21_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s21_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status


  if __name__ == "__main__":
    ao = ActiveObject(name="T_question")
    ao.start_at(s11_state)
    time.sleep(0.1)
    pp(ao.spy())

The guard condition totally makes sense when you look it it in Python.

Functions ``g`` and ``t`` use the chart's ``scribble`` method which puts little
notes directly into the spy output log.  We do this so that our tests will
reveal exactly when ``g`` and ``t`` are called by the event processor.

.. _scribbleexample-from-diagram-to-code,-tenth-pass:

Code, Add the other functions
-----------------------------

Now let's frame ``a``, ``b``, ``c``, ``d``, ``e``. Notice we re-name the ``e``
function to ``e_function`` to avoid a name collision:

.. code-block:: python
  :emphasize-lines: 37,38,52,65-66,73,82-83, 85-86, 91, 96, 105-106, 111, 124-127
  :linenos:

  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def s_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def s1_state(chart, e):
    def b(chart):
      chart.scribble("Running b()")

    def g(chart):
      chart.scribble("Running g() -- the guard, which returns True")
      return True

    def t(chart):
      chart.scribble("Running t() -- function run on event T")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      b(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.T):
      if g(chart):
        t(chart)
        status = chart.trans(s2_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s11_state(chart, e):
    def a(chart):
      chart.scribble("Running a()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      a(chart)
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status


  @spy_on
  def s2_state(chart, e):
    def c(chart):
      chart.scribble("running c()")

    def d(chart):
      chart.scribble("running d()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      c(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      d(chart)
      status = chart.trans(s21_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status


  @spy_on
  def s21_state(chart, e):
    def e_function(chart):
      chart.scribble("running e()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      e_function(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status


  if __name__ == "__main__":
    ao = ActiveObject(name="T_question")
    ao.start_at(s11_state)

    ao.clear_spy()
    ao.post_fifo(Event(signal=signals.T))
    time.sleep(0.1)
    pp(ao.spy())

Challenging Our Hypothesis
--------------------------
Let's bring our question and our hypothesis back into view so we can think
about it again:

"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

Our answer:
``if g() returns True, then the function order will be:`` ``g``, ``a``, ``b``, ``t``, ``c``, ``d``, ``e``

Let's examine my own personal psychological state.  I have been taking tiny
steps to keep my cognitive load light, and right now I'm feeling pretty good.
I have a theory, but more importantly I have built up some firm reality outside
of myself that I can push against.  My sense of possession has transfered from
my answer into the structure that will be used to attack this answer.

Moreover, I feel a sense of control and I'm feeling satisfaction from building
something.  The part of my mind that gets a buzz from pursuit, from seeking is
activated and I'm feeling ready to grok something about these statecharts.  

If you have actually been doing the work and debugging your own code, well,
maybe you feel this too.

Now, let's pull the trigger and see what happens.

.. code-block:: python
  :emphasize-lines: 3,4, 6, 11, 13, 15, 18

  ['T:s11_state',
   'T:s1_state',
   'Running g() -- the guard, which return True',
   'Running t() -- function run on event T',
   'EXIT_SIGNAL:s11_state',
   'Running a()',
   'SEARCH_FOR_SUPER_SIGNAL:s11_state',
   'SEARCH_FOR_SUPER_SIGNAL:s2_state',
   'SEARCH_FOR_SUPER_SIGNAL:s1_state',
   'EXIT_SIGNAL:s1_state',
   'Running b()',
   'ENTRY_SIGNAL:s2_state',
   'running c()',
   'INIT_SIGNAL:s2_state',
   'running d()',
   'SEARCH_FOR_SUPER_SIGNAL:s21_state',
   'ENTRY_SIGNAL:s21_state',
   'running e()',
   'INIT_SIGNAL:s21_state',
   '<- Queued:(0) Deferred:(0)']

Look, it's different.  We got an order of: ``g``, ``t``, ``a``, ``b``, ``c``,
``d``, ``e``.  

The answer:
``g``, ``t``, ``a``, ``b``, ``c``, ``d``, ``e``.

Now let's see what happens when we adjust the ``g`` function to return a False:

.. code-block:: python

  ['T:s11_state',
   'T:s1_state',
   'Running g() -- the guard, which return False',
   '<- Queued:(0) Deferred:(0)']

Now that we understand that, let's re-ask the question:

"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

1. If g() returns False, only ``g`` is called
2. If g() returns True, then ``g``, ``t``, ``a``, ``b``, ``c``, ``d``, ``e``.

We know this, because we just confirmed the behavior.

Learning for my Mistake
-----------------------

If you are deeply familiar with the UML specification for statecharts, you will
see that our observed behavior is an infraction.  The original answer was
supposed to describe the behavior.  The good news is that this event processor
algorithm is based on the work of Miros Samek.

.. image:: _static/scribble.svg

On pages 80-81 of his book titled `Practical UML Statecharts in C/C++ Second
Edition`_ he wrote:

    One big problem with UML transition sequence is that it requires executing
    actions associated with the transition `after` destroying the source state
    configuration but before creating the target state configuration.  In the
    analogy between exit actions in state machines and destructors in OOP, this
    situation corresponds to executing a class method after partially destroying an
    object.  Of course, such action is illegal in OOP.  As it turns out, it is also
    particularly awkward to implement for state machines.

    Executing actions associated with a transition is much more natural in the
    context of the source state -- the same context in which the guard condition is
    evaluated.  Only after the guard and the transition actions execute, the source
    state configuration is exited and the target state configuration is entered
    `atomically`.  That way the state machine is observable only in a safe state
    configuration, either before or after the transition, but not in the middle.

So, our ``t`` function runs within the context of the thing that asked for the
transition.  This keeps it out of the strange limbo state described above.

Let's think about how we could re-adjust our thinking, by re-asking the
question and considering how we could approach it the next time we see
something like it.

"Suppose we started the above chart in ``s11``, then we send a ``T`` event to it,
when would each of the functions, ``a``, ``b``, ``c``, ``d``, ``e``, ``g``, and ``t`` happen?"

.. image:: _static/scribble.svg

Knowing that the source state of our ``T`` event was **s11** you would first
re-imagine the diagram as:

.. image:: _static/scribble2.svg

Then the answer to the question would just reveal itself from your imagined diagram:

* ``g``, ``t``, ``a``, ``b``, ``c``, ``d``, ``e`` if ``g`` returns True
* ``g`` if ``g`` returns False

:ref:`back to examples <examples>`

.. _Practical UML Statecharts in C/C++ Second Edition: https://www.amazon.ca/Practical-UML-Statecharts-Event-Driven-Programming/dp/0750687061/ref=sr_1_1?s=books&ie=UTF8&qid=1510515714&sr=1-1&dpID=51Uq%252BHZ9L-L&preST=_SX198_BO1,204,203,200_QL40_&dpSrc=srch

.. [#f1] The S1 rectangle containing the two small rectangles with a line between them is short hand for a composite state 

