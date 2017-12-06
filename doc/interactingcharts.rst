
.. _interactingcharts-interacting-statecharts:

Interacting Statecharts
=======================
Your designs can be significantly simplified if you break them up into separate
active objects, each running in their own thread communicating with one
another using a central dispatcher.  If your statechart is interested in an
event, it can subscribe to it.  If your statechart would like to provide
information to another statechart, it can publish an event.  By separating your
design into separate parts it makes it much easier to test and document.

:ref:`back to examples <examples>`
