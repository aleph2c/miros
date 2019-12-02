.. _othogonalregions-othogonal-regions-with-miros:

Othogonal Regions With Miros
============================

The CSXML standard describes an orthogonal region statechart like this:

.. image:: _static/xml_chart_1.svg
    :target: _static/xml_chart_1.pdf
    :align: center

.. note::

  The parallel CSXML parallel regions document is full of mistakes, but written
  well enough to describe how orthogonal regions should behave.

If a ``to_p`` event is received while in the ``outState`` or any of its childs
states, a transition will occur into the ``p`` orthogonal region.  Instead of
one active state, the statechart will have two active states.  The ``S1 Region``
will initialize itself to the ``S11`` state and the ``S2 Region`` will
initialize itself to ``S21``.  So both ``S11`` and ``S21`` will be active at the
same time.


:ref:`back to examples <examples>`
