.. _reading_diagrams-reading-diagrams:

  *If I can't picture it, I can't understand it* 
  
  -- Albert Einstein

Diagrams
========

In the 1990s a number of people got together an collected all of the different
popular ways of drawing pictures of software into one standard called UML
(unified modeling language).  The Harel formalism (the way David Harel wanted us
to draw statecharts) was included in UML.

Unfortunately, UML has fallen out of favor because the committee controlling it
produced something that the software community didn't want.  There are many
different reasons for this, but it is safe to say that it is no longer popular.
In fact, UML, in some ways, has become a kind of anti-brand.

But they left behind some useful technology.  A number of open source
diagramming tools still exist with which we can quickly draw our statecharts.

Martin Fowler rendered down the complexity of the UML standard into : `UML
distilled <https://martinfowler.com/books/uml.html>`_.  If you want a very solid
understanding about Harel formalism as it relates to UML, go to the source and
read `Practical UML Statechart in C/C++, 2nd Edition
<https://sourceforge.net/projects/qpc/files/doc/PSiCC2.pdf/download>`_ by Miro
Samek.

But do you need to read these books before you use UML?  No, not really, this
section should give you enough information so that you can make your own
pictures.

At some point another attempt will be made to standardize the current best
practices for diagramming our software systems.  Maybe it will incorporate all
of the new programming idioms.  Until then we can limp along with UML.

.. _reading_diagrams-a-warning-about-diagramming:

A Warning about Diagramming
---------------------------
Be aware that as you draw your pictures, you will lock-in your thinking.

You and everyone on your team will be effected by the Sunk Cost Fallacy:  "Your
decisions are tainted by the emotional investments you accumulate, and the more
you invest in something the harder it becomes to abandon". [#]_  

If you build beautiful drawings with a graphic design application; you will need
to put time and effort into them and you will probably become emotionally
attached to them.  Remember, your diagrams are just mistakes in the right
direction.  You need to be able to destroy these pictures, just as casually as
you would refactor your code.

So use a simple and fast moving tool that almost draws the pictures for you; I
use UMLet.  With UMLet you can build custom templates.  `Here is the custom
template I use <https://github.com/aleph2c/umlet-statechart-template>`_.  It is
hard to fall in love with a picture made by UMLet.

You don't have to use this tool or this template, there `a lot of other UML drawing
tools available
<https://en.wikipedia.org/wiki/List_of_Unified_Modeling_Language_tools>`_.

Another way to make your pictures easy to change is to limit the amount of
detail on them.  You don't have to draw every class and you can shrink a
complicated statechart into a kind of short hand.

UML can't begin to describe what you write with your Python code.  So, if you
need to express a code's idea on the diagram, just write the code directly onto
the picture.

.. _reading_diagrams-classes:

Classes
-------
The class is a blueprint for an object.

Typically, your class diagram would have a name and it would describe the
important variables (attributes) and functions (methods) of your class.  I tend
to put a little line between these when I'm diagramming them.

.. image:: _static/class_1.svg
    :target: _static/class_1.pdf
    :align: center

If your class inherits from another class, you draw it with the inheritance
arrow (the ToasterOven *is an* ActiveObject):  

.. image:: _static/class_2.svg
    :target: _static/class_2.pdf
    :align: center

.. code-block:: python

  # ...
  class ToaterOven(ActiveObject):
    # ...

If the object that is instantiated from your class, constructs another
object, of another class, you can draw this with the composite arrow (The toaster
oven *has a* light):

.. image:: _static/class_3.svg
    :target: _static/class_3.pdf
    :align: center

.. code-block:: python

  class ToasterOven(ActiveObject):
    def __init__(self):
      self.light = Light()
      # ...

If your object references another object that already exists, you can draw this
with an aggregation arrow (The toaster oven *has a* relay).

.. image:: _static/class_4.svg
    :target: _static/class_4.pdf
    :align: center

.. code-block:: python

  relay = Relay()

  # ...
  class ToasterOven(ActiveObject):
    def __init__(self, relay):
      self.relay = relay
      # ...

  toaster_oven = ToasterOven(relay)

.. _reading_diagrams-backwards-arrows:

Oh, but wait, did you notice the aggregation and composition arrows are
backwards?  This was done for a good reason, the arrow head (diamond looking
thing) is on the side that owns the other thing.  So at a glance you can see who
owns what.

.. image:: _static/arrow_pear.svg
    :target: _static/arrow_pear.pdf
    :align: center


The composite arrow is black because when your object is destroyed, so is the
object that it has built within it.

.. image:: _static/arrow_pear_2.svg
    :target: _static/arrow_pear_2.pdf
    :align: center

These mnemonics should help you when you are diagramming.

.. note::

  These class diagrams are ill conceived since you have to know about all sorts
  of activity in the background before you understand them.  You have to know
  that the relationships are between the objects that are instantiated and not
  the classes themselves.  As Dave Thomas (of Pragmatic fame) says, "[Python] is
  not about class oriented programming, it's an object oriented programming
  language, yet UML draws everything with classes."

  So treat the class diagrams as a quick reference to provide your statechart
  some context, or just a kind of throw away thing.  Use lots of class shorthand
  pictures if you are going to draw a few different classes on the same diagram.
  Your actual classes are well defined in your Python code, so you can use your
  code-tools (ctag/cscope) to see the class hierarchies and who references what
  within your editor.

Martin Fowler spends over two chapters of `UML distilled
<https://martinfowler.com/books/uml.html>`_ writing about class diagrams.  You
can make them really complicated if you want.

If you are using the miros package, you are rightfully managing your system's
complexity using statecharts and not with classes.  So drawing detailed pictures
using class diagrams is not a good use of your time.

.. _reading_diagrams-inheritance:

Inheritance and miros
----------------------
Within the context of this library, you would inherit from either the
ActiveObject or the ActiveFactory to gain access to the event processor, and all
of the other useful methods which would drive your statechart.  Then, you can
either attach this class directly to your statechart, or make an intermediate
class that holds all of your worker-functions for the thing you are trying to
build.

.. image:: _static/class_6.svg
    :target: _static/class_6.pdf
    :align: center

Inheritance is patching.  Patching is easy for a computer to do, but it's a lot
harder for a human mind.  In the 1990's when object oriented programming was
*the* raging fad, the computer science community really over-emphasized this
feature.  We have since learned that inheritance is like any good vitamin, if
you use too much of it, it becomes hazardous to your well-being.

So don't over use inheritance or you will make your code *really* hard to debug
and maintain:

.. image:: _static/class_7.svg
    :target: _static/class_7.pdf
    :align: center

It makes sense to inherit from an ActiveObject or an ActiveFactory, because you
probably have no intention of debugging this library's code.  If you make a
subclass of one of these classes, you can put your specific worker functions and
named attributes in it; but will you ever need to subclass beyond that point?
Probably not; inheritance can get you into a lot of trouble if it's too deep.

If you are going to inherit ask yourself if the "as-a" relationship holds true
when you use the two class names in a sentence.  "The ToasterOven class is an
ActiveObject"; yes, that makes sense.  Ok, I'll use inheritance.

If you want all of the states of your statechart to react the same when they see
a specific event, use the :ref:`ultimate hook pattern <patterns-ultimate-hook>`.
This gives you all of the benefits of inheritance while still having debuggable
code.

.. _reading_diagrams-events:

Events
------
Any code which uses the miros library is event-driven.

This means that your software will be waiting for an occurrence of an event: a
mouse click, a stock price passing a certain threshold, or the arrival of a data
packet.  After recognizing the event your system will react to it, by
manipulating the hardware state or sending further internal events to itself.
After completing the processing of this event in accordance to your design, and
the Harel formalism (the rule book of the board game), the system will stop
processing; and wait for the next event.

An event has a name and an optional payload.  The event's name is called a
signal name.  There are internal signal names, like entry, exit and init (black
dot's on the diagram) and there are external signals; which are just names that
you define to track the real world events that your software is reacting to.

Here is how to make an external event in miros:

.. code-block:: python

  from miros import Event, signals
  from collections import namedtuple

  my_event = Event(signal=signals.MY_EVENT)
  my_event_with_payload = Event(signal=signals.MY_EVENT,
    payload="with a payload that is just a string")

  MouseCoordinate = namedtuple("MouseCoordinates",
    ['x_px','y_px','z_px']

  mouse_click_evt = Event(signal=signals.MOUSE_CLICK,
    payload=(MouseCoordinate(x_px=20, y_px=40, z_pz=30)))

Typically, external events like these come from outside of your statechart, so
you don't have to draw them on your diagram.

The event is like a named marble that can roll on a groove, described by the
arrows of your statechart.  You can think of the groove as being pitched so that
a marble can only roll in one direction.  Any groove can have software written
on it, but this software will only run when a marble rolls over it.  This is how
these grooves can be drawn with UML:

.. image:: _static/Transition_Triggers.svg
    :target: _static/Transition_Triggers.pdf
    :align: center

In English, the above diagram would say, "If I receive an event with a signal
name "SIGNAL_NAME" while I am in source_state, run the guard, if it returns
True, run the action() function within the context of the source state, then add
the EVT_A event to my fifo queue so that it can be run during my next RTC
process, then transition to the target_state, but, if my guard code returns
False, ignore the event and do nothing".

Your event can also run some code without causing a state transition; this is
called a hook:

.. image:: _static/hook_diagram_1.svg
    :target: _static/hook_diagram_1.pdf
    :align: center

In English, the above diagram would say, "If I receive an event with a signal
named "SIGNAL_NAME" while I am in source_state, run the guard, if it returns
True, run the action().  When I have finished running the action, stay in the
source_state.  If the guard returned false, ignore the event."

Now that we understand how to draw external events on our diagrams we will talk
about internal events:

  * entry
  * exit
  * init (the black dot, which means, "Now what?")

The entry and exit internal events, are just hooks:

.. image:: _static/Transition_Triggers_With_Internal_0.svg
    :target: _static/Transition_Triggers_With_Internal_0.pdf
    :align: center

The init internal event is drawn with something that UML calls a pseudostate;
which means a widget on your picture that is not a state.  The init signal is a
black dot connected to an arrow.

.. image:: _static/Transition_Triggers_With_Internal_1.svg
    :target: _static/Transition_Triggers_With_Internal_1.pdf
    :align: center

The internal events are triggered in reaction to transitions made by external
events on your diagram.

.. _reading_diagrams-event-processor-connection:

Event Processor Attachment Points
---------------------------------
The event processor is the rule book for your statechart.  It is the thing that will
cause you to transition from one state to another, it will trigger internal
events and it will read and run all of your code as your code reacts to the
outside world.

To connect the event processor of your object to a statemachine; inherit it into
the class that will solve your problem, then draw the attachment point like this:

.. image:: _static/attachment_point_1.svg
    :target: _static/attachment_point_1.pdf
    :align: center

I'm not sure if I'm using UML properly according to the standard, and I don't
really care.  What I care about is if you understand what I mean.

In the context of this library an object instantiated with an event processor
can attach itself to a statemachine.  Another object instantiated with an event
processor can also attach to the same statemachine.

.. image:: _static/attachment_point_2.svg
    :target: _static/attachment_point_2.pdf
    :align: center

The statemachine doesn't keep track of variables or the current state; it simply
acts as a behavioral specification.  The object that was instantiated from the class
containing the event processor keeps track of it's variable contents and state
information.  This is why the diagram is drawn this way.

.. image:: _static/attachment_point_3.svg
    :target: _static/attachment_point_3.pdf
    :align: center

If you want to embed your state machine within your class, you can, you just
write it's functions as staticmethods.  An embedded state chart might look like
this:

.. image:: _static/attachment_point_4.svg
    :target: _static/attachment_point_4.pdf
    :align: center

As your team gets used to looking at these kinds of diagrams, you might create
a short hand for the attachment point, or leave it off of your diagram all
together.

.. _reading_diagrams-states:

States
------ 
The states in miros are just functions that you write that will react to events
send to them by the event processor.  They will have access to the attributes
and methods of the object that is referencing them, and they will be arranged in
a graph that is interpreted by the event processor (the rule book).  

As a developer, you don't have to solve the problems that the event processor
solves, instead you just learn some simple rules, then write your code into
your statechart functions.  But you don't do this directly in one step, first
you learn how to draw simple pictures that are easy to think about.  Model these
pictures so that they map to your problem then write your code after you have a
decent idea about your design.  These pictures are called state machines, and
they come in many different UML flavors.

The Miro Samek algorithm doesn't really care about the specifics of these
drawing conventions, since it supports finite state machines (with simple
states: Mealy or Moore) and hierarchical state machines (composite states) in
exactly the same way.

Here is a simple state, you would use it when drawing a finite state machine:

.. image:: _static/simple_state_1.svg
    :target: _static/simple_state_1.pdf
    :align: center

Here is an example of a finite state machine (FSM) -- An oven.

.. image:: _static/simple_state_2.svg
    :target: _static/simple_state_2.pdf
    :align: center

Here is a composite state (a state that can have states within it):

.. image:: _static/composite_state_1.svg
    :target: _static/composite_state_1.pdf
    :align: center

Here is a simple hierarchical state machine (HSM) -- A slightly better oven:

.. image:: _static/composite_state_2.svg
    :target: _static/composite_state_2.pdf
    :align: center

I think a lot of the terminology that was invented for UML came from exhausted
committees working on Friday afternoons, minutes before the weekend:  Any
state-looking-widget on your diagram that actually isn't a state, is called a
pseudostate.  For instance, on our diagram, the black initialization dot and the
H with a star beside it (deep history) are both called pseudostates.

If you had to draw your statechart into a diagram that didn't have enough room
for it, you might want to simplify it into a compacted representation.  This
would let the person reading your diagram know that there is more to it, but
that it was simplified on the picture so that everything would fit on the page.
For some reason this is called "decomposition hiding".  I'll demonstrate this by
hiding some of the details of our HSM oven:

.. image:: _static/composite_state_3.svg
    :target: _static/composite_state_3.pdf
    :align: center

The states aren't useful without the assortment of arrows, internal events and
hooks that you will pepper all over your drawing.  In addition to this, there are
UML ways to solve some of the common problems that you will have when you try to
draw how your code works on a diagram.  Read on for the details.

.. _reading_diagrams-if-structures:

If-Else Structures
------------------
If you would like an event to be managed in different ways depending on some
condition, you would use an if-else structure.  In UML your if-else structures look
like diamonds with an event guard written on one of the arrows:

.. image:: _static/if_else_1.svg
    :target: _static/if_else_1.pdf
    :align: center

.. _reading_diagrams-extending-arrows:

Extending Arrows
----------------
Often you will find it tricky to get all of your arrows packed onto your page.
If a number of arrows share the same kind of action, you can "join" them using a
bar:

.. image:: _static/join_1.svg
    :target: _static/join_1.pdf
    :align: center

You can also "fork" them using a bar too:

.. image:: _static/fork_1.svg
    :target: _static/fork_1.pdf
    :align: center

.. _reading_diagrams-terminate-pseudostate:

Terminate Icon
-------------
If you want to destroy your statechart upon reacting to an event, you can use
the terminate pseudostate (icon):

.. image:: _static/terminate_1.svg
    :target: _static/terminate_1.pdf
    :align: center

.. _reading_diagrams-final-state:

Final Icon
----------
If your event has completed all of the work required in the enclose region, you
can draw this with the final state icon:

.. image:: _static/final_1.svg
    :target: _static/final_1.pdf
    :align: center

It might make sense to use this if you want some code to run upon the
initialization of the state, but you do not want to transition deeper into the
state machine:

.. image:: _static/final_2.svg
    :target: _static/final_2.pdf
    :align: center

Fall Through
------------
The miros event handler can do something that I haven't seen specified anywhere,
it can do a kind of catch and release, where an event can be processed by a
state, then released outward into the statechart to be processed by an outer
state.

.. image:: _static/fall_through_1.svg
    :target: _static/fall_through_1.pdf
    :align: center

I draw this with an un-attached arrow.  The arrow has code marked on it, but it
does not connect to anything, to express that it is not locally handled, so that
the event processor will recurse outward in it's search to find where it is
handled.  The action on the unhandled arrow is a kind of side effect that can
provide some useful features.

.. image:: _static/catchandrelease1.svg
    :target: _static/catchandrelease1.pdf
    :align: center

.. note::

  This is not in the UML standard

.. _reading_diagrams-deep-history-dot:

Deep History Icon
-----------------
If an event has caused you to leave a state deeply embedded in your statechart,
but you would like to transition back to that state after the interruption, you
can use the deep history pseudostate, it's a circle enclosing a H*:

.. image:: _static/TransitionToHistoryStatePattern.svg
    :target: _static/TransitionToHistoryStatePattern.pdf
    :align: center

.. _reading_diagrams-publishing-to-other-charts:

Subscription and Publishing Icons
---------------------------------
If you are publishing an event to another chart, it is often very useful to have
your eyes fall on this immediately while looking at your diagram.  It is an
output.  I use a red dot to signify this, red, because the event is currently
stopped, as it is waiting for processing in a queue.

Likewise, if you have subscribed to an event being posted by another chart, it's
often very useful to have your eyes fall immediately on where it is being acted
upon.  It is an input.  I use a green dot, to show that this signal is going, or
being acted upon by the statechart which has subscribed to it

.. image:: _static/pub_sub_icons.svg
    :target: _static/pub_sub_icons.pdf
    :align: center

.. note::

  This is not in the UML standard


.. _reading_diagrams-high-level-dependency-diagrams:

High Level Federation Diagrams
------------------------------
If you have a number of statecharts that are all working together to perform
some sort of collective action, it's often very useful to see how they relate
to one another from a very high point of view.  For this I draw high level
dependency diagrams:

.. image:: _static/context_diagram.svg
    :target: _static/context_diagram.pdf
    :align: center

When I need to write about a specific part of the system, I will change it's
colour to draw my audience's attention.  In this example I am trying to draw
your attention to the CacheFileChart used by the `miros-rabbitmq plugin
<https://aleph2c.github.io/miros-rabbitmq/how_it_works.html>`_.

.. note::

  This is not in the UML standard

.. _reading_diagrams-medium-level-construction-and-pub/sub-diagrams:

Medium Level Construction and Pub/Sub Diagrams
----------------------------------------------
If you have build a federation of statecharts working together, you might want
to look at how a specific statechart works in the context of this federation
without looking at the details of its state machine.  This can be done with a
medium level contextual view.  You would identify what it publishes, what it's
subscribed to and what it constructs to perform it's roll:

.. image:: _static/medium_context_lan_chart.svg
    :target: _static/medium_context_lan_chart.pdf
    :align: center

This is a medium context diagram of the LanChart used by the `miros-rabbitmq plugin
<https://aleph2c.github.io/miros-rabbitmq/how_it_works.html>`_.  It uses two
"has a" composite arrows to show that it builds a CacheFileChart and a
LanRecceChart when it is constructed.  When the LanChart is destroyed, both the
CacheFileChart and the LanRecceChart will be destroyed as well.

We use the publish and subscribe icons to show about events are inputs (green)
and what events are outputs (red).  The payloads of the events are described as
well.  From this diagram we can see how are LanChart chart contributes to the
federation of our design.

What is missing is that the LanChart doesn't describe who constructs it.  I
really shouldn't because it doesn't have access to this information.  To see
this, you would reference the detailed statechart diagram.

.. _reading_diagrams-detailed-statechart-diagrams:

Detailed Statechart Diagrams
----------------------------
The complete statechart is something that shows the topological nature of your
design with code marked upon it so you can quickly scan it and see what it's
doing.  The publish and subscription dots are immediately visible and if you
need to further augment the chart with graphs to describe timing or whatever you
think will be useful, place those on the diagram too:

.. image:: _static/miros_rabbitmq_cache_file_chart.svg
    :target: _static/miros_rabbitmq_cache_file_chart.pdf
    :align: center

.. _reading_diagrams-sequence-diagrams:

Sequence Diagrams
-----------------
Sequence diagrams are very useful and extremely fragile to design changes.  The
`can be generated directly from the trace instrumentation of the state machine
<https://github.com/aleph2c/sequence>`_ and quickly written up in plain text.
You can drop this plain text into your code or use it directly in your docs.

From this instrumentation trace log:

.. code-block:: python

  [2013-3-24] [doc_process] event->begin() spec->statechart
  [2013-3-24] [doc_process] event->prototype() statechart->code
  [2013-3-24] [doc_process] event->debug() code->code
  [2013-3-24] [doc_process] event->communicate() code->trace
  [2013-3-24] [doc_process] event->sequence.rb() trace->sequence_diagram

To this sequence diagram:

.. code-block:: python

   [ Chart: doc_process ] (?)
      spec       statechart        code             trace      sequence_diagram 
        +-begin()->|                |                |                |
        |   (?)    |                |                |                |
        |          +--prototype()-->|                |                |
        |          |      (?)       |                |                |
        |          |                +                |                |
        |          |                 \ (?)           |                |
        |          |                 debug()         |                |
        |          |                 /               |                |
        |          |                <                |                |
        |          |                +-communicate()->|                |
        |          |                |      (?)       |                |
        |          |                |                +-sequence.rb()->|
        |          |                |                |      (?)       |

Avoid spending a lot of time on these diagrams, and avoid the more advanced
diagramming features, since to put effort into hand drawing a sequence diagram
while designing a reactive system will be a Sisyphean effort.

.. _reading_diagrams-payloads:

Payloads
--------
Your statechart is running in it's own thread.  An event can be published from
one thread and consumed by another thread.  This means if you put mutable data
in your event's payload, you could be creating a shared global variable between two
separating threads.  Shared global information should be locked and unlocked if
it's being used by multiple concurrent processes.

Instead of coming up with complicated locking mechanisms, wrap large common data
structures within their own statecharts and copy smaller payloads into named
tuples.  A named tuple is immutable, so you won't accidentally shoot yourself in
the foot by accidentally creating a global variable.  You can draw your payloads
into your statecharts like this:

.. image:: _static/immutable_payload.svg
    :target: _static/immutable_payload.pdf
    :align: center

Pepper your payloads all over your drawings, you might be repeating yourself,
but the quick understanding that you will be getting from a glance will pay for
this trade off.  The `namedtuple is nice to work with
<https://docs.python.org/3.5/library/collections.html#collections.namedtuple>`_.

.. _reading_diagrams-dealing-with-the-anti-brand:

Dealing with the Anti-Brand
---------------------------
People may roll their eyes when they see your pictures.

A techno-anthropologist could build a career around looking at the history of
UML.  In my own career I saw a strange kind of social stratum emerge between
architects and practitioners, where architects had higher social status than the
people implementing their vision.  The architects invented techno-babble to
describe simple concepts and tried to present their work as a collection of open
secrets and I don't think they did this on purpose.

The developers, who were ultimately responsible for the delivery of working
software would create something independent of this vision.  It wouldn't
surprise me if the whole agile management movement was given birth because of
this political tension.  It is a lot more interesting than this, but I'm not a
historian.

So, what do you do when people start rolling their eyes when you show them these
pictures?  First of all, don't take it personally, they might have some well
earned cynicism.  Just quickly explain what the pictures mean and show them how
to draw their own pictures.  Show them why they are useful.  Explain things in
plain English, don't use the language of professors or consultants.  You don't
have to signal that you are clever, we are trying to expose ideas not to hide
behind them.

The Python programming language has moved well beyond UML.  In fact, it could be
said that we don't really know how to program computers yet.  We might still be
using Roman numerals; when Arabic numbers have yet to be discovered.  UML isn't
the answer, it's a trajectory toward what we really want.  We want to be able
to see our designs using the visual parts of our mind.  We want to be able to
communicate our complex ideas to one another using a formalism that is
expressive enough to solve our problems.

If you can't sell your ideas to everyone, don't worry about it.  Their will
always be people you can't reach, focus on what you can change instead.  This is
the power of open source, you can always fork a project and go your own way.

If a developer isn't diagramming their own software, then your organization is
doing it wrong.

.. raw:: html

  <a class="reference internal" href="zero_to_one.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="examples.html"><span class="std std-ref">next</span></a>

.. [#]  `The Sunk Cost Fallacy <https://youarenotsosmart.com/2011/03/25/the-sunk-cost-fallacy/>`_
