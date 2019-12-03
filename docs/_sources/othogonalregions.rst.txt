.. _othogonalregions-othogonal-regions-with-miros:


`example <https://github.com/aleph2c/miros/blob/master/examples/xml_chart.py>`_


Orthogonal Regions
==================

It goes without saying that we need to comprehend our designs.  We must know
what we are building, and we must find a abstractions which make it possible to
discuss what we are doing with others.

But as your designs get more complicated you will experience **state space
explosion**:  The number of states that are needed to make your system work, mix
together combinatorially so that it becomes impractical to comprehend all paths
of possible behavior.

Another way of describing the problem is that the state space gets so large that
you can't comprehend it using your chosen design abstraction.  This is
especially true if you are using a finite statemachine as your main design tool.
You can hold off the effects of **state space explosion** by switching to a
hierarchical state machine approach; common behaviors are mapped into outer
states making a design more comprehensible, but this can only take you so far.
At some point you must chunk your design into concurrent pieces which interact.
Each piece being something you can comprehend and trust to work on its own.

David Harel's original statechart paper addressed state space explosion by
inventing the notion of the **orthogonal region**.  Orthogonal regions describe
concurrency *within* an HSM.  

The orthogonal region abstraction was not supported in Miro Samek's statechart
algorithm for performance reasons.  Instead he offered up :ref:`orthogonal
components <patterns-orthogonal-component>`; HSMs acting as variables within
other HSMs.

In this example I will show you what an orthogonal region is and why you would
use it. Then we will map the orthogonal region behavior into a python program
using the existing miros features.  We will be using the :ref:`orthogonal
components <patterns-orthogonal-component>` mixed with a Factory to satisfy a
behavioral description written as part of the `SCXML standard
<https://www.w3.org/TR/scxml/>`_.

Packing a design into a suitable theory is a strategic effort.  Every good
strategy needs supporting tactics and in this case we need to provide our
engineers with the means to see what their code does once it is written.  So our
example will be instrumented.

----

The SCXML standard describes an orthogonal region statechart similar to this:

.. image:: _static/xml_chart_1.svg
    :target: _static/xml_chart_1.pdf
    :align: center

.. note::

  Click the above diagram to see a larger version.

  The parallel `CSXML parallel regions document
  <https://www.w3.org/TR/scxml/#CoreIntroduction>`_ is full of mistakes, but
  written well enough to describe how orthogonal regions should behave.


Let's break the above UML diagram away from its supporting `xml
<https://github.com/aleph2c/miros/blob/master/examples/xml_chart.xml>`_:

.. image:: _static/xml_chart_2.svg
    :target: _static/xml_chart_2.pdf
    :align: center

The dotted line describes two orthogonal regions within the ``p`` state which
will both become active when the ``p`` state is entered.  This means that
``S11`` and ``S21`` will both become active states.  In the case that the
statechart immediately receives a ``to_outer`` event while in the ``p`` state,
the exit behavior in both orthogonal regions will be followed until the ``p``
state is exited: ``S11`` exit code will run and the ``S21`` exit code will run.

The power of the orthogonal region comes from it's multiplicative feature.  The
number of state combinations within ``p`` is the product of the number of states
in each region: ``3*3 = 9`` (counting the final pseudostates).  

.. note::

   This multiplicative property holds true for any concurrency
   mechanism, whether it be concurrent statecharts or with the orthogonal
   component pattern.

The benefit of how David Harel describes things is how nicely it can be drawn
onto a diagram.  To have concurrency (with it's multiplicative ability to
compact design complexity) in part of the design while having it go away in
another part of the design is a beautiful form of compression.

If you take the time to read the `expected behavior for orthogonal region in the
CSXML standard <https://www.w3.org/TR/scxml/#CoreIntroduction>`_ you will see
that a "final" event can be defined when all of the regions within ``p`` have
entered their final state (the circle with the black dot).  The diagram's
``p_final`` arrow describes what should happen when both the ``S1`` and ``S2``
regions have finished.



:ref:`back to examples <examples>`
