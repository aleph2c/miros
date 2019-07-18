.. _reading_diagrams-reading-diagrams:

  *If I can't picture it, I can't understand it* 
  
  -- Albert Einstein

  *Obey, cooperate, diverge*

  -- Chinese Proverb

Diagrams
========

.. _reading_diagrams-history-and-context:

History and Context
^^^^^^^^^^^^^^^^^^^

In the 1990s a number of people got together an collected all of the different
popular ways of drawing pictures of software into one standard called UML
(`unified <https://xkcd.com/927/>`_ modeling language).  The Harel formalism
(the way David Harel wanted us to draw statecharts) was included in UML.

Unfortunately, UML has fallen out of favor because the committees developing it
built something that the general software community didn't want.  There are many
different reasons for this, but it is safe to say that it is no longer popular.
In fact, UML, in some ways, has become a kind of anti-brand.

The UML mission was noble, to create an object-oriented-picture language that
could be used to build working systems.  But the broader software community
didn't want a separate picture language, they wanted some simple and common
drawing techniques that would help them communicate their thinking in a compact
form.

To make a picture language, or any programming language is complicated, so as
the rules governing the picture language became more complex, it became less
useful for those who just wanted to use it to share ideas.

.. note::

   Aspects of UML are still alive and well.  They have been integrated into
   model-driven development tools like those provided by Matlab.  It makes sense
   to have these diagrams under the control of a single, well funded software
   company, closely integrated with the mathematical theory used for control
   systems, FFTs and that kind of thing.

   As processors become ever more complicated (`A technical reference manual is
   typically over 2000 pages now <http://www.ti.com/tool/HERCULES-DSPLIB>`_),
   the software specialists at Matlab work hand in hand with the hardware
   vendors that have developed the new processors.  This means they eat the
   mundane and arcane complexity on your behalf, by providing code which will
   automatically write the software drivers needed to control the hardware.

   This unlocks the engineer from being drown in the specifics, it gives them
   the power to quickly develop working prototypes.  It comes at a cost; you no
   longer practice programming, you practice the Matlab user interface.  But
   your increase in capability may be worth it for the productivity gain.

UML was written for the C++ tradition of object oriented programming.  Python
also uses this tradition, so this means that UML fits tightly to Python.  So we
have some useful tools and drawing techniques for compacting our designs into a
set of images.

Martin Fowler rendered down the complexity of the UML standard into: `UML
distilled <https://martinfowler.com/books/uml.html>`_.  If you want a very solid
understanding about Harel formalism as it relates to UML, go to the source and
read `Practical UML Statecharts in C/C++, 2nd Edition
<https://sourceforge.net/projects/qpc/files/doc/PSiCC2.pdf/download>`_ by Miro
Samek.

But do you need to read these books before you use UML? No, because we are not
going to treat UML as a formal computer language with mathematical semantics. We
will use UML as something to sketch with.  The formal language we will use is
Python.

This section should give you enough information so that you can make your own
pictures.

.. _reading_diagrams-the-most-important-rule-in-uml:

The Most Important Rule in UML
------------------------------

  *Software modelers depend on and use engineering analogies but often fail to
  understand them.  Engineers realize that the models aren't the product; they're
  abstractions of the product.  In fact, in most cases, the models are only
  partial abstractions of the product, used to hightlight aspects that the
  engineer should know about the product.  The term *executable specification*
  is an oxymoron -- if the specification were truly executable, it would
  actually be "the thing".  Otherwise, it would merely model "the thing," which
  by definition is partial and incomplete.*

  -- Dave Thomas

**You don't have to draw everything on your picture.**

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

----

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

----

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

If you are going to inherit ask yourself if the "is-a", or "is-an", relationship
holds true when you use the two class names in a sentence.  "The ToasterOven
class is an ActiveObject"; yes, that makes sense.  Ok, I'll use inheritance.

If you want all of the states of your statechart to react the same when they see
a specific event, use the :ref:`ultimate hook pattern <patterns-ultimate-hook>`.
This gives you all of the benefits of inheritance while still having debuggable
code.

.. _reading_diagrams-events:

Events
------
Any code which uses the miros library is event-driven.

On your drawings the events are represented as the hook descriptions on the
upper left part of a state, or by the arrows which point from one state to
another.  In the special case of the **init** event, it is represented as the
black dot with an arrow on it.

There can be many events which all share the same name; an event's name is
called a signal.  An event can also carry a python object with it as a payload.
You draw how an event will be handled by your statechart, by drawing arrows or
hooks labeled with that event's signal name.  If your event has a payload, draw the
structure into which you will place that payload.

The event that is not a hook, is like a named marble that can roll on a groove,
described by the arrows of your statechart.  You can think of the groove as
being pitched so that a marble can only roll in one direction.  Any groove can
have software written on it, but this software will only run when a marble rolls
over it.  This is how these grooves can be drawn with UML:

.. image:: _static/Transition_Triggers.svg
    :target: _static/Transition_Triggers.pdf
    :align: center

In English, the above diagram would say, "If I receive an event with a signal
name SIGNAL_NAME while I am in source_state, run the guard, if it returns True,
run the action() function within the context of the source state, then add the
EVT_A event to my fifo queue so that it can be run during my next RTC process,
then transition to the target_state, but, if my guard code returns False, do not
transition, but let the SIGNAL_NAME event propagate outward."

.. note::

  On the ``^EVT_A`` shorthand.

  In miros there are many different ways to post events.  You can post to a
  fifo; ``post_fifo`` and you can post to a lifo, ``post_lifo``.  You can even
  publish an event, so that another concurrent statechart will receive the
  message.  So, to use the ``^EVT_A`` in UML isn't descriptive capture miro's
  capabilities.

  As a rule, if I see ``^EVT_A`` I will assume that it is using the
  ``post_fifo`` API, and if I need to be specific, I will write the code that
  performs the post directly on the diagram.

The above diagram written as `code
<https://github.com/aleph2c/miros/blob/master/examples/guard_example.py>`_,
could look like this:

.. code-block:: python
  :emphasize-lines: 24-33
 
   # guard_example.py
   import time
   from collections import namedtuple

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   OptionalPayload = namedtuple('OptionalPayload', ['x'])

   def guard():
     '''should we let an event pass?'''
     return True

   def action():
     '''some code to run when the event occurs (on the arrow)'''
     print('some action')

   @spy_on
   def source_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.SIGNAL_NAME):
       if guard():
         action()  # perform some action on this event

         # the EVT_A event will be posted after we have
         # finish our transition
	 chart.post_fifo(Event(signal=signals.EVT_A))

         # transition to the target_state
	 status = chart.trans(target_state)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status
    
   @spy_on
   def target_state(chart, e):
     chart.temp.fun = chart.top
     status = return_status.SUPER
     return status

   if __name__ == "__main__":

     # event arrow example
     ao = ActiveObject('eae')
     ao.live_trace = True
     ao.start_at(source_state)
     ao.post_fifo(Event(signal=signals.SIGNAL_NAME,
       payload=OptionalPayload(x='1')))
     time.sleep(0.01)

This will produce the following trace:

.. code-block:: python
  
   [20:42:14.851] [eae] e->start_at() top->source_state
   some action
   [20:42:14.853] [eae] e->SIGNAL_NAME() source_state->target_state

----   

Your event can also run some code without causing a state transition; this is
called a hook:

.. image:: _static/hook_diagram_1.svg
    :target: _static/hook_diagram_1.pdf
    :align: center

In English, the above diagram would say, "If I receive an event with a signal
named "SIGNAL_NAME" while I am in source_state, or any of its inner states, run
the guard, if it returns True, run the action().  When I have finished running
the action, do not perform a state transition.  If the guard returned false,
ignore this event and let it percolate outward to my super state"

The above diagram expressed in `code
<https://github.com/aleph2c/miros/blob/master/examples/hook_example_1.py>`_
could look like this:

.. code-block:: python
  :emphasize-lines: 22-25
 
   # hook_example_1.py
   import time
   from collections import namedtuple

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   OptionalPayload = namedtuple('OptionalPayload', ['x'])

   def guard():
     return True

   def action():
     print('hook code was run {}')

   @spy_on
   def a(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.SIGNAL_NAME):
       if guard():
	 action()
         status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def a1(chart, e):
     chart.temp.fun = a
     status = return_status.SUPER
     return status

   if __name__ == "__main__":
     # simple hook example
     ao = ActiveObject(name="she")
     ao.live_trace = True
     ao.start_at(a1)
     ao.post_fifo(Event(signal=signals.SIGNAL_NAME, payload=OptionalPayload(x=2)))
     # starting another thread, let it run for a moment before we shut down
     time.sleep(0.01)  
     print(ao.state_name)
          
This will produce the following trace:

.. code-block:: python

   [2019-07-08 21:06:57.385487] [she] e->start_at() top->a1
   hook code was run 2
   a1

----

If I would like my hook to stop the event from being handled outside of the
state, I would handle it with the hook, but I would show that I'm doing nothing
with it by drawing ``{}`` in the action part of the hook.

.. image:: _static/hook_diagram_2.svg
    :target: _static/hook_diagram_2.pdf
    :align: center

In English, the above diagram would say, "If I receive an event with a signal
named 'SIGNAL_NAME' while I am in a1, or any of its inner states (a11), do
not let this event proceed past the a1 boundary, and do not cause a
state transition."

The above diagram expressed in `code
<https://github.com/aleph2c/miros/blob/master/examples/hook_example_2.py>`_
could look like:

.. code-block:: python
  :emphasize-lines: 26-27
 
   # hook_example_2.py
   import time
   from collections import namedtuple

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   OptionalPayload = namedtuple('OptionalPayload', ['x'])

   @spy_on
   def a(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.SIGNAL_NAME):
       print("this code should never run")
       status = return_status.HANDLED
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def a1(chart, e):
     if(e.signal == signals.SIGNAL_NAME):
       status = return_status.HANDLED
     else:
       chart.temp.fun = a
       status = return_status.SUPER
     return status

   @spy_on
   def a11(chart, e):
     chart.temp.fun = a1
     status = return_status.SUPER
     return status

   if __name__ == "__main__":
     # simple hook example 2
     ao = ActiveObject(name="she2")
     ao.live_trace = True
     ao.start_at(a11)
     ao.post_fifo(Event(signal=signals.SIGNAL_NAME))
     # starting another thread, let it run for a moment before we shut down
     time.sleep(0.01)  
     print(ao.state_name)

When run the above code will produce the following:

.. code-block:: python
  
   [2019-07-09 06:11:13.640030] [she2] e->start_at() top->a11
   a11

----

There are internal and external signals.

The internal signals are ENTRY_SIGNAL, INIT_SIGNAL and EXIT_SIGNAL.  They are
automatically sent to your statechart by the event processor as it solves the
topological problems required to have your program follow the Harel Formalism.

An event with the ENTRY_SIGNAL will be sent to your state as another event has
caused a transition from the outer part of the state to the inner part of the
state.  On the state drawing, it is called **enter** and it follows the same
drawing rules as any other hook.

Conversely, an event with the EXIT_SIGNAL internal signal is send to your state
when another event has caused a transition from inner part of the state to the
outer part of the state.  On the state drawing, it is called **exit** and it
follows the hook drawing rules. 

An event called INIT_SIGNAL will be sent to your state, once that state has been
settled into.  On the diagram it is a **large black dot** with an arrow on it.

.. image:: _static/internal_signals_1.svg
    :target: _static/internal_signals_1.pdf
    :align: center

Here is some `code
<https://github.com/aleph2c/miros/blob/master/examples/internal_signals_1.py>`_
that would map to the above diagram:

.. code-block:: python
  :emphasize-lines: 13-20, 23-29, 37-42
 
   # internal_signals_1.py
   import time

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def a(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       print("'a' entered")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       print("'a' exited")
       status = return_status.HANDLED
     # need to add an external signal so we can cause exits
     # for our demo
     elif(e.signal == signals.Reset):
       status = chart.trans(a)
     elif(e.signal == signals.INIT_SIGNAL):
       print_string  = "code to run after 'a' entered "
       print_string += "and we have settled into 'a', "
       print_string += "the INIT_SIGNAL wants us to "
       print_string += "transition into 'a1'"
       print(print_string)
       status = chart.trans(a1)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def a1(chart, e):
     if(e.signal == signals.ENTRY_SIGNAL):
       print("'a1' entered")
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       print("'a1' exited")
       status = return_status.HANDLED
     else:
       chart.temp.fun = a
       status = return_status.SUPER
     return status

   if __name__ == "__main__":
     # simple hook example 2
     ao = ActiveObject(name="she2")
     ao.live_trace = True
     ao.start_at(a1)
     ao.post_fifo(Event(signal=signals.SIGNAL_NAME))
     ao.post_fifo(Event(signal=signals.Reset))
     # starting another thread, let it run for a moment before we shut down
     time.sleep(0.01)  

If we were to run this code we would see:

.. code-block:: python
  
  'a' entered
  'a1' entered
  [2019-07-09 06:54:53.050553] [she2] e->start_at() top->a1
  'a1' exited
  'a' exited
  'a' entered
  code to run after 'a' entered and we have settled into 'a',
  the INIT_SIGNAL wants us to transition into 'a1'
  'a1' entered
  [2019-07-09 06:54:53.052104] [she2] e->Reset() a1->a1

External event signal names are created the moment they are labeled in the code.
Here is some code that shows how this is done:

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

.. _reading_diagrams-event-processor-connection:

Event Processor Attachment Points
---------------------------------
The event processor is the rule book for your statechart.  It is the thing that
will cause it to transition from one state to another.  It will trigger
internal events and it will read and run all of your code as your code reacts
to the outside world.

To connect the event processor of your object to a statemachine; inherit it into
the class that will solve your problem, then draw the attachment point like this:

.. image:: _static/attachment_point_1.svg
    :target: _static/attachment_point_1.pdf
    :align: center

This attachment point serves double duty, it shows that the event processor drives
the state chart dynamics and it shows were the state machine is started.

.. note::
  
   I'm not sure if I'm using UML properly according to the standard, and I don't
   really care.  What I care about is if you understand what I mean.

The above diagram could be `written this way
<https://github.com/aleph2c/miros/blob/master/examples/attachment_point_1.py>`_
in Python:

.. code-block:: python
  :emphasize-lines: 82-85
 
   # attachment_point_1.py
   import time

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   class Class1UsedToSolveProblem(ActiveObject):
     def __init__(self, name):
       '''demonstration class used to show 
	  event processor attachment point on statechart diagram

       **Args**:
	  | ``name`` (string): the name to show up in the trace
       '''
       super().__init__(name)
       self.attribute_1 = None
       self.attribute_2 = None

     def method_1(self):
       print("method 1 called")

     def method_2(self):
       print("method 2 called")

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.attribute_1 = True
       chart.attribute_2 = True
       status = return_status.HANDLED
     if(e.signal == signals.Hook):
       print('hook')
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       status = chart.trans(inner_state_1)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state_1(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.method_1()
       status = return_status.HANDLED
     elif(e.signal == signals.B):
       status = chart.trans(inner_state_2)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.method_2()
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status
       
   @spy_on
   def inner_state_2(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.attribute_1 = True
       chart.attribute_2 = True
       status = return_status.HANDLED
     elif(e.signal == signals.A):
       status = chart.trans(inner_state_1)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.attribute_1 = False
       chart.attribute_2 = False
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

   if __name__ == "__main__":
     subclassed_ao = Class1UsedToSolveProblem('subclassed_ao')
     subclassed_ao.live_trace = True
     # this is the attachement point where the event processor
     # is linking to the statemachine defined above as a set of 
     # functions which reference each other
     subclassed_ao.start_at(outer_state)
     subclassed_ao.post_fifo(Event(signal=signals.B))
     subclassed_ao.post_fifo(Event(signal=signals.A))
     subclassed_ao.post_fifo(Event(signal=signals.Hook))
     time.sleep(0.01)

If you were to run this code you would see something like this:

.. code-block:: python

   method 1 called
   [07:26:35.66] [subclassed_ao] e->start_at() top->inner_state_1
   method 2 called
   [07:26:35.66] [subclassed_ao] e->B() inner_state_1->inner_state_2
   method 1 called
   [07:26:35.66] [subclassed_ao] e->A() inner_state_2->inner_state_1
   hook

----

In the context of this library an object instantiated with an event processor
can attach itself to a statemachine.  Another object instantiated with a
different event processor can also be attach to the same statemachine.

.. image:: _static/attachment_point_2.svg
    :target: _static/attachment_point_2.pdf
    :align: center

.. note::

   The statemachine and its functions do not keep track of variables or the
   current state; they simply act as a behavioral specification.  The attribute
   changes are always performed on the first arguement of the state function,
   the state function itself has no memory or notion of the program's state.

You could manifest the above diagram in `code like
this <https://github.com/aleph2c/miros/blob/master/examples/attachment_point_2.py>`_:

.. code-block:: python
  :emphasize-lines: 99-100, 110-112
  
  # attachment_point_2.py
  import time

  from miros import spy_on
  from miros import Event
  from miros import signals
  from miros import ActiveObject
  from miros import return_status

  class Class1UsedToSolveProblem(ActiveObject):
    def __init__(self, name):
      '''demonstration class used to show 
         event processor attachment point on statechart diagram

      **Args**:
         | ``name`` (string): the name to show up in the trace
      '''
      super().__init__(name)
      self.attribute_1 = None
      self.attribute_2 = None

    def method_1(self):
      print("method 1 called")

    def method_2(self):
      print("method 2 called")

  class Class2UsedToSolveProblem(Class1UsedToSolveProblem):
    def __init__(self, name):
      '''demonstration class showing how inheritance can
         overload methods of an another class, and indepentently attach
         to the statemachine used by the other class.

      **Args**:
         | ``name`` (string): the name to show up in the trace
      '''
      super().__init__(name)

    def method_1(self):
      print("method 1(overloaded) called")

    def method_2(self):
      print("method 2(overloaded) called")

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      chart.attribute_1 = True
      chart.attribute_2 = True
      status = return_status.HANDLED
    if(e.signal == signals.Hook):
      print('hook')
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(inner_state_1)
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state_1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      chart.method_1()
      status = return_status.HANDLED
    elif(e.signal == signals.B):
      status = chart.trans(inner_state_2)
    elif(e.signal == signals.EXIT_SIGNAL):
      chart.method_2()
      status = return_status.HANDLED
    else:
      chart.temp.fun = outer_state
      status = return_status.SUPER
    return status
      
  @spy_on
  def inner_state_2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      chart.attribute_1 = True
      chart.attribute_2 = True
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = chart.trans(inner_state_1)
    elif(e.signal == signals.EXIT_SIGNAL):
      chart.attribute_1 = False
      chart.attribute_2 = False
      status = return_status.HANDLED
    else:
      chart.temp.fun = outer_state
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    subclassed_ao1 = Class1UsedToSolveProblem('subclassed_ao1')
    subclassed_ao1.live_trace = True
    # this is the attachement point to the first object
    subclassed_ao1.start_at(outer_state)
    subclassed_ao1.post_fifo(Event(signal=signals.B))
    subclassed_ao1.post_fifo(Event(signal=signals.A))
    subclassed_ao1.post_fifo(Event(signal=signals.Hook))

    # the two statemachines will be running at the same time in different
    # threads, so we will delay so we don't end up with a confusing trace
    time.sleep(0.01)
    subsubclassed_ao2 = Class2UsedToSolveProblem('subsubclassed_ao2')
    subsubclassed_ao2.live_trace = True
    # this is the attachement point to the second object
    # (it uses the same statemachine as the first object)
    subsubclassed_ao2.start_at(outer_state)
    subsubclassed_ao2.post_fifo(Event(signal=signals.Hook))
    subsubclassed_ao2.post_fifo(Event(signal=signals.B))
    subsubclassed_ao2.post_fifo(Event(signal=signals.A))
    
    time.sleep(0.01)

This would produce output like this:

.. code-block:: python
  
  method 1 called
  [07:45:22.30] [subclassed_ao1] e->start_at() top->inner_state_1
  method 2 called
  [07:45:22.30] [subclassed_ao1] e->B() inner_state_1->inner_state_2
  method 1 called
  [07:45:22.30] [subclassed_ao1] e->A() inner_state_2->inner_state_1
  hook
  method 1(overloaded) called
  [07:45:22.32] [subsubclassed_ao2] e->start_at() top->inner_state_1
  hook
  method 2(overloaded) called
  [07:45:22.32] [subsubclassed_ao2] e->B() inner_state_1->inner_state_2
  method 1(overloaded) called
  [07:45:22.32] [subsubclassed_ao2] e->A() inner_state_2->inner_state_1

----

If you want to embed your state machine within your class, you can, you just
write it's functions as ``staticmethods`` and use the ``miros.Factory``.  An
embedded state chart might look like this:

.. image:: _static/attachment_point_4.svg
    :target: _static/attachment_point_4.pdf
    :align: center

The ``Event Processor`` component in the ``ClassWithEmbeddedChart`` is taking up
a lot of room on the diagram.  So, why not just keep the bulbus part of its
glyph as a shorthand for the attachment point.  It still shows where we want the
statechart to start:

.. image:: _static/attachment_point_5.svg
    :target: _static/attachment_point_5.pdf
    :align: center

Here is the `code
<https://github.com/aleph2c/miros/blob/master/examples/class_with_embedded_chart.py>`_
that could manifest the above diagram, notice that the ``start_at`` call is made
within the ``ClassWithEmbeddedChart`` ``__init__`` method:

.. code-block:: python
  :emphasize-lines: 51,52
  
  import time
  from collections import namedtuple

  from miros import Event
  from miros import signals
  from miros import Factory
  from miros import return_status

  class ClassWithEmbeddedChart(Factory):
    def __init__(self, name, live_trace=None):
      '''demonstration of a miros hierarchical statemachine within a class.

      **Args**:
         | ``name`` (str): The name of this object in the trace instrumentation
         | ``live_trace=None`` (str): set to true to get a live trace of the chart
      '''
      super().__init__(name)
     
      self.live_trace = True if live_trace else False
      self.outer_state = self.create(state="outer_state"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.outer_state_entry_signal). \
        catch(signal=signals.INIT_SIGNAL,
          handler=self.outer_state_init_signal). \
        catch(signal=signals.Hook,
          handler=self.outer_state_hook). \
        to_method()

      self.inner_state_1 = self.create(state="inner_state_1"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.inner_state_1_entry_signal). \
        catch(signal=signals.EXIT_SIGNAL,
          handler=self.inner_state_1_exit_signal). \
        catch(signal=signals.B,
          handler=self.inner_state_1_b). \
        to_method()

      self.inner_state_2 = self.create(state="inner_state_2"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.inner_state_2_entry_signal). \
        catch(signal=signals.A,
          handler=self.inner_state_2_a). \
        catch(signal=signals.EXIT_SIGNAL,
          handler=self.inner_state_2_exit_signal). \
        to_method()

      self.nest(self.outer_state, parent=None). \
        nest(self.inner_state_1, parent=self.outer_state). \
        nest(self.inner_state_2, parent=self.outer_state)

      # this is the attachment point on the diagram
      self.start_at(self.outer_state)

    @staticmethod
    def outer_state_entry_signal(chart, e):
      status = return_status.HANDLED
      chart.attribute_1 = False
      chart.attribute_2 = False
      return status

    @staticmethod
    def outer_state_init_signal(chart, e):
      status = chart.trans(chart.inner_state_1)
      return status

    @staticmethod
    def outer_state_hook(chart, e):
      status = return_status.HANDLED
      print("hook")
      return status

    @staticmethod
    def inner_state_1_entry_signal(chart, e):
      status = return_status.HANDLED
      chart.method_1()
      return status

    @staticmethod
    def inner_state_1_exit_signal(chart, e):
      status = return_status.HANDLED
      chart.method_2()
      return status

    @staticmethod
    def inner_state_1_b(chart, e):
      status = chart.trans(chart.inner_state_2)
      return status

    @staticmethod
    def inner_state_2_entry_signal(chart, e):
      status = return_status.HANDLED
      chart_attribute_1 = True
      chart_attribute_2 = True
      return status

    @staticmethod
    def inner_state_2_a(chart, e):
      status = chart.trans(chart.inner_state_1)
      return status

    @staticmethod
    def inner_state_2_exit_signal(chart, e):
      status = return_status.HANDLED
      chart_attribute_1 = False
      chart_attribute_2 = False
      return status

    def method_1(self):
      print("calling method_1")

    def method_2(self):
      print("calling method_2")

  if __name__ == "__main__":
    cwec = ClassWithEmbeddedChart('cwec', live_trace=True)
    cwec.post_fifo(Event(signal=signals.B))
    cwec.post_fifo(Event(signal=signals.Hook))
    cwec.post_fifo(Event(signal=signals.A))
    time.sleep(0.01)

.. note::

  Object Oriented statecharts were first implemented and written about in 1996

As your team gets used to looking at these kinds of diagrams, you might create a
different short hand for the attachment point, or leave it off of your diagram
all together.

.. _reading_diagrams-states:

States
------ 

The states in miros are just functions that you write that will react to events
send to them by an active object's event processor.  A state function has
two arguments, a reference to the active object calling it and an event.  State
functions typically contain an if-elif-else structure, which describes the event
arrows and hooks on the statechart diagram.  The state function will contain
information about what state wraps it in the diagram (it's super state), this is
typically expressed in the else clause of it's if-elif-else structure.  The
state function needs to return predefined information to tell the event
processor how it has reacted to an event; like if it is transitioning, or if the
event was unhandled and needs to be passed to the super state, or if it has been
handled so that the event processor can stop processing the event.

An important thing to remember is that a state function will be called many
times by the event processor while it is trying to find the answers to different
questions.  The state function can be asked for its super state, or it can be
asked how it handles a particular event.  The state function acts as a node in a
graph and a behavioral specification.

If you look at the following diagram, you will see we need to define three state
functions.

.. image:: _static/attachment_point_1.svg
    :target: _static/attachment_point_1.pdf
    :align: center

You can see the code that could implement this design `here
<https://github.com/aleph2c/miros/blob/master/examples/attachment_point_1.py>`_.

The outer_state code could look like this:

.. code-block:: python

    from miros import signals
    from miros import return_status
    
    def outer_state(chart, e):

      # return_status contain information about how this state
      # has reacted to the event,
      # we initialize our return status it to UNHANDLED,
      # so that if an event guard fails the event can percolate outward
      # to its superstate (parent state)
      status = return_status.UNHANDLED 
    
      # e, is the event that is being sent to this state function by the event
      # processor
      #
      # The signals object contains all of the signals that are used by this
      # statechart, the ENTRY_SIGNAL is an internal signal which is sent to the
      # this function by the event processor.
      if(e.signal == signals.ENTRY_SIGNAL):
        # we are reacting to the entry event on the diagram
        # we only change variables on the first argument of our function, like
        # we would if it was named 'self' in a typical Python method
        chart.attribute_1 = False  
        chart.attribute_2 = False  

        # this state wants to tell the event processor this event was handled
        # do not percolate outward in the graph (it wouldn't anyway for internal
        # signals)
        status = return_status.HANDLED

      # The INIT_SIGNAL is the big black dot on the diagram.  It is the "now
      # what" signal.  We have landed in the outer_state, now what?  Well our
      # diagram tells use we want a transition to inner_state_1
      elif(e.signal == signals.INIT_SIGNAL):
         # We are reacting to the init event

         # Here we tell the event processor that we want it to transition to a
         # different state by feeding the state function of our target as an
         # argument to the trans method.
         # The trans method will determine what we want  to return from
         # this function.
         status = chart.trans(inner_state_1)

      # The Hook signal name is an external signal name, something that is
      # specific to this design.  The first time, miros sees `Hook` in an event
      # it invents it and appends it to the signals object. (lightweight
      # metaprogramming)
      elif(e.signal == signals.Hook):
        # We are reacting to the Hook event on the diagram.
        #
        # This is what we want to happen if the Hook event is sent to the state
        # chart while it is in this state, or the inner_state_1 or the
        # inner_state_2
        print("hook")
        # This is the code that makes the handing of this event a hook,
        # or an event which causes  code to run without causing a
        # state transition.  Here we tell the event processor to stop searching.

        # So imagine that we were in the inner_state_2 and a 'Hook' event was 
        # sent to the chart, the above code would run and the chart would remain
        # in the inner_state_2 state.
        status = return_status.HANDLED
      else:
        # We specifically write what our outer state function is, since there
        # isn't one for outer_state, we use the special `top` attribute of the
        # active object to indicate to the event processor that we are at the
        # outermost state of our design.
        chart.temp.fun = chart.top 
        # We tell the event processor that we are in the "set-super" part of our
        # state function.  We landed here because the event sent was not handled
        # by the if-elif part of our function above.
        status = return_status.SUPER

      # tell the event processor how we dealt with the event
      return status

The inner_state_1 and inner_state_2 state functions would look like this:

.. code-block:: python
  
   def inner_state_1(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.method_1()
       status = return_status.HANDLED
     elif(e.signal == signals.B):
       status = chart.trans(inner_state_2)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.method_2()
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status
  
   def inner_state_2(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.attribute_1 = True
       chart.attribute_2 = True
       status = return_status.HANDLED
     elif(e.signal == signals.A):
       status = chart.trans(inner_state_1)
     elif(e.signal == signals.EXIT_SIGNAL):
       chart.attribute_1 = False
       chart.attribute_2 = False
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

----

There are two different ways to draw a state on a diagram:
   * simple states
   * composite states

Here is a simple state, you would use it when drawing a finite state machine:

.. image:: _static/simple_state_1.svg
    :target: _static/simple_state_1.pdf
    :align: center

Here is an example of a finite state machine (FSM) -- An oven.

.. image:: _static/simple_state_2.svg
    :target: _static/simple_state_2.pdf
    :align: center

To make such a finite statemachine with miros is very straight forward, you just
set your state function super states to the ``top`` attribute of the
ActiveObject.  Here is some code that the above diagram could model:

.. code-block:: python
  
   import time

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def off(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.bake_pressed):
       status = chart.trans(heating)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def heating(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.off_pressed):
       status = chart.trans(off)
     elif(e.signal == signals.too_hot):
       status = chart.trans(idling)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def idling(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.too_cold):
       status = chart.trans(heating)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

Notice that the **init** signal is not written into the code, instead we use the
``start_at`` method to attach our ActiveObject to the off state:

.. code-block:: python
  :emphasize-lines: 4
  
  if __name__ == "__main__":
     ao = ActiveObject('simple_fsm_2')
     ao.live_trace = True
     # attach the ActiveObject's event processor to the state machine 
     # and start its thread
     ao.start_at(off)  
     ao.post_fifo(Event(signal=signals.bake_pressed))
     ao.post_fifo(Event(signal=signals.off_pressed))
     ao.post_fifo(Event(signal=signals.bake_pressed))
     ao.post_fifo(Event(signal=signals.too_hot))
     ao.post_fifo(Event(signal=signals.too_cold))
     time.sleep(0.01)

If we run it we see that it works:

.. code-block:: python
 
  [2019-07-12 07:02:10.304293] [simple_fsm_2] e->start_at() top->off
  [2019-07-12 07:02:10.305574] [simple_fsm_2] e->bake_pressed() off->heating
  [2019-07-12 07:02:10.306446] [simple_fsm_2] e->off_pressed() heating->off
  [2019-07-12 07:02:10.307243] [simple_fsm_2] e->bake_pressed() off->heating
  [2019-07-12 07:02:10.308006] [simple_fsm_2] e->too_hot() heating->idling
  [2019-07-12 07:02:10.308924] [simple_fsm_2] e->too_cold() idling->heating

So, to get a finite state machine working with miros, we must know that the
**init** glyph is just a synonym for the attachment point:

.. image:: _static/simple_state_3.svg
    :target: _static/simple_state_3.pdf
    :align: center

----

The UML term for a state, which can have other states inside of it, is called a
"composite state".  Here is what it looks like:

.. image:: _static/composite_state_1.svg
    :target: _static/composite_state_1.pdf
    :align: center


It shares the same rounded rectangular look of the simple state icon, but it
also has a bar across the top, above which, you type the state's name.  The name
of the state is placed at the top like this to separate it away from the rest of
the rounded rectangle's inner area.  The majority of the compound state's inner
area serves as a canvas where you will draw your inner states, hooks, event
arrows...  etc.

In miros, all states are composite states.

Here is a simple hierarchical state machine (HSM) -- A slightly better oven:

.. image:: _static/composite_state_2.svg
    :target: _static/composite_state_2.pdf
    :align: center

Any state-looking-widget on your diagram that actually isn't a state, is called
a **pseudostate**.  For instance, on our diagram, the black initialization dot
and the H with a star beside it (deep history) are both called pseudostates.  

We will talk about these shortly.

If you had to draw your statechart into a diagram that didn't have enough room
for it, you might want to simplify it into a compacted representation.  This
would let the person reading your diagram know that there is more to it, but
that it was simplified on your picture so that everything would fit on the page.
This is called **decomposition hiding**.  I'll demonstrate this by hiding some
of the details of our HSM oven:

.. image:: _static/composite_state_3.svg
    :target: _static/composite_state_3.pdf
    :align: center

I have hidden the majority of the door_closed state in the decomposition hiding
state icon.  When you see this icon, you know that some details have been hidden
to make the diagram fit on a page.  But there is a good chance that I am
breaking the UML standard by drawing the above diagram the way I did.  I'm
hiding the door_closed state, yet I'm showing part of it's design.  I'm showing
an arrow going into the door_closed state, and showing it land on a deep history
icon.  So, am I hiding the state or not?  Well, I'm doing both.  I'm trying to
explain the gist of the hidden part of the design: to go back to the previous
sub-state of the door_closed part of the statechart, when the door is opened
after the over was in a door_open state.  I'm trying to show this
history-behavior is happening without going into the details of what substates
exist within the door_closed state.

When you sketch your diagrams without adhering to a rigid set of drawing rules,
you can make decisions like this.  The diagrams act as sketches rather than a
programming language.

.. _reading_diagrams-deep-history-dot:

Deep History Icon
-----------------
If an event has caused you to leave a state deeply embedded in your statechart,
but you would like to transition back to that state after the interruption, you
can use the deep history pseudostate, it's a circle enclosing a H*:

.. image:: _static/TransitionToHistoryStatePattern.svg
    :target: _static/TransitionToHistoryStatePattern.pdf
    :align: center

The :ref:`transition to history <patterns-transition-to-history>` section of the
patterns part of this document goes into the details about how to implement this in code.

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
the terminate pseudostate (icon).  

.. image:: _static/terminate_1.svg
    :target: _static/terminate_1.pdf
    :align: center

Here is some code that shows a trivial statechart being terminated with the
ActiveObject's ``stop`` method.

.. note::

  In this picture's code example we will turn on
  the :ref:`spy <recipes-using-the-spy>`, and :ref:`scribble
  <recipes-scribble-on-the-spy>` onto its output.

.. code-block:: python
  :emphasize-lines: 11, 25
  
  import time

  from miros import spy_on
  from miros import ActiveObject
  from miros import signals, Event, return_status

  @spy_on
  def some_state(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Destroy_This_Chart):
      chart.stop()
      chart.scribble("Terminating Thread")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    ao = ActiveObject('some_state')
    ao.live_spy = True
    ao.start_at(some_state)
    time.sleep(0.1)
    assert(ao.thread.is_alive() == True)
    ao.post_fifo(Event(signal=signals.Destroy_This_Chart))
    time.sleep(0.1)
    assert(ao.thread.is_alive() == False)

If we were to run this code we would see:

.. code-block:: python

  START
  SEARCH_FOR_SUPER_SIGNAL:some_state
  ENTRY_SIGNAL:some_state
  INIT_SIGNAL:some_state
  <- Queued:(0) Deferred:(0)
  Destroy_This_Chart:some_state
  Terminating Thread
  Destroy_This_Chart:some_state:HOOK
  <- Queued:(1) Deferred:(0)


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

Here is some code that would answer this design:

.. code-block:: python
  :emphasize-lines: 20, 21
  
   # final_icon_example_1.py
   import time

   from miros import spy_on
   from miros import Event
   from miros import signals
   from miros import ActiveObject
   from miros import return_status

   @spy_on
   def outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.condition = False if chart.condition == None else chart.condition
       status = return_status.HANDLED
     elif(e.signal == signals.INIT_SIGNAL):
       if chart.condition:
         status = chart.trans(inner_state)
       else:
         chart.scribble("run code, but don't transition out of outer_state")
         status = return_status.HANDLED
     elif(e.signal == signals.Retry):
       chart.condition = False if chart.condition else True
       status = chart.trans(outer_state)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       status = return_status.HANDLED
     else:
       chart.temp.fun = outer_state
       status = return_status.SUPER
     return status

We are writing our debug code onto the :ref:`spy instrumentation
<recipes-using-the-spy>` using its :ref:`scribble <recipes-scribble-on-the-spy>`
feature, so we have to turn on the spy instrumentation to see it:

.. code-block:: python
  :emphasize-lines: 4
  
   if __name__ == "__main__":
     ao = ActiveObject('final_icon')
     ao.augment( name='condition', other=None)
     ao.live_spy = True
     ao.start_at(outer_state)
     ao.post_fifo(Event(signal=signals.Retry))
     ao.post_fifo(Event(signal=signals.Retry))
     time.sleep(0.01)

If you run this code you will see the following:

.. code-block:: python
  :emphasize-lines: 5, 21
  
  START
  SEARCH_FOR_SUPER_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  run code, but don't transition out of outer_state
  <- Queued:(0) Deferred:(0)
  Retry:outer_state
  EXIT_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  SEARCH_FOR_SUPER_SIGNAL:inner_state
  ENTRY_SIGNAL:inner_state
  INIT_SIGNAL:inner_state
  <- Queued:(1) Deferred:(0)
  Retry:inner_state
  Retry:outer_state
  EXIT_SIGNAL:inner_state
  EXIT_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  run code, but don't transition out of outer_state
  <- Queued:(0) Deferred:(0)

The above final pseudostate example could have been made with a statechart
wrapped within a class:

.. image:: _static/final_3.svg
    :target: _static/final_3.pdf
    :align: center

Here is some code which interlocks with the above design diagram:

.. code-block:: python
  :emphasize-lines: 62, 63
  
   import time

   from miros import Event
   from miros import signals
   from miros import Factory
   from miros import return_status

   class InstrumentedFactory(Factory):
     def __init__(self, name, live_trace=None, live_spy=None):
       super().__init__(name)
       self.live_trace = False if live_trace == None else live_trace
       self.live_spy = False if live_spy == None else live_spy

   class FinalIconExample(InstrumentedFactory):
     def __init__(self, name, condition, live_trace=None, live_spy=None):
       '''statechart demonstration the final icon

       **Args**:
          | ``name`` (str): name of the statechart
          | ``condition`` (bool): do we want to transition into the inner state?
          | ``live_trace=None``: enable live_trace feature?
          | ``live_spy=None``: enable live_spy feature?

       **Example(s)**:
         
       .. code-block:: python
          
          FinalIconExample(name='final_icon', condition=True)

       '''
       super().__init__(name, live_trace, live_spy)
       self.condition = condition

       self.outer_state = self.create(state="outer_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.outer_state_entry_signal). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.outer_state_init_signal). \
         catch(signal=signals.Retry,
           handler=self.outer_state_retry). \
         to_method()

       self.inner_state = self.create(state="inner_state"). \
         to_method()

       self.nest(self.outer_state, parent=None). \
            nest(self.inner_state, parent=self.outer_state)

       self.start_at(self.outer_state)

     @staticmethod
     def outer_state_entry_signal(chart, e):
       chart.condition = False if chart.condition == None else chart.condition
       status = return_status.HANDLED
       return status

     @staticmethod
     def outer_state_init_signal(chart, e):
       if chart.condition:
         status = chart.trans(chart.inner_state)
       else:
         chart.scribble("run code, but don't transition out of outer_state")
         status = return_status.HANDLED
       return status

     @staticmethod
     def outer_state_retry(chart, e):
       chart.condition = False if chart.condition else True
       status = chart.trans(chart.outer_state)
       return status

   if __name__ == "__main__":
     ao = FinalIconExample(name='final_icon', condition=True, live_spy=True)
     ao.post_fifo(Event(signal=signals.Retry))
     ao.post_fifo(Event(signal=signals.Retry))
     time.sleep(0.01)

If you were to run this code you would see a spy output very similar to the
first example:

.. code-block:: python
  :emphasize-lines: 15
  
  START
  SEARCH_FOR_SUPER_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  SEARCH_FOR_SUPER_SIGNAL:inner_state
  ENTRY_SIGNAL:inner_state
  INIT_SIGNAL:inner_state
  <- Queued:(0) Deferred:(0)
  Retry:inner_state
  Retry:outer_state
  EXIT_SIGNAL:inner_state
  EXIT_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  run code, but don't transition out of outer_state
  <- Queued:(1) Deferred:(0)
  Retry:outer_state
  EXIT_SIGNAL:outer_state
  ENTRY_SIGNAL:outer_state
  INIT_SIGNAL:outer_state
  SEARCH_FOR_SUPER_SIGNAL:inner_state
  ENTRY_SIGNAL:inner_state
  INIT_SIGNAL:inner_state
  <- Queued:(0) Deferred:(0)


Fall Through
------------
The miros event handler can do something that I haven't seen specified anywhere,
it can do a kind of `catch-and-release
<https://en.wikipedia.org/wiki/Catch_and_release>`_, where an event can be
processed by a state, then released outward into the statechart to be processed
by another, outer, state.  This event bubbling continues until the event falls
off the edge of the chart or is handled by a hook.

.. note::
  
   This is not in the UML standard

.. image:: _static/fall_through_1.svg
    :target: _static/fall_through_1.pdf
    :align: center

I draw this with an un-attached, or an unhandled, arrow.  The arrow has code
marked on it, but it does not connect to anything, to express that it is not
handled within the current state region; the event processor will recurse
outward in it's search to find where it is handled.  

The action on the "unhandled" arrow is a search side effect that can provide
some useful features.

.. code-block:: python
  :emphasize-lines: 26-28, 36-38
   
  import time

  from miros import Event
  from miros import spy_on
  from miros import signals
  from miros import ActiveObject
  from miros import return_status

  @spy_on
  def a0(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(a2)
    elif(e.signal == signals.Bubbling):
      print(
        "finally hooked by a0, but state remains as {}".
        format(chart.state_name))
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def a1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Bubbling):
      print("caught and released by a1")
    else:
      chart.temp.fun = a0
      status = return_status.SUPER
    return status

  @spy_on
  def a2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Bubbling):
      print("caught and released by a2")
    else:
      chart.temp.fun = a1
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    ao = ActiveObject('fall_through')
    ao.live_trace = True
    ao.start_at(a0)
    ao.post_fifo(Event(signal=signals.Bubbling))
    time.sleep(0.1)

Running the above would result in this output:

.. code-block:: text
  
   [2019-07-16 09:02:04.725787] [fall_through] e->start_at() top->a2
   caught and released by a2
   caught and released by a1
   finally hooked by a0, but state remains as a0

.. _reading_diagrams-publishing-to-other-charts:

Publish and Subscribe Coloured Dots
-----------------------------------------
If you are publishing an event to another chart, it is often beneficial to have
your eyes fall on this immediately while looking at your diagram. It is an
output.  I use a red dot to signify this. Red because the event is currently
stopped as it is waiting for processing in a queue.

Eventually, this published event will pass through to the other chart.  To make
it easy to see where this happens, I mark the location with a green dot.  Green
for go; the event is being acted upon.

The red and green dots are not part of the UML standard, so you will be fighting
your UML drawing tools to place these dots in a way that is consistent on each
diagram.  So don't worry about placement consistency, just get the dots close to
where you want them; think of them as marks you might make with a highlighter to
emphasize what you need to see.

.. note::

  Putting red and green dots on your statechart is not in the UML standard

To make a point I will draw two statecharts, which work together, with too much
UML:

.. image:: _static/pub_sub_icons_2.svg
    :target: _static/pub_sub_icons_2.pdf
    :align: center

The diagram is very busy.

The inheritance arrows at the top of the diagram describe the program's
structure.  We see that I'm trying to get the attributes and methods of Chart1
into Chart2.  Chart2 also pulls in the features of the Factory, so we can
:ref:`create a statechart inside of a class
<recipes-creating-a-statechart-inside-of-a-class>`.  

These structural details might be helpful when we first
write our code, but after that, they become clutter. The state machines are the vital part of the diagram;  this is where we pack the
design's behavioral complexity.  We have two coupled state machines that work
together, so when we need to come back to this drawing, we will want to see how
this behavioral partnership works right away.  This is why we add the
highlighter marks.

Here is the code for the above picture with the event sharing code highlighted:

.. code-block:: python
  :emphasize-lines: 27, 29-32, 98-99
  
   # pub_sub_example.py
   import time
   from collections import namedtuple

   from miros import Event
   from miros import spy_on
   from miros import signals
   from miros import Factory
   from miros import ActiveObject
   from miros import return_status

   Coordinate = \
     namedtuple('Coordinate', ['x','y', 'z'])

   class Chart1(ActiveObject):
     def __init__(self, name):
       super().__init__(name)
       self.x, self.y, self.z = None, None, None

     def print_payload(self):
       print("x: {}, y: {}, z: {}".format(self.x, self.y, self.z))

   @spy_on
   def c_1_outer_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.subscribe(Event(signal=signals.Chart_2_Started))
       status = return_status.HANDLED
     elif(e.signal == signals.Chart_2_Started):
       chart.x = e.payload.x
       chart.y = e.payload.y
       chart.z = e.payload.z
       status = chart.trans(c_1_inner_state)
     else:
       chart.temp.fun = chart.top
       status = return_status.SUPER
     return status

   @spy_on
   def c_1_inner_state(chart, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       chart.print_payload()
       chart.post_lifo(Event(signal=signals.Reset))
       status = return_status.HANDLED
     elif(e.signal == signals.Reset):
       status = chart.trans(c_1_outer_state)
     elif(e.signal == signals.INIT_SIGNAL):
       status = return_status.HANDLED
     else:
       chart.temp.fun = c_1_outer_state
       status = return_status.SUPER
     return status


   class Chart2(Chart1, Factory):

     def __init__(self, name, live_trace=None, live_spy=None):
       super().__init__(name)
       self.x = 0
       self.live_spy = False if live_spy == None else live_spy
       self.live_trace = False if live_trace == None else live_trace

       self.c_2_outer_state = self.create(state="c_2_outer_state"). \
         catch(signal=signals.INIT_SIGNAL,
           handler=self.c_2_outer_state_init_signal). \
         catch(signal=signals.Reset,
           handler=self.c_2_outer_state_reset). \
         to_method()

       self.c_2_inner_state = self.create(state="c_2_inner_state"). \
         catch(signal=signals.ENTRY_SIGNAL,
           handler=self.c_2_outer_state_entry_signal). \
         to_method()

       self.nest(self.c_2_outer_state, parent=None). \
            nest(self.c_2_inner_state, parent=self.c_2_outer_state)

       self.start_at(self.c_2_inner_state)

     def increment_x(self):
       self.x += 1

     @staticmethod
     def c_2_outer_state_init_signal(chart, e):
       status = chart.trans(chart.c_2_inner_state)
       return status

     @staticmethod
     def c_2_outer_state_reset(chart, e):
       chart.increment_x()
       status = chart.trans(chart.c_2_outer_state)
       return status

     @staticmethod
     def c_2_outer_state_entry_signal(chart, e):
       status = return_status.HANDLED
       chart.publish(Event(signal=signals.Chart_2_Started,
         payload=Coordinate(x=chart.x, y=2, z=3)))
       return status

   if __name__ == '__main__':
     # need to create an active object
     # set it's live trace attribute
     # then start it in the correct state
     c_1 = Chart1('c_1')
     c_1.live_trace = True
     c_1.start_at(c_1_outer_state)

     # Chart2 starts itself in the correct state
     c_2 = Chart2(name='c_2', live_trace=True)
     c_2.post_fifo(Event(signal=signals.Reset))
     c_2.post_fifo(Event(signal=signals.Reset))
     time.sleep(0.1)

Running this code, we see:

.. code-block:: python

   [09:05:33] [c_1] e->start_at() top->c_1_outer_state
   [09:05:33] [c_2] e->start_at() top->c_2_inner_state
   x: 0, y: 2, z: 3
   [09:05:33] [c_1] e->Chart_2_Started() c_1_outer_state->c_1_inner_state
   [09:05:33] [c_1] e->Reset() c_1_inner_state->c_1_outer_state
   [09:05:33] [c_2] e->Reset() c_2_inner_state->c_2_inner_state
   x: 1, y: 2, z: 3
   [09:05:33] [c_2] e->Reset() c_2_inner_state->c_2_inner_state
   [09:05:33] [c_1] e->Chart_2_Started() c_1_outer_state->c_1_inner_state
   [09:05:33] [c_1] e->Reset() c_1_inner_state->c_1_outer_state
   x: 2, y: 2, z: 3
   [09:05:33] [c_1] e->Chart_2_Started() c_1_outer_state->c_1_inner_state
   [09:05:33] [c_1] e->Reset() c_1_inner_state->c_1_outer_state

Let's run the above trace output through the `sequence tool
<https://github.com/aleph2c/sequence>`_ and compare the resulting :ref:`sequence
diagram <reading_diagrams-sequence-diagrams>` and UML statecharts:

.. image:: _static/pub_sub_icons_2.svg
    :target: _static/pub_sub_icons_2.pdf
    :align: center
  
.. code-block:: python

   [Statechart: c_1] (Chart1: ActiveObject)
            top            c_1_outer_state      c_1_inner_state
             +-----start_at()---->|                    |
             |        (1)         |                    |
             |                    +--Chart_2_Started()>|
             |                    |        (3)         |
             |                    +<------Reset()------|
             |                    |        (4)         |
             |                    +--Chart_2_Started()>|
             |                    |        (7)         |
             |                    +<------Reset()------|
             |                    |        (8)         |
             |                    +--Chart_2_Started()>|
             |                    |        (9)         |
             |                    +<------Reset()------|
             |                    |       (10)         |

   [Statechart: c_2] (Chart2: Factory)
         top      c_2_inner_state
          +--start_at()->| publishes Chart_2_Started
          |     (2)      |
          |              +
          |               \ (5)
          |               Reset() publishes Chart_2_Started
          |               /
          |              <
          |              +
          |               \ (6)
          |               Reset() publishes Chart_2_Started
          |               /
          |              <

Here is what happens when we run our code:

1. c_1 (Chart1) starts and settles into the c_1_outer_state.
#. c_2 (Chart2) starts and transitions into the c_2_inner_state, which publishes
   Chart_2_Started.
#. c_1 reacts to the Chart_2_Started event, transitions from c_1_outer_state to
   c_1_inner_state, prints the contents of the Chart_2_started event's payload,
   then posts a Reset event to itself using the post_lifo API.
#. c_1 reacts to its Reset event, transitioning into c_1_outer_state.
#. c_2 receives a Reset event from our main thread, it publishes a
   Chart_2_Started event.
#. c_2 receives another Reset event from our main thread, it publishes a
   Chart_2_Started event.
#. c_1 reacts to the Chart_2_Started event, transitions from c_1_outer_state to
   c_1_inner_state, prints the contents of the Chart_2_started event's payload,
   then posts a Reset event to itself using the post_lifo API.
#. c_1 reacts to its Reset event, transitioning into c_1_outer_state.
#. c_1 reacts to the Chart_2_Started event, transitions from c_1_outer_state to
   c_1_inner_state, prints the contents of the Chart_2_started event's payload,
   then posts a Reset event to itself using the post_lifo API.
#. c_1 reacts to its Reset event, transitioning into c_1_outer_state.


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
Sequence diagrams are very useful and extremely fragile to design changes.  They
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
        |   (1)    |                |                |                |
        |          +--prototype()-->|                |                |
        |          |      (2)       |                |                |
        |          |                +                |                |
        |          |                 \ (3)           |                |
        |          |                 debug()         |                |
        |          |                 /               |                |
        |          |                <                |                |
        |          |                +-communicate()->|                |
        |          |                |      (4)       |                |
        |          |                |                +-sequence.rb()->|
        |          |                |                |      (5)       |


The horizontal axis describes the states we want to show in an interaction.  The
vertical axis represents time, time starts at the top of the page and moves into
the program's future, lower down the page.

Vertical bars descend from each state, as guides for your eyes.  These are
called "lifelines," the lifelines are connected by asynchronous events.  An
event can connect two different lifelines, or they can connect back on
themselves (like the debug event on the code lifeline).  Such an event
connection represents a state transition.

The UML sequence diagram standard describes ways we can define loops,
iterations, unexpected messages, lost messages, synchronous messages, actors and
all sorts of other stuff that we don't care about.  We don't care about this
stuff, because the engineering trade-off is not worth it.  The time spent to
build these beautiful and descriptive diagrams is wasted because they are broken
by the smallest change to your statechart.

So avoid spending a lot of time or effort on these diagrams, use code to
generate them, and avoid using their more advanced diagramming features.

.. _reading_diagrams-payloads:

Payloads
--------
Your statechart is running in its own thread.  An event can be published from
one thread and consumed by another thread.  This means if you put mutable data
in your event's payload, you could be creating a shared global variable between
two separate threads.  Shared global information should be locked and unlocked
if it's being used by multiple concurrent processes.

Instead of coming up with complicated locking mechanisms, wrap large common data
structures within their own statecharts and copy smaller payloads into named
tuples.  A named tuple is immutable, so you won't accidentally shoot yourself in
the foot by inadvertently creating a global variable shared between two
different threads.  You can draw your payloads into your statecharts like this:

.. image:: _static/immutable_payload.svg
    :target: _static/immutable_payload.pdf
    :align: center

Pepper these payload descriptions all over your drawings, you might be repeating
yourself, but the quick understanding that you will be getting from a glance
will pay for this trade-off.  The `namedtuple is nice to work with
<https://docs.python.org/3.5/library/collections.html#collections.namedtuple>`_.

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
direction.  You need to be able to destroy and reform these pictures, just as
casually as you would refactor your code.

So use a simple and customizable tool.  To draw the pictures in this
documentation I used UMLet.  With UMLet you can build custom templates, `here is
mine <https://github.com/aleph2c/umlet-statechart-template>`_.  And it is hard
to fall in love with a picture made by UMLet.

You don't have to use this tool or this template, there `a lot of other UML
drawing tools available
<https://en.wikipedia.org/wiki/List_of_Unified_Modeling_Language_tools>`_.

Another way to make your pictures easy to change is to limit the amount of
detail on them.  You don't have to draw every class and you can shrink a
complicated statechart into a kind of short hand.

There are some diagrams that are extremely expressive and extremely fragile.  I
can explain how a sequence diagram works to someone in 10 seconds.  But any
sequence diagram used to describe your statechart behavior, will be extremely
fragile to change.

You might feel reluctant to change your design, not because you are attached to
your picture, but because you don't want to re-write all of the boiler plate
code to describe your statechart in Python.  To avoid what used to take me hours
of work (mostly to debug) I have written some Ultisnips snippets for vim, that
mostly write the statechart code for me.  You can `find these snippets here
<https://github.com/aleph2c/vim_tmux/blob/master/snippets/python.snippets>`_.

UML can't begin to describe everything you can create with your Python code.
So, if you need to express a code's idea on the diagram, just write the code
directly onto the picture.

You may decide to extend or change how UML diagrams are drawn to match your way
of programming.  I have done this in this documentation.  There are a lot of
features that would make it very nice to view a statechart, like being able to
click on a diagram and drill in to see the specifics of that part of the
picture.  UMLet doesn't support this, and to get such a thing to show up in HTML
(this doc) you would need some sort of SVG library working with javascript.
Well, I don't have time to write that, and I'm not funded, so we will do the
best we have with the tools we got.

When you customize the way you draw a picture, just make sure the other
people on your team understand what you mean.

.. raw:: html

  <a class="reference internal" href="zero_to_one.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="examples.html"><span class="std std-ref">next</span></a>

.. [#]  `The Sunk Cost Fallacy <https://youarenotsosmart.com/2011/03/25/the-sunk-cost-fallacy/>`_
