  *Decisions without actions are pointless. Actions without decisions are reckless.* 
  
  -- John Boyd

.. _introduction-introduction:

Introduction
============

Miros is a statechart library written in Python.  Statecharts are a type of
behavioral drawing.

These drawings use a kind of formalism that was invented by Dr. David Harel in
the 1980s to help the Israeli air force construct better software for their jet
fighters.

His innovation was to take the sentences that you would find in a specification
and quickly translate them into an easily understood picture.  These pictures
were different from the other types of technical drawings that were used at the
time.  You could pack a lot more complexity into them, all the while keeping
them from needlessly spreading over multiple pages and becoming more
complicated than the code that they were suppose to describe.

The diagrams were easy to explain and they were easy to turn into software.

For this reason statecharts have been used to:

1. Allow software to write itself to automatically find better software algorithms
2. Describe the quantum interactions of atoms
3. :ref:`Create infinitely-expensive-engineering-systems (F22/F35)<on-firmware>`
4. :ref:`Design toaster ovens<quick-start>`
5. :ref:`Control Fusion Reactors<nuclear_fusion_example>`

These pictures will also reduce the cognitive load you experience while designing
and building your system.  Think about how hard it would be to perform a double
digit multiplication problem using Roman numerals, whereas the same problem can
be performed effortlessly using Arabic numbers by a child in grade 3.  A hard
problem can be transformed into an easy problem by using a better point of
view.

  **Point of view is worth 80 IQ points** 
  -- *Alan Kay*

As a library, Miros provides most of the features expected to express your
Harel statechart pictures in running Python software.  The same pictorial
formalism is used by industrial software frameworks like Matlab and Miro
Samek's `QP framework`_ for embedded systems.  So, you can quickly prototype
your ideas using this library in Python, then port your work into compiled
production code if you need the performance such systems provide.  Or you can
use it as the reactive portion of your Python project while still having access
to the legion of other libraries written in Python.

Miros is not a drawing tool.  It is a way to express your drawing as running
software.  The :term:`Harel drawing formalism<Harel Formalism>` is simple
enough to be expressed on a napkin, or a piece of paper -- both of which are
excellent technologies for expressing a Harel :term:`statechart<Statechart>`.

The :term:`Harel Formalism<Harel Formalism>` for drawing
:term:`statecharts<Statechart>` was digested by the UML standard in the 1990s.
Though, :term:`UML<UML>` itself has proved to be an overcomplicated failure,
but there are parts of it that are useful.  The statechart formalism and
resulting sequence diagrams turn out to be in the good parts of UML.  If you
need to describe your designs in pictures, you can use a UML tool to draw your
statecharts and import them into your documents.  I use a simple and free
drawing tool called `umlet`_.

If you are unfamiliar with how to draw Harel :term:`statecharts<Statecharts>`,
I recommend that you read the :ref:`quick start<quick-start>` section.  There I
will describe a system that you already understand as a
:term:`statechart<Statechart>`, then go through how to express that thing using
the miros library.

If you already know what :term:`statecharts<Statechart>` are and you just want
to see how to use this library, jump to the :ref:`examples<examples>` section.
There I create a number of simple statecharts and show how to build them. Then
I go into greater detail about how to reflect upon their behavior as you make
it react to events.

If you know how to use the library and just need to know how to implement
something using a programming example, jump to the :ref:`recipes<recipes>`
section.  It contains examples of the small lego-blocks you will need to build
up your structure.

If you would like to expand your architectural abilities, read the
:ref:`patterns<patterns>` section.

The library is called miros in honor of `Dr. Miro Samek`_ who has written so
much about how to implement such systems.  The event processor within this
library is based on his publications.  This should make it easy to use the
miros library for prototyping, or testing a `QP framework`_.

:ref:`Next topic<quick-start>`.

.. literalinclude:: ./../miros/hsm.py
   :pyobject: HsmEventProcssor.dispatch

.. _QP framework: http://www.state-machine.com/
.. _Dr. Miro Samek: https://www.linkedin.com/in/samek
.. _umlet: http://www.umlet.com

.. toctree::
   :maxdepth: 2
   :caption: Contents:


