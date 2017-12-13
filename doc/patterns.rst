.. _patterns:

.. hlist::
  :columns: 3

  * :ref:`ultimate hook<patterns-ultimate-hook>`
  * :ref:`reminder<patterns-reminder>`
  * :ref:`deferred event<patterns-deferred-event>`
  * :ref:`orthogonal component<patterns-orthogonal-component>`
  * :ref:`transition to history<patterns-transition-to-history>`
  * :ref:`multichart race<patterns-multichart-race>`
  * :ref:`multichart pend<patterns-multichart-pend>`

Patterns
========
The idea of software design patterns came from the architect Christopher
Alexander.  He wrote a book, a pattern language, about how different approaches
to architecture could be used across different scales (from the country to the
pantry) to help people feel better about living in their communities.  It's a
lovely book; a child can understand it yet it is still useful to professional
architects.

This can not be said for the book it inspired in computer science, "Design
Patterns: Elements of Reusable Object-Oriented Software"  This book *was not*
child friendly, in fact everyone I knew secretly hated it because of its
illegibility; but would make sure to have a copy of it on their shelf to look
like they were in the club.

The ideas within the book were great and the follow up books that translated it
into English were really useful.  Basically it described a set of techniques
for solving classes of problems that come up over and over again.  If you
haven't learned the patterns yet, find a copy of a patterns book written by a
practitioner in your language(s) and work through it.  You will level up.

In chapter 5 of "Practical UML STATECHARTS in C/C++" I was leveled up by Miro
Samek.  He describes 5 statechart patterns and made the bold claim that
**statecharts are a pattern of patterns**.  I completely agree with him.  So here
is my translation of his work into this library.  I'll start each pattern with
quotes from his book, then write about it within the context of this work.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. _patterns-ultimate-hook:

Ultimate Hook
^^^^^^^^^^^^^
Formal description:

    [The Ultimate Hook Pattern provides a] common facilities and policies for
    handling events but let clients override and specialize every aspect of the
    system's behavior.

    The semantics of state nesting provide the desired mechanism of handling
    all events, first in the context of the client code (the nested state) and
    of automatically forwarding of all unhandled events to the [parent state]
    (the default behavior). In that way, the client code intercepts every
    stimulus and can override every aspect of the behavior. To reuse the
    default behavior, the client simply ignores the event and lets the
    superstate handle it (the [child state] inherits behavior from the
    superstate) [#1]_

Makes sense to me.  Keep up! ;)

To understand the ultimate hook pattern, you first have to understand what a
hook is.  It is just some code in an ``if-elif`` clause.   A hook is just some
code that catches an event, runs your :term:`client code<Client Code>` and then
returns something which tells the event processor to stop searching.  **A hook
doesn't cause a state transition**.  It is a way to get the event processor's
search algorithm to do work for you without changing state.

You see, anytime the event processor is trying to figure out what to do with an
event it needs to :ref:`search your
statechart<recipes-what-a-state-does-and-how-to-structure-it>`.  If it finds
that it needs to do a transition, it will enlist the heavy-duty parts of it's
algorithm to make sure that the :term:`Harel Formalism<Harel Formalism>`
occurs.  The hook has nothing to do with this, because it short circuits the
search before it does a transition, but not before it gets this search algorithm
to do some useful work.

If your if-else structure in your state method catches the signal name of an
event, runs your code, then returns the ``return_status.HANDLED`` back to the
event processor, no state transition will occur.  This is how you make a hook.
You make sure that part of your if-elif clause catches the event signal, runs
your :term:`client code<Client Code>` and returns the ``return_state.HANDLED``
value.

.. image:: _static/ultimate_hook1.svg
    :align: center

Here is a simple example which demonstrates a hook.  In this example we will
show that we can get some client code to run when we post an event with the
signal name of BEHAVIOR_NAME to your statechart:

.. code-block:: python
  :emphasize-lines: 10-13

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(outer_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

The highlighted code describes the hook.  We see that when the BEHAVIOR_NAME
signal is caught by this state method it runs your :term:`client code<Client Code>` then returns ``return_status.HANDLED``.

The :ref:`spy<recipes-using-the-spy>` output would look like this:

.. code-block:: python
  :emphasize-lines: 7
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'INIT_SIGNAL:outer_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:outer_state',
   'your outer_state code here',
   'BEHAVIOR_NAME:outer_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

Lines 1-5 describe the first :term:`rtc<Run To Completion>` event which occurs
when we start the statechart.  Lines 5-9 of the
:ref:`spy<recipes-using-the-spy>` log actually describe the hook behavior.  The
event processor ran, searching the statechart starting at the outer_state
method to see if it knew how to process the BEHAVIOR_NAME signal and it did:
the :term:`client code<Client Code>` just
:ref:`scribbled<recipes-scribble-on-the-spy>` something into our
:ref:`spy<recipes-using-the-spy>` log so we can see what happened.  On line 7
we see the result of this in the :ref:`spy<recipes-using-the-spy>` log.
Furthermore, no state transition occurred.

.. image:: _static/ultimate_hook2.svg
    :align: center

Now suppose we add another state within the outer state and start our active
object there.

.. code-block:: python
  :emphasize-lines: 20-29, 32
  :linenos:

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your inner_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = outer_state
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

Then look at the :ref:`spy<recipes-using-the-spy>`:

.. code-block:: python
  :emphasize-lines: 9
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:inner_state',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'ENTRY_SIGNAL:inner_state',
   'INIT_SIGNAL:inner_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:inner_state',
   'your inner_state code here',
   'BEHAVIOR_NAME:inner_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

Ok, no surprises.  The inner_state hooked the BEHAVIOR_NAME signal and
ran some :term:`client code<Client Code>`.

.. image:: _static/ultimate_hook3.svg
    :align: center

Now let's remove the handling of the BEHAVIOR_NAME from our
inner state and see what happens when we start the active object in the
inner_state then send it an event with the BEHAVIOR_NAME.

.. code-block:: python
  :emphasize-lines: 28-29
  :linenos:
  
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    #if(e.signal == signals.BEHAVIOR_NAME):
    #  # your code would go here
    #  chart.scribble("your inner_state code here")
    #  status = return_status.HANDLED
    #else:
    #  chart.temp.fun = outer_state
    #  status = return_status.SUPER
    chart.temp.fun = outer_state
    status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

In the highlighted code you can see that I adjusted the inner_state to run as
if it's ``else`` method clause was always active.  I did this so that it would not
handle the BEHAVIOR_NAME signal.  Now we run the code and look at the
:ref:`spy<recipes-using-the-spy>` output.

.. code-block:: python
  :emphasize-lines: 8-11
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:inner_state',
   'SEARCH_FOR_SUPER_SIGNAL:outer_state',
   'ENTRY_SIGNAL:outer_state',
   'ENTRY_SIGNAL:inner_state',
   'INIT_SIGNAL:inner_state',
   '<- Queued:(0) Deferred:(0)',
   'BEHAVIOR_NAME:inner_state',
   'BEHAVIOR_NAME:outer_state',
   'your outer_state code here',
   'BEHAVIOR_NAME:outer_state:HOOK',
   '<- Queued:(0) Deferred:(0)']

The highlighted lines show how our event processor tried to determine what to
do with the event containing the BEHAVIOR_NAME signal.

It called the inner_state with the event (8), it wasn't handled, so it
called the parent outer_state with the same event (9) and we see on
line (10) that the outer_state :term:`client code<Client Code>` was run.  Finally, on line (11)
the spy instrumentation tells us that it detected a hooked event.  When you see
this in the log it means there was no state transition.

So, the outer_state hook code caught an event that was sent to the
inner_state.  The :term:`Harel Formalism<Harel Formalism>` followed by the
event processor determines that when it has an event, it will search outward
from the current state, to the next :term:`parent state<Parent State>`, then the next parent state
over and over until your event is handled or, it reaches the top most state of
your :term:`HSM<Hierarchical State Machine>`. This means that any inner state
method will automatically inherit the hook code of any outer state.  The outer
most state contains the ultimate hook; this is why the pattern is called what
it is.

.. image:: _static/ultimate_hook4.svg
    :align: center

.. note::

  To show that there is some sort of explicit design feature occuring on your
  diagram, something that might be too subtle for someone to see right away UML
  provides a dotted-collaboration-bubble.  It is very easy to over use
  this feature and clutter up your diagram.

You can overwrite the behavior of the outer state hooks simply by explicitly
handling the signal in an inner state.  These ideas are very similar to
inheritance and overloading in object oriented programming.

As a designer you would write default :term:`client code<Client Code>` behavior in the outer states
of charts, and all of your inner states would get this behavior for free.  If
they needed to overwrite this behavior they would specifically handle the
event in their state methods.

.. image:: _static/ultimate_hook5.svg
    :align: center

You would place generic reactions to events in your outer states and place the
specific responses in your inner states. Let's build out the above diagram:

.. code-block:: python
  :emphasize-lines: 6-8, 10-12, 14-17
  :linenos:
  
  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def process_a_generic(chart, e):
    chart.scribble('processing a generic')
    return return_status.HANDLED

  def process_b_generic(chart, e):
    chart.scribble('processing b generic')
    return return_status.HANDLED

  # overrides the generic hook while in the specific state
  def process_a_specific(chart, e):
    chart.scribble('processing a specific')
    return return_status.HANDLED

  chart = Factory('ultimate_hook_example')
  generic = chart.create(state='generic'). \
    catch(signal=signals.a, handler=process_a_generic). \
    catch(signal=signals.b, handler=process_b_generic). \
    to_method()

  specific = chart.create(state='specific'). \
      catch(signal=signals.a, handler=process_a_specific). \
      to_method()

  chart.nest(generic, parent=None). \
        nest(specific, parent=generic)

  chart.start_at(specific)
  chart.post_fifo(Event(signal=signals.b))
  chart.post_fifo(Event(signal=signals.a))
  time.sleep(0.001)
  pp(chart.spy())

First of all we notice that instead of using an active object the diagram asks
us to use a :ref:`factory<towardsthefactoryexample-using-the-factory-class>`.
To use the factory we create states and tie specific signals to callback
functions.

The highlighted code shows the callback functions that are acting like hooks.
Pay special attention to what they return.  If they do not return
``return_status.HANDLED`` they will not work as hooks.

We can deterime if we got the expected behavior by looking at the
:ref:`spy<recipes-using-the-spy>` log:

.. code-block:: python
  :emphasize-lines: 10, 11, 14, 15
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:specific',
   'SEARCH_FOR_SUPER_SIGNAL:generic',
   'ENTRY_SIGNAL:generic',
   'ENTRY_SIGNAL:specific',
   'INIT_SIGNAL:specific',
   '<- Queued:(0) Deferred:(0)',
   'b:specific',
   'b:generic',
   'processing b generic',
   'b:generic:HOOK',
   '<- Queued:(1) Deferred:(0)',
   'a:specific',
   'processing a specific',
   'a:specific:HOOK',
   '<- Queued:(0) Deferred:(0)']

On lines 10 and 11 we see the reaction to our first ``b`` signal.  As expected
the generic state's hook function was run while the statechart remained in the
specific state. 

On lines 14 and 15 we see the specific behavior for the ``a`` signal.  The
statechart ran the :term:`client code<Client Code>` in the specific state then
stopped processing the signal.


.. _patterns-reminder:

Reminder
^^^^^^^^

Formal description:
  
  Make the statechart topology more flexible by inventing an event an posting
  it  to itself.

  Often in state modeling, loosely related functions of a system are strongly
  coupled by a common event. Consider, for example, periodic data acquisition,
  in which a sensor producing the data needs to be polled at a predetermined
  rate. Assume that a periodic TIME_OUT event is dispatched to the system at
  the desired rate to provide the stimulus for polling the sensor. Because the
  system has only one external event (the TIME_OUT event), it seems that this
  event needs to trigger both the polling of the sensor and the processing of
  the data. A straightforward but suboptimal solution is to organize the state
  machine into two distinct orthogonal regions (for polling and processing).
  However, orthogonal regions increase the cost of dispatching events ... and
  require complex synchronization between the regions because the polling and
  processing are not quite independent. [#2]_

.. note::

  Programming a statechart with :term:`orthogonal regions<Orthogonal Region>` is
  computationally expensive.  So if you find yourself drawing two seperate states
  with a lot of arrows connecting them, remind yourself of the reminder pattern.

The reminder pattern uses the ultimate hook pattern mixed with
:term:`artificial event<Artificial Event>` injection.  It's an artificial event
because it is invented by the statechart and injected to itself rather than
being invented and injected by an outside caller.

I'll try to explain this idea by showing a design using orthogonal regions,
show how it is expensive and then refactor the design using the reminder
pattern.

We will begin with some specifications:

* Part of the system will poll a sensor based on a system clock running with
  a period of 100ms.
* Once polled this information will be sent to some processing code.
* After five such events, the system will perform some processing and it will
  enter a busy state (maybe communicating with a server).
* While the unit is in a busy state it should not poll the sensor or process
  input.
* After the busy process is completed the system should go back into it's
  polling mode.

Here is a first shot at implementing this specification:

.. image:: _static/reminder1.svg
    :align: center

We create a polling state which upon entry poles something.  Any time there is
a time out it will re-enter the state making this happen.  

Then when it Initializes it transitions into the processing state.  Upon
entering the processing state we add one to the ``chart.processing_count`` and
then process the message.  When the processing state initializes itself it will
either go back to the polling state or enter the busy state, if the
``chart.processing_count`` is high enough.

Upon entering the busy state the ``chart.busy_count`` is set to zero.  Then the
TIME_OUT event is used with a :term:`hook<Hook>` to work the information.  In
this example we just scribble "busy" into the spy log.  Then we add 1 to our
``chart.busy_count``.  If the count is big enough we transition back to the
polling state.  Upon exiting the processing state, the
``chart.processing_count`` is set to 0.  That should work!

But notice the large **Xs** on the diagram.  These are there to show that they
are illegal transitions.  The Miro Samek event processoring algorithm will only
allow init events to drill further into child states; they can not leave there
current state and navigate to another region of the chart.   It's an honest
mistake.

Let's see what happens when we try to make this broken statechart

.. code-block:: python
  :emphasize-lines: 11,12,25,26

  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def polling_time_out(chart, e):
    return chart.trans(polling)

  def polling_enter(chart, e):
    chart.scribble("polling")
    return return_state.HANDLED

  def polling_init(chart, e):
    # illegal (init can't leave parent states)
    return chart.trans(processing)

  def processing_entry(chart, e):
    chart.processing_count += 1
    chart.scribble("processing")
    return return_status.HANDLED

  def processing_init(chart, e):
    status = None
    if chart.processing_count >= 5:
      status = chart.trans(busy)
    else:
    # illegal (init can't leave parent states)
      status = chart.trans(polling)
    return status

  def processing_exit(chart, e):
    chart.processing_count = 0
    return return_status.HANDLED

  def busy_entry(chart, e):
    chart.busy_count = 0
    return return_status.HANDLED

  def busy_time_out(chart, e):
    chart.busy_count += 1
    status = return_status.HANDLED
    if chart.busy_count >= 5:
      status = chart.trans(polling)
    return status

  chart = Factory('reminder_pattern_needed_1')
  chart.augment(other=0, name="processing_count")
  chart.augment(other=0, name="busy_count")

  polling = chart.create(state="polling"). \
              catch(signal=signals.TIME_OUT, handler=polling_time_out). \
              catch(signal=signals.INIT_SIGNAL, handler=polling_init). \
              to_method()

  processing = chart.create(state="processing"). \
              catch(signal=signals.ENTRY_SIGNAL, handler=processing_entry). \
              catch(signal=signals.INIT_SIGNAL, handler=processing_init). \
              catch(signal=signals.EXIT_SIGNAL, handler=processing_exit). \
              to_method()

  busy = chart.create(state="busy"). \
          catch(signal=signals.ENTRY_SIGNAL, handler=busy_entry). \
          catch(signal=signals.TIME_OUT, handler=busy_time_out). \
          to_method()

  chart.nest(polling, parent=None). \
        nest(processing, parent=None). \
        nest(busy, parent=processing)

  chart.start_at(polling)
  chart.post_fifo(Event(signal=signals.TIME_OUT), times=20, period=0.1)
  time.sleep(5)
  pp(chart.spy())

I have highlighted the illegal transition.

If we run the code we will see:

.. code-block:: python

  miros.hsm.HsmTopologyException: 
    impossible chart topology for HsmEventProcessor.init,
    see HsmEventProcessor.init doc string for details

So, how do we make this software work?  When you see this
``HsmTopologyException``, it's probably time to consider another way to design
your statechart.  We will get to that shortly, but for now let's find a way to force
this software to work they way we want it too.

Instead of making the INIT_SIGNAL transition outside of the state, instead we
could invent a new signal, post it to ourselves and pretend like it came from
outside of the active object and then react to it like we would any other
event.  This is why it is called an :term:`artificial event<Artificial Event>`.
hey

.. _patterns-deferred-event:

Deferred Event
^^^^^^^^^^^^^^

.. _patterns-orthogonal-component:

Orthogonal Component
^^^^^^^^^^^^^^^^^^^^

.. _patterns-transition-to-history:

Transition To History
^^^^^^^^^^^^^^^^^^^^^


.. _patterns-multichart-race:

Multichart Race
^^^^^^^^^^^^^^^


.. _patterns-multichart-pend:

Multichart Pend
^^^^^^^^^^^^^^^

.. [#1] p.206 Practical UML STATECHARTS in C/C++, Second Edition
.. [#2] p.211 Practical UML STATECHARTS in C/C++, Second Edition

