Introduction
============
Miros is a statechart library written in Python.  Statecharts are a type of
behavioral drawing.

These drawings use a kind of formalism that was invented by David Harel in the
1980s when he was trying to help the Israeli air force construct software for
their jet fighters.  

Once you understand how to draw these types of pictures, you can pack a
tremendous amount of behavioral complexity into them. These pictures will
reduce the cognitive load you experience while designing and building your
system.  Think about how hard it would be to perform a double digit
multiplication problem using Roman numerals, whereas the same problem can be
performed effortlessly using Arabic numbers by a child in grade 3.  A hard
problem can be transformed into an easy problem by using a better point of
view.

**Point of view is worth 80 IQ points** -- *Alan Kay*

This of course can be taken too far, as we saw with the failure of UML in the
late 1990's.

As a library, Miros provides most of the features expected to express your
Harel statechart pictures in running software.  The same pictorial formalism is
used by industrial software frameworks like Matlab, IBM rational rose and Miro
Samek's quantum programming platform for embedded systems.  So, you can quickly
prototype your ideas using this library in Python, then port your work into
production code if you need the performance such systems provide.  Or you can
use it as the reactive portion of your Python project.

Miros is not a drawing tool.  It is a way to express your drawing as running
software.  The Harel drawing formalism is simple enough to be expressed on a
napkin, or a piece of paper -- both of which are excellent technologies for
expressing a Harel statechart.

If you are unfamiliar with how to draw Harel statecharts, I recommend that you
read the :ref:`quick-start` section.  There I will describe a system that you already
understand as a statechart, then go through how to express that thing using the
miros library.

If you already know what statecharts are and you just want to see how to use
this library, jump to the :ref:`examples` section.  There I create a simple statechart
and show how to build it. Then I go into great detail about how to reflect upon its
behavior as you make it react to events.

If you know how to use the library, can just need to know to implement
something using a programming example, jump to the :ref:`recipes` section.  It
contains examples of the small lego blocks you will need to build up your
structure.

If you would like to expand your architectural abilities, read the patterns
section.

The library is called miros in honor of Dr. Miro Samek who has written so much
about how to implement such systems.  The event processor within this library
is based on his publications.

.. _QP framework: http://www.state-machine.com/
.. _Dr. Miro Samek: https://www.linkedin.com/in/samek

.. toctree::
   :maxdepth: 2
   :caption: Contents:
