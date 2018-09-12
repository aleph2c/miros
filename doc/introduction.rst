  *Decisions without actions are pointless. Actions without decisions are reckless.* 
  
  -- John Boyd

  *Point of view is worth 80 IQ points*

  -- Alan Kay

.. _introduction-introduction:

Introduction
============
Miros is a statechart library written in Python.  A statechart is a hierarchical
state machine (HSM), running within it's own thread.  If you program using
statecharts, you will have the ability to :ref:`quickly translate your design goals into working and robust code <quick-start>`.

An HSM follows an intuitive set of rules called the `Harel formalism
<http://www.inf.ed.ac.uk/teaching/courses/seoc/2005_2006/resources/statecharts.pdf>`_.
This formalism was invented by the mathematician, Dr. David Harel in the 1980s
to help the Israeli air force construct better software for their jet fighters.

His innovation was to take the sentences that you would find in a specification
and quickly translate them into an easily understood picture.

These pictures reduce the cognitive load you experience while designing and
building your system.  Think about how hard it would be to perform a double
digit multiplication problem using Roman numerals, whereas the same problem can
effortlessly be done by a child in grade 3 using Arabic numbers.  A hard
problem can be transformed into an easy problem by using the correct type of
abstraction.

If you use this library you do not have to write your own state-machine event
processing engine.  It is provided, batteries included.  The library is named,
miros, in honour of the person who wrote it's HSM event processing algorithm,
used by its event processing engine; `Dr. Miro Samek`_.


.. note:: 

  In fact the whole miros library has been constructed to help send some
  business Miro's way.  He runs an embedded consulting company call Quantum
  Leaps.  If you write code using this library, it should be fairly straight
  forward to port it to c/C++ if you would like to transfer your design to his
  `QP framework`_ (for a huge performance gain).

The miros package is not a drawing tool.  It is a way to express your drawings
as running software.  There are a lot of open source drawing tools that can be
used to draw your statecharts.  I use a tool called `UMLet`_.

This package is only dependent upon the Python standard library.

I have tried to document this project so that you can learn how to:
  * translate your design goals into statechart pictures
  * program these pictures in Python so that they will use the Harel
    formalism.
  * use the various statechart patterns, or idioms.
  * reflect upon the behavior of your state machines
  * create federations of statecharts that work together
  * to test your work

If you would like to network your statechart, you can use the `miros-rabbitmq
<https://aleph2c.github.io/miros-rabbitmq/index.html>`_ plugin.

.. raw:: html

  <a class="reference internal" href="installation.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="quickstart.html"><span class="std std-ref">next</span></a>


.. literalinclude:: ./../miros/hsm.py
   :pyobject: HsmEventProcssor.dispatch

.. _QP framework: http://www.state-machine.com/
.. _Dr. Miro Samek: https://www.linkedin.com/in/samek
.. _UMLet: http://www.umlet.com

.. toctree::
   :maxdepth: 2
   :caption: Contents:


