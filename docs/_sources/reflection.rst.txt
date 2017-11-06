.. _reflection

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Reflection
==========

:ref:`reflection-what-state-am-i-in?`

:ref:`reflection-a-high-level-description-of-the-behavior`

:ref:`reflection-an-extremely-detailed-view`

:ref:`reflection-live-output-from-your-chart`

:ref:`reflection-how-to-test-using-reflection`

:ref:`reflection-creating-a-sequence-diagram`

.. _reflection-thoughts-on-reflection:

Thoughts On Reflection
----------------------

The `miros` framework has several different mechanisms to view how your design
behaves.  This is extremely important, since with the compacting of complexity
into behavioral maps it is very easy to lose track of what your system actually
does.  In fact, it is inevitable that for any moderately ambitious design, you
will not be able to track the entirety of its behavior in your head.  With any
addition of state or event management there is an exponential increase in the
number of possible stories your chart can tell.  This is the power and the
curse of a statechart.

The state of your chart might change as it responds to an event, so you might
want to :ref:`reflect upon the current state<reflection-what-state-am-i-in?>`.

You might want to view :ref:`what events caused what state transitions from a
high level<reflection-a-high-level-description-of-the-behavior>`.

:ref:`You may need to view the state dynamics in fine detail. 
<reflection-an-extremely-detailed-view>`.

:ref:`If you have a number of charts running in parallel, you may want to see how
they interact in a live manner.<reflection-live-output-from-your-chart>`

The tools needed to view these dynamics are embedded into the `miros` framework.

Another issue that is faced is how to explain your design to someone else.  A
statechart diagram is not helpful when you are talking to a customer or someone
within your team who is not versed in Harel formalism.  For this reason, it is
good to talk about a specific behavior, not all of the behaviors at once.  A
statechart diagram might make sense to you but it can psychologically shutdown
a teammate.  `miros` :ref:`provides a way to translate how your chart responds
to a particular event into a different type of diagram, a sequence
diagram<reflection-creating-a-sequence-diagram>`.  Anyone can understand a
sequence diagram.  By referencing something that is easy to understand you can
reduce the transaction costs in your organization; everyone should be able to
participate in the conversation.

With the smallest adjustment of a statechart, all of your sequence diagrams can
become moot.  For this reason the sequence diagrams can be generated
programatically from the trace output.  This means that you don't have to waste
expensive engineering time on documentation that will be thrown away as you
build out your system.  This is also important because your engineers won't
become reluctant to change a design to avoid hours and hours of grinding work.

I would recommend that if you use statecharts, you avoid using non-text based
documentation systems.  If you use Word to make pretty diagrams, the steps to
manually change your documents will amplify cost through your organization.
Whereas if you use markdown, LaTeX, HTML, anything that can quickly be
constructed without a lot of user intervention, it is easy and cheap to change
your design descriptions.  If you want to buy a Microsoft product, buy Visio,
since you can make beautiful diagrams with links.  It makes sense to put a lot
of time and attention into the map.  To save money, you can use `umlet`_
instead.

Suppose you are a documentation genius.  This doesn't mean that anyone wants to
read your work.  With the `miros` reflection features an engineer can run an
experiment to see how the system actually behaves, rather than digging into
dreary specifications.  The chart will quickly become the specification, this
is the point of Harel formalism.  The specification documents can be thought of
as temporary work orders that adjust the global specification, the chart
itself.

As your system gets bigger and more complicated, it is very important to lock
it down with tests.  But the more specific the test, the more tightly coupled
it is to your design.  Any change will break it.  To fix things an engineer
could isolate the test, reflect upon the behavior, determine if it is correct
by carefully thinking about it, then overwrite the test with a copy of the
reflection.  :ref:`It has to be very easy and cheap to isolate and update your tests
<reflection-how-to-test-using-reflection>`,
otherwise your organization will lose this discipline and you will lose control
of your design.

.. _reflection-what-state-am-i-in?:

What State Am I In?
-------------------
To see what state your chart is in:

.. code-block:: python
  :emphasize-lines: 1
  :linenos:

    chart.state.fun           # will be the state method
    chart.start.fun.__name__  # will be the state method name


.. _reflection-a-high-level-description-of-the-behavior:

A High Level Description of The Behavior
----------------------------------------
If you would like to see what your active object is doing from a very high
level, you can look at it's `trace` instrumentation.  The trace will only
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

An Extremely Detailed View of the Behavior
------------------------------------------


.. _reflection-how-to-test-using-reflection:

How to Test Using Reflection
----------------------------

.. _reflection-live-output-from-your-chart:

Live Output From Your Chart
---------------------------

.. _reflection-creating-a-sequence-diagram:

Creating a Sequence Diagram
---------------------------




.. _reflection-how-to-explain-your-design-to-others:

How to Explain your Design to Others
------------------------------------
Once your design reaches a moderate level of complexity, you will not be able
to explain it to people who are not technical.  At some point, you too will lose
track of how your system behaves.  You will have to study and probe your design
to see how it works.  For this reason it is extremely important to build up
regression tests as you work on your system.


.. code-block:: python
  :emphasize-lines: 1
  :linenos:
        
    [05:43:06.135566] [75c8c] e->None() top->arming
    [05:43:06.254068] [75c8c] e->BATTERY_CHARGE() arming->armed
    [05:43:06.354835] [75c8c] e->BATTERY_CHARGE() armed->armed
    [05:43:06.456146] [75c8c] e->BATTERY_CHARGE() armed->armed
    [05:43:06.553918] [75c8c] e->CAPACITOR_CHARGE() armed->tazor_operating
    [05:43:06.554796] [75c8c] e->CAPACITOR_CHARGE() tazor_operating->tazor_operating
    [05:43:06.555828] [75c8c] e->CAPACITOR_CHARGE() tazor_operating->tazor_operating

    [ Chart: 75c8c ] (?)
             top                arming                armed           tazor_operating   
              +------None()------->|                    |                    |
              |        (?)         |                    |                    |
              |                    +-BATTERY_CHARGE()-->|                    |
              |                    |        (?)         |                    |
              |                    |                    +                    |
              |                    |                     \ (?)               |
              |                    |                     BATTERY_CHARGE()    |
              |                    |                     /                   |
              |                    |                    <                    |
              |                    |                    +                    |
              |                    |                     \ (?)               |
              |                    |                     BATTERY_CHARGE()    |
              |                    |                     /                   |
              |                    |                    <                    |
              |                    |                    +-APACITOR_CHARGE()->|
              |                    |                    |        (?)         |
              |                    |                    |                    +                    
              |                    |                    |                     \ (?)               
              |                    |                    |                     CAPACITOR_CHARGE()  
              |                    |                    |                     /                   
              |                    |                    |                    <                    
              |                    |                    |                    +                    
              |                    |                    |                     \ (?)               
              |                    |                    |                     CAPACITOR_CHARGE()  
              |                    |                    |                     /                   
              |                    |                    |                    <                    
    
    



.. _umlet: http://www.umlet.com
