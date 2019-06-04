  *Decisions without actions are pointless. Actions without decisions are reckless.* 
  
  -- John Boyd

  *Point of view is worth 80 IQ points*

  -- Alan Kay

.. _introduction-introduction:

Introduction
============
Miros is a statechart library written in Python.  A statechart is a
`hierarchical state machine (HSM)
<https://en.wikipedia.org/wiki/UML_state_machine>`_, running within it's own
thread.  If you program using statecharts, you will have the ability to :ref:`quickly
translate your design goals into robust working code <quick-start>`.

The problem with most software systems is that they are too complex to
understand without a picture.  The lion's share of a programmer's time is spent
troubleshooting their software, instead of adding working features.  This
is because it's difficult to see how a specific portion of code interacts with
the overall design.  Most developers are in the dark, armed only with a flashlight.

Let's turn the light on.  We can start by drawing pictures in a way that we can
see the full system at once while allowing other people to understand our
thinking.  The pictures will guide how we write our code.

But we tried this before in the 1990s with `UML (Universal Modeling Language)
<https://en.wikipedia.org/wiki/Unified_Modeling_Language>`_.  The group behind
this movement promised systems understanding through pictures.  To do this they
pulled together 14 different ways that people were drawing software systems
under one standard.

Then the movement lost momentum, because they drew the wrong pictures: they
emphasized class diagrams instead of statechart diagrams.  Then they tried to
take over programming entirely with pictures, instead of letting the pictures
act as guidance for thinking and communicating designs.  They ended up
separating the people who drew pictures from the people who wrote the code.  The
language around diagramming techniques became so flowery that only the people
drawing the images understood what they meant.

But amoungst the rubble of this failed movement are some useful gems.  In this
documentation we will use the good parts of UML.  We won't become enamored with
our pictures, but keep them small and easy to change.

To use this library is to program in Python, not pictures; so there is no
picture-to-code compiler here.  This means you can use whatever picture drawing
technology you want, from a napkin to `UMLet`_... it's up to you.

We will learn some simple, formal rules for drawing statecharts. These drawing
rules will help us draw our ideas with a picture and then link that picture to
our code.  The same rules will describe how our code is expected to interact
with the world.  These statechart drawing and behavioral rules are called the
`Harel formalism
<http://www.inf.ed.ac.uk/teaching/courses/seoc/2005_2006/resources/statecharts.pdf>`_,
named after `Dr. David Harel`_, a mathematician who invented the statechart in
1987 at the request of the Israeli airforce.  The statechart picture is only 1
of the 14 UML drawing types.

In the early 2000s `Dr. Miro Samek`_ implemented a statechart framework in
c/C++.  As a firmware developer Dr. Samek ran into the tight memory and
processing constraints that confine a developer while they write code for small
processors.  He refactored the Harel formalism to be more performant and then he
published a core part of the algorithm that lets a statechart designer translate
their picture into working code: the event processing algorithm.

This library uses Miros Samek's event processing algorithm and this is why it is
called miros.

.. note:: 

  If you would like to translate your design into Miro Samek's `QP framework`_
  (for a huge performance gain), it should be fairly straight forward to port
  your Python code to c/C++.

As the author of this library I can't expect you to know UML.  So I will include
instructions on how to draw enough of these pictures to help guide your
thinking.

I will explain how statecharts work, and what they are, then I will show you how
to use this library to program with them.

This package is only dependent upon the Python standard library.

From this documentation you can learn how to:
  * understand how statecharts work
  * translate your design goals into statechart pictures
  * quickly look up the specifics about how to do something
  * have a set of examples to work from
  * reflect upon the behavior of your state machines
  * test your code
  * create federations of statecharts that work together

If you would like to network your statecharts, you can use the `miros-rabbitmq
<https://aleph2c.github.io/miros-rabbitmq/index.html>`_ plugin.

.. raw:: html

  <a class="reference internal" href="installation.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="quickstart.html"><span class="std std-ref">next</span></a>


.. literalinclude:: ./../miros/hsm.py
   :pyobject: HsmEventProcssor.dispatch

.. _QP framework: http://www.state-machine.com/
.. _Dr. Miro Samek: https://www.linkedin.com/in/samek
.. _UMLet: http://www.umlet.com
.. _Dr. David Harel: https://en.wikipedia.org/wiki/David_Harel
.. toctree::
   :maxdepth: 2
   :caption: Contents:


