Introduction
============
Miros is a statechart library written in Python.  Statecharts are a type of
behavioral drawing.

These drawings use a kind of formalism that was invented by Dr. David Harel in
the 1980s when he was trying to help the Israeli air force construct software
for their jet fighters.

His innovation was to take the sentences that you would find in a specification
and quickly translate them into an easily understood picture.  These pictures
were different from the other types of technical drawings that were used at the
time.  You could pack a lot more complexity into them, all the while keeping
them from needlessly spreading over multiple pages and becoming more
complicated than the code that they were suppose to describe.

Once you understand how to draw these types of pictures, you can pack a
tremendous amount of behavioral complexity into them. These pictures will
reduce the cognitive load you experience while designing and building your
system.  Think about how hard it would be to perform a double digit
multiplication problem using Roman numerals, whereas the same problem can be
performed effortlessly using Arabic numbers by a child in grade 3.  A hard
problem can be transformed into an easy problem by using a better point of
view.

**Point of view is worth 80 IQ points** -- *Alan Kay*

As a library, Miros provides most of the features expected to express your
Harel statechart pictures in running Python software.  The same pictorial
formalism is used by industrial software frameworks like Matlab, IBM rational
rose and Miro Samek's `QP framework`_ for embedded systems.  So, you can
quickly prototype your ideas using this library in Python, then port your work
into compiled production code if you need the performance such systems provide.
Or you can use it as the reactive portion of your Python project.

Miros is not a drawing tool.  It is a way to express your drawing as running
software.  The Harel drawing formalism is simple enough to be expressed on a
napkin, or a piece of paper -- both of which are excellent technologies for
expressing a Harel statechart.

The Harel formalism for drawing statecharts was digested by the UML standard in
the 1990s.  Though, UML itself has proven to be an overcomplicated failure,
there are parts of it that are useful.  The statechart formalism and resulting
sequence diagrams turn out to be in the good parts of UML.  If you need to
describe your designs in pictures, you can use a UML tool to draw your
statecharts and import them into your documents.  I use a simple and free
drawing tool called `umlet`_.

If you are unfamiliar with how to draw Harel statecharts, I recommend that you
read the :ref:`quick-start` section.  There I will describe a system that you
already understand as a statechart, then go through how to express that thing
using the miros library.

If you already know what statecharts are and you just want to see how to use
this library, jump to the :ref:`examples` section.  There I create a number of
simple statecharts and show how to build them. Then I go into great detail about
how to reflect upon their behavior as you make it react to events.

If you know how to use the library and just need to know how to implement something
using a programming example, jump to the :ref:`recipes` section.  It contains
examples of the small lego blocks you will need to build up your structure.

If you would like to expand your architectural abilities, read the patterns
section.

The library is called miros in honor of `Dr. Miro Samek`_ who has written so much
about how to implement such systems.  The event processor within this library
is based on his publications:

.. literalinclude:: ./../miros/hsm.py
   :pyobject: HsmEventProcssor.dispatch

.. _QP framework: http://www.state-machine.com/
.. _Dr. Miro Samek: https://www.linkedin.com/in/samek
.. _umlet: http://www.umlet.com

.. toctree::
   :maxdepth: 2
   :caption: Contents:
