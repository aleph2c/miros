.. _reflection

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Reflection
==========

:ref:`reflection-what-state-am-i-in?`

:ref:`What happened? Summarized.<reflection-a-high-level-description-of-the-behavior>`

:ref:`What happened? Detailed. <reflection-an-extremely-detailed-view>`

:ref:`What is happening now?<reflection-live-output-from-your-chart>`

:ref:`How can I test this behavior?<reflection-how-to-test-using-reflection>`

:ref:`How can I explain this to others?<reflection-how-to-explain-your-design-to-others>`

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

.. include:: i_determining_the_current_state.rst 

.. _reflection-a-high-level-description-of-the-behavior:

A High Level Description of The Behavior
----------------------------------------

.. include:: i_trace_reactive.rst 

An Extremely Detailed View of the Behavior
------------------------------------------

.. include:: i_spy_reactive.rst

.. _reflection-how-to-test-using-reflection:

How to Test Your Design Using Reflection
----------------------------------------

.. _reflection-testing-with-the-trace-output:

Testing with the Trace Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_test_with_trace.rst

.. _reflection-testing-with-the-spy-output:

Testing with the Spy Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: i_test_with_spy.rst

.. _reflection-live-output-from-your-chart:

Live Output From Your Chart
---------------------------

.. _reflection-how-to-explain-your-design-to-others:

How to Explain your Design to Others
------------------------------------

.. include:: i_making_sequence_diagrams_from_trace.rst

.. _umlet: http://www.umlet.com
