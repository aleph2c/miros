.. _examples:

Examples
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. _examples-single-chart-examples:

Single Chart Examples
---------------------


.. _examples-active-object-example:

Active Object Example
^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/simple_example_1.svg

In this example we will show how to build the statechart structure described
above using an `ActiveObject`.  We will then learn how to create some events
and present them to the chart so we can see how it reacts.

If you are new to statecharts and if you haven't heard of an active object
before, I would recommend that you draw the above design on a piece of paper,
and scribble on it as we move through the example.

The code blocks in this section are specific to this library, but the
principals apply to any other system using the active object design pattern.

The above diagram describes the structure of how we would like our code to
react to events.  Think of it as a plan of plans, and the `ActiveObject` will
help you build such a structure.

What is missing from the picture is the action itself; what events are
happening and when.  The `ActiveObject` allows you to control this action and
watch what happens, in that it provides the facilities to reflect upon the
action that the statechart took as a response to your programmed stimulation.

This reaction could be a change of state, or just a running of custom code upon
a signal.  By "custom code", I mean code that is not needed to describe the
reactive structure itself. For instance, the inner state has ``print("hello
world")`` linked to it's response to an entry event.

Before we print our `hello world`, we need to build up the statechart
structure, then we send events to the chart.

Let's begin by building the structure.

First we import some items from the miros library:

.. code-block:: python

  from miros.event import Event
  from miros.event import signals
  from miros.event import return_status

  from miros.activeobject import spy_on
  from miros.activeobject import ActiveObject

Now we write our state methods.  Each of these methods will represent a specific
state in our diagram.

Let start by writing the `outer` state method.  This method will represent the
rectangle labeled `outer` in the above diagram.

.. code-block:: python

  @spy_on
  def outer(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      # outer state custom entry-code here
      status = return_status.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      # outer state custom exit-code here
      status = return_status.HANDLED

    elif(e.signal == signals.WaitComplete):
      # WaitComplete signal code here
      status = chart.trans(middle)

    elif(e.signal == signals.ResetChart):
      # ResetChart signal code here
      status = chart.trans(outer)

    else:
      # This signal wasn't managed, pass a
      # reference to the # method that is
      outside of us
      status, chart.temp.fun = \
        return_status.SUPER, chart.top
    return status

We see that our method is basically a big if-else structure, which reads the
signal attribute of the `e` (Event) variable and decides what to do about it. We
see that this state reacts to the `WaitComplete` by calling the ``trans`` method
with the `middle` state as an argument.  This will represent the arrow labeled
`WaitComplete` on the above diagram connecting the `outer` state with the
`middle` state.

Likewise, we see that this method calls ``trans`` with the `outer` method as an
argument when it receives an event with the signal named `ResetChart`.  This
represents the arrow which loops from-and-to the `outer` rectangle in the above
diagram.

You can pack a lot of complexity into an `ActiveObject`.  They are very dynamic
and as a result they can be very difficult to debug.  For this reason the miros
library allows you to instrument your state methods so that you can see how they
have responded to the different types of events you send at them.  

This instrumentation is done with the ``@spy_on`` decorator.  This adds a
special kind of logging to the method, more will be said about this as our
example continues.

Now lets write the middle state:

.. code-block:: python

  @spy_on
  def middle(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      # middle entry code here
      status = return_status.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      # middle exit code here
      status = return_status.HANDLED

    elif(e.signal == signals.INIT_SIGNAL):
      # middle init code here
      status = chart.trans(inner)
    else:
      status, chart.temp.fun = \
        return_status.SUPER, outer
    return status

Now lets write the inner state:

.. code-block:: python

  @spy_on
  def inner(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("hello world")
      status = return_status.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      # inner exit code here
      status = return_status.HANDLED

    else:
      status, chart.temp.fun = \
        return_status.SUPER, middle
    return status

Now that our states are defined, we create an `active object` and tell it where
to start in our diagram:

.. code-block:: python

  ao = ActiveObject()
  ao.start_at(outer)

The call to the ``start_at`` active object method will create two different
:abbr:`daemonic threads(threads that stop when the main program stops running)`,
one is for managing the active object itself and the other is for managing the
`ActiveFabric`.  The active fabric is just a process that dispatches methods
between all of the active objects in your system.  Then ``start_at`` causes the
active object to change state by climbing into the statechart to the state which
was provided as an argument; `outer`.

We can see what happened by reading some of the results of our instrumentation,
through the `spy` api:

.. code-block:: python

    print(ao.spy_full())
      # ['START', 
      #  'SEARCH_FOR_SUPER_SIGNAL:outer', 
      #  'SEARCH_FOR_SUPER_SIGNAL:top', 
      #  'ENTRY_SIGNAL:top', 
      #  'ENTRY_SIGNAL:outer', 
      #  'INIT_SIGNAL:outer', 
      #  '<- Queued:(0) Deferred:(0)']

Here we see something about the interplay between the active object and the
states which it interacts with.  Before it can climb into the `outer` state, it
needs to `search` the chart so it can know what to do.  Once it knows what to
do, it takes action by sending a series of signals at our state methods:  It
sends the entry signal to `top` (and internal state method), then the entry
signal to the `outer` state, then the `init` signal (the big black dot in our
picture) to the `outer` state.

The spy api is very detailed.  If you would like to just see a summary of what
happened you can use the `trace` instrumentation instead.

.. code-block:: python

    print(ao.trace())
      # 09:53:38.941445 [01352] None: top->outer

The `trace` is different from our `spy` in that it does not show all of the
activity resulting from our internal event processing, but instead just shows
information about state transitions and the signal which caused the transition
to occur.  In this case there was :abbr:`no signal(the transition was caused by
a start_at)` so the `trace` displays ``None`` for the signal name.  The `trace`
does give us some new information though: it outputs a timestamp of when the
transition took place.

Now that our state is in ``outer`` state, we can send an event at it.  After
the statechart reacts we can see what happened by viewing our instrumentation:

.. code-block:: python

  # clear our spy and trace logs
  ao.clear_trace()
  ao.clear_spy()

  # Send an event with signal 'WaitComplete' so we can 
  # watch the reaction
  event_wait_complete = Event(signal=signals.WaitComplete)
  ao.post_fifo(event_wait_complete) #=> "hello world"

  # Look at the reaction of our statechart in greater detail
  print(ao.spy_full())
    # ['WaitComplete:outer',
    #  'SEARCH_FOR_SUPER_SIGNAL:middle',
    #  'ENTRY_SIGNAL:middle',
    #  'INIT_SIGNAL:middle',
    #  'SEARCH_FOR_SUPER_SIGNAL:inner',
    #  'ENTRY_SIGNAL:inner',
    #  'INIT_SIGNAL:inner',
    #  '<- Queued:(0) Deferred:(0)']

  # Look at the reaction of our chart with less detail
  print(ao.trace()) #=>
    # 10:34:47.344218 [01352] W: outer->inner

From the trace output we see that we were in the `outer` state and an event with
the `WaitComplete` signal caused us to transition into the `inner` state.  This
is true, but it doesn't really describe what happened.

If we want the full story we need to look at the results of our spy.  We see
that the system was in the `outer` state and it reacted to an event with the
signal `WaitComplete`.  It saw that it needed to transition into the `middle`
state, so it issued an event with the `entry` signal to the middle state.  If
you had code linked to this event in the `middle` state method it would have
been run.  Once it is in the `middle` state it sees that there is an `init`
handler, so it fires another event with the signal `init` which causes a
transition into the `inner` state.  Since the `inner` state required entry, the
event processor created an event with the `entry` signal and sent it to the
`inner` state.  Any entry code within the `inner` state event handler would have
been run at this point and time.  Finally, the event processor issued an other
`init` event to the inner state.  The inner state does not handle this event, so
it is ignored and our system settles into the `inner` state.  It will remain
here until it has to react to events provided by the user.

As mentioned previously, their are two different threads running in the
background since we created our `active object`.  They are both pending on
queues.  The number of items in the active object queue can be seen in our `spy`
instrumentation.  We see that at the end of this reaction to the event with the
`WaitComplete` signal, there was nothing in the queue so the `active object`
thread had nothing to do.  It is just waiting.

Lets stop both threads, and place a number of events into the queue managed by the
active object.

.. _label:
.. code-block:: python

    import time
    # stop the threads
    ao.stop()

    # clear the spy and the trace
    ao.clear_spy()
    ao.clear_trace()

    # post a number of events and see what happens
    event_wait_complete = Event(signal=signals.WaitComplete)
    event_reset_chart = Event(signal=signals.ResetChart)
    ao.post_fifo(event_wait_complete)
    ao.post_fifo(event_reset_chart)   
    ao.post_fifo(event_wait_complete)
    ao.post_fifo(event_reset_chart)
    time.sleep(0.3)

We would expect that nothing should happens since the task which is pending on
an event has been shut down.  Let's look at the results, first with the trace:

.. code-block:: python

    print(ao.trace)
     # 11:35:20.469870 [01352] WaitComplete: inner->inner
     # 11:35:20.470871 [01352] ResetChart: inner->outer
     # 11:35:20.470871 [01352] WaitComplete: outer->inner
     # 11:35:20.470871 [01352] ResetChart: inner->outer

It seems that our active object woke up even though we killed the thread.  This
is true, because the active object has a phoenix thread; if it has been killed,
and something has been placed in the queue it will resurrect itself and get back
to work.

We see from the high level state summary that all 4 post of our events caused
state transitions in our statechart.  

To begin with we were in the `inner` state and the `WaitComplete` signal was
received.  If we look at the diagram we see that the `inner` state does not
handle this signal so it passes control to the `middle` state.  The `middle`
state does not handle the `WaitComplete` either so it passes control to the
`outer` state.  The `outer` state knows what to do with the `WaitComplete`
signal, it must transition to the `middle` state.  

This is what is meant by behavioral inheritance.  All of the child states of the
`outer` state will all behave the same as the `outer` state does the
`WaitComplete` event; they inherit the behavior of the `outer` state.

Now lets get back to the story.  The middle state has an `init` signal, the big
black dot, which requires a transition to the `inner` state, so it does this.
Ultimately the statechart rests in the `inner` state just in time for the active
object thread to send the next event at it, the event containing the
`ResetChart` signal.

The `trace` output summarizes the last paragraph as:

.. code-block:: python

  # 11:35:20.469870 [01352] WaitComplete: inner->inner

The `inner` state doesn't know what to do with the `ResetChart` signal, so it
passes control to the `middle` state.  The `middle` state doesn't know what do
to with it so it passes control out to the `outer` state.  It sees that it knows
what to do, which is to leave and re-enter itself.  More will be said about this
in a bit when we look at the spy.  Skipping some details, we see that when it is
completed, the statechart rests in the `outer` state, because it does not
respond to the `init` signal (it does not have a black dot).  Then the active
object dispatches a `WaitComplete` signal to the `outer` state.

The `trace` output summarizes the last paragraph as:

.. code-block:: python

  # 11:35:20.470871 [01352] ResetChart: inner->outer

The `outer` state knows what to do with this, it needs to transition to the `middle`
state, which in turn will transition into the `inner` state.  At this point the
chart rests, just in time to be sent an event with the `ResetChart` signal.
Which repeats a behavior we have already described.

The `trace` output summarizes the last paragraph as:

.. code-block:: python

  # 11:35:20.470871 [01352] WaitComplete: outer->inner
  # 11:35:20.469870 [01352] WaitComplete: inner->inner

If that isn't enough detail for you, let's look at what the active object is
actually doing by viewing the spy instrumentation:

.. code-block:: python

  print(ao.spy_full())
    #['WaitComplete:inner',
    # 'WaitComplete:middle',
    # 'WaitComplete:outer',
    # 'EXIT_SIGNAL:inner',
    # 'SEARCH_FOR_SUPER_SIGNAL:inner',
    # 'EXIT_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:middle',
    # 'ENTRY_SIGNAL:middle',
    # 'INIT_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:inner',
    # 'ENTRY_SIGNAL:inner',
    # 'INIT_SIGNAL:inner',
    # '<- Queued:(3) Deferred:(0)',
    # 'ResetChart:inner',
    # 'ResetChart:middle',
    # 'ResetChart:outer',
    # 'EXIT_SIGNAL:inner',
    # 'SEARCH_FOR_SUPER_SIGNAL:inner',
    # 'EXIT_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:middle',
    # 'EXIT_SIGNAL:outer',
    # 'ENTRY_SIGNAL:outer',
    # 'INIT_SIGNAL:outer',
    # '<- Queued:(2) Deferred:(0)',
    # 'WaitComplete:outer',
    # 'SEARCH_FOR_SUPER_SIGNAL:middle',
    # 'ENTRY_SIGNAL:middle',
    # 'INIT_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:inner',
    # 'ENTRY_SIGNAL:inner',
    # 'INIT_SIGNAL:inner',
    # '<- Queued:(1) Deferred:(0)',
    # 'ResetChart:inner',
    # 'ResetChart:middle',
    # 'ResetChart:outer',
    # 'EXIT_SIGNAL:inner',
    # 'SEARCH_FOR_SUPER_SIGNAL:inner',
    # 'EXIT_SIGNAL:middle',
    # 'SEARCH_FOR_SUPER_SIGNAL:middle',
    # 'EXIT_SIGNAL:outer',
    # 'ENTRY_SIGNAL:outer',
    # 'INIT_SIGNAL:outer',
    # '<- Queued:(0) Deferred:(0)']

When you scan such output with your eyes, you can split it into
behavioral chunks, based on the ``<- Queued:(n) Deferred:(m)`` lines.  The `n`
stands for the number of events that are waiting to be processed by the active
object when it is completed processing the one it is currently working on.  The
`m` stands for the number of events that have been squirreled away by the
statechart as a part of a design pattern that is not used in this example.

The information between the ``<- Queued:(n) Deferred:(m)`` statements represent
what the active objects event processor actually did with the previous event,
and how the chart reacted to it.  This phase of operation is called a `run to
completion`: rtc.

.. code-block:: python

  # Thou shalt NOT interrupt a statechart part way through its
  # reaction to an old event, with a new event.

Don't worry about this rule, the active object takes care of it for you.  This
is why it has queues.  Any new event is just placed in the queue until the
previous reaction is completed.  Only then will the active object force the
statechart to react to it.  

So, lets use the ``<- Queued: (n) Deferred:(m)`` statements to break out the
first rtc reaction of our statechart:

.. code-block:: python

    ['WaitComplete:inner',
     'WaitComplete:middle',
     'WaitComplete:outer',
     'EXIT_SIGNAL:inner',
     'SEARCH_FOR_SUPER_SIGNAL:inner',
     'EXIT_SIGNAL:middle',
     'SEARCH_FOR_SUPER_SIGNAL:middle',
     'SEARCH_FOR_SUPER_SIGNAL:middle',
     'ENTRY_SIGNAL:middle',
     'INIT_SIGNAL:middle',
     'SEARCH_FOR_SUPER_SIGNAL:inner',
     'ENTRY_SIGNAL:inner',
     'INIT_SIGNAL:inner',
     '<- Queued:(3) Deferred:(0)',

The statechart was in the state `inner`, it received the event with the signal
name `WaitComplete`.  At the end of the spy log we see that the `Queued` item
has 3 items in it.  This makes sense since we sent 4 events to the statechart,
and this part of the spy represents how the first event was processed.

Before we break down this spy log in detail, lets look back at the ``Queued:(n)
Deferred:(m)`` items that followed in the log:

.. code-block:: python

  ... the 1st rtc (1st event processed)
  '<- Queued:(3) Deferred:(0)']
  
  ... the 2nd rtc (2nd event processed)
  '<- Queued:(2) Deferred:(0)']
  
  ... the 3nd rtc (3th event processed)
  '<- Queued:(1) Deferred:(0)']
  
  ... the 4nd rtc (4th event processed)
  '<- Queued:(0) Deferred:(0)']
  
  .. the queue is empty so our active object threads wait

Now that we know how to break a large spy log into behavioral chunks, lets look
at the first chunk in detail and compare it to the trace output which was used
for tracking the same response.  Remember that that this represents the
statechart's reaction to the event with the `WaitComplete` signal while it was
in the `inner` state.

Since the trace is easy to understand, we will look at it first:

.. code-block:: python

  11:35:20.469870 [01352] WaitComplete: inner->inner

The trace says "we were in the `inner` state, then we got a signal named
`WaitComplete` and then we transitioned back into the `inner` state".  This
does not even begin to tell the story, to get a better idea of what actually
happened, we look at the result of the spy instrumentation for the same
reaction:

.. code-block:: python

  ['WaitComplete:inner',
   'WaitComplete:middle',
   'WaitComplete:outer',
   'EXIT_SIGNAL:inner',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'EXIT_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:middle',
   'ENTRY_SIGNAL:middle',
   'INIT_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'INIT_SIGNAL:inner',
   '<- Queued:(3) Deferred:(0)',

Let's break it down into parts and try to make sense of how the `inner` state
reacted to the `WaitComplete` event.

.. code-block:: python

  ['WaitComplete:inner',
   'WaitComplete:middle',
   'WaitComplete:outer',
   'EXIT_SIGNAL:inner',

The spy says, `inner` reacted to `WaitComplete`, it didn't know how to handle
this signal so it passed it out to it's parent state, `middle`.  The `middle`
state didn't know how to handle `WaitComplete` either, so it passed it out to
it's parent state, `outer`.  The `outer` state knew how to handle this event,
because there is something else happening on the next line of the spy log.  

This was the search phase of the `ActiveObject` event processor; it is looking
at the statechart, querying each of it's states with various events to
determine what to do.

.. code-block:: python

   'EXIT_SIGNAL:inner',  # repeated from above
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'EXIT_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:middle',

Let's rewind our output a bit, starting at the ``EXIT_SIGNAL:inner`` in our
log.  Now that the event processor knows what to do it must determine how to do
it.  

To get from the `inner` state to the `outer` state, the statechart needs to
exit the inner state, then exit the middle state.  When a state is exited, the
`EXIT_SIGNAL` event is sent to that state, this is what we see in this part of
the spy log.  We see these `EXIT_SIGNAL` events happening in the states where
they are needed, and we see some `SEARCH_FOR_SUPER_SIGNAL` events being sent at
the various states, so that the event processor can figure out what to do next.
If you are just debugging your design, you can ignore these
`SEARCH_FOR_SUPER_SIGNAL` items in your spy log, but if you are debugging the
event processor itself, these lines are very important.

At this point, we are at the tail end of the `WaitComplete` arrow in our
diagram.  The tip of the arrow is asking us to enter the `middle` state. Lets
look at that part of the story:

.. code-block:: python

  'SEARCH_FOR_SUPER_SIGNAL:middle',
  'SEARCH_FOR_SUPER_SIGNAL:middle',
  'ENTRY_SIGNAL:middle',

At this point it needed to move from the `outer` state into the `inner` state,
but to do that it first had to figure out how to get there.  This is why we see
the `SEARCH_FOR_SUPER_SIGNAL` events here.  Once it determines how what it
wants it does it.  It enters the `middle` state by sending the `ENTRY_SIGNAL`
event to the middle state.

We are now in the `middle` state. 

On our diagram we see that in the `middle` state rectangle, there is a big
black dot with the arrow attached to it.  Anytime you see a black dot in a
state it means that there is some initialization code that it needs to run.

The arrow attached to this dot represents what this initialization code would
like to do, it would like us to run it's initialization code, then, leave the
`middle` state and go to the `inner` state.

Here we see that the statechart did just that, it ran the `INIT_SIGNAL` event
in the `middle` state, searched then ran the `ENTRY_SIGNAL` event in the
`inner` state.

.. code-block:: python

  'INIT_SIGNAL:middle',
  'SEARCH_FOR_SUPER_SIGNAL:inner',
  'ENTRY_SIGNAL:inner',

Now that the statechart has found itself in the `inner` state, it needs to run
the `inner` states initialization code.  When we look at the diagram we don't
see any big black dots in the inner state so we would expect the chart to come
to rest here.  It does, the run to completion event is exhausted and it outputs
how many events are waiting for our `ActiveObject` thread's attention:

.. code-block:: python

  # 'INIT_SIGNAL:inner',
  # '<- Queued:(3) Deferred:(0)',

We see that three events were waiting in the Queue, which means that the
`ActiveObject` thread will pull the next item, run to completion, then do it
again and again.



.. _examples-simple-posting-example:

Simple Posting Example
^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/posting_example.svg

Here we see an active object.  To understand it, lets take the following steps:

1. Look at the states and see how they are related to one another in a hierarchy.
2. What external events exist and how the relate to the states.
3. What custom code has been placed within the hierarchy.

In the above example we see three different states interacting with 4 different
user defined events.  The outer state contains a middle state which contains an
inner state.  

The event with signal name *A* will cause a transition from the
middle state to the inner state.  The event with signal name *B* will cause the
outer event to exit, print "flash b!" then enter back into the outer state.
The event with the signal name *C* will cause the outer state to transition
into the middle state.  Finally, the event with the signal name *D* will cause
the ``recall`` method to be triggered in the outer state.

Now that we have a feeling for how the states relate and how they react to
events, lets look at the custom code that has been placed within the
hierarchical structure.

We see that, as previously mentioned, the outer state contains some signal
handling for the *D* named event.

The middle state has some code that is run upon entering the state.  It looks
like we are posting an event to the chart named *A*, that we want it to happen
3 times, with a period of 1 [second] and that we would like it to be deferred. The
entry condition also contains code which *augments* the chart with something.

The middle state has some exit code, where we are canceling an event.

Upon entering, the inner state, calls the defer method with an Event named *B*.
When the innner state is initialized, it prints hello world to the terminal,
then stops processing.

Generally speaking we have an idea about what is going on with the chart, now
let's look how to implement this design using the miros library, then start it
up in the ``outer`` state.  We will do this in three steps:

1. We will define the state methods and fill them with the custom code in the
   diagram.
2. We will create an active object
3. We will tie our active object to the state methods, by starting it within
   the ``outer`` state.
4. We will trigger an event and watch the chart react.

The outer state method would look like this:

.. code-block:: python
  :linenos:

  @spy_on
  def outer(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      ao.recall()
      status = state.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = state.HANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = state.HANDLED
    elif(e.signal == signals.D):
      ao.recall()
      status = state.HANDLED
    elif(e.signal == signals.B):
      print("flash B!")
      status = ao.trans(outer)
    else:
      status, ao.temp.fun = state.SUPER, ao.top
    return status

On line **1** we see we are using the ``@spy_on`` decorator.  This will allow us to
look at how the chart behaves in a log once we start sending events to
it.

Line **2** has the state name, and the method signature.  The ``ao`` object will be
overwritten with ``self`` when this method is used by an active object.
However, it can be used by other active objects as well, in that it is a kind
of slide that can be shared between objects.  So long as we don't mark the
function's name space directly we could share this method between as many
active objects as we construct in our system.  In this example we only use this
method within one active object.  The second argument in the method signature
contains the event that is being sent to this state method.

On line **3** we see the ``status`` variable defined.  Pay special attention to
this status variable, because it is used by the event processor to determine
what to do as it searches the chart hierarchy while responding to various
events.  We will talk about this in greater detail as we move through the
example.

On lines **4-6**, we see the entry handling for this state.  If we are entering the
state (line **4**), then call the ``recall`` method of the active object (line **5**)
and finally set the ``status`` to ``HANDLED``, or tell the event processor that
we know what to do with this event and it does not have to recurse the chart
to respond to the event anymore (line **6**).

On line *7-8* we are saying, run no custom code upon exiting the state.  One
line *9-10* we are saying, no custom code needs to be run to initialize this
state.

Lines **11-13** describe this state's reaction to an event with the **D**
signal.  It runs the ``recall`` method of the active object (line **12**) then
sets the status variable to ``HANDLED``.  If there is an event in the deferred
queue of the active object it will be placed into the fifo for the next run to
completion event.  This probably won't make sense to you yet, don't worry when
we move through the dynamics of the chart, we will see what this means.  Line
**13** tells the event processor that the **D** signal was handled.  This means
that if the **D** signal was received by the chart while it was in another
state, that the code on line 12 was run, then control was passed back to the
state which received the event.  This behavior is an example of the ultimate
hook pattern which you can read about in the section titled
:ref:`patterns-ultimate-hook`.

Lines **14-16** describe the **B** arrow on the diagram.  If any state within
our state chart receives an event called **B** we would like it to pass control
to the outer state (line 14,16), then exit the outer state, run ``print(flash
B)`` (line 15) then re-enter the outer state (line 16).  Pay special attention
to line 16.  Here we are using the ``trans`` method, which will return the
status.  Unlike the other parts of this method, we are not saying that the
status is HANDLED, here we let the trans method decide how to set this
variable.  This is important since it allows the event processor to perform the
work required by our hierarchical topology.

On lines **17-18** we are telling the event processor that if we haven't
managed this signal pass it onto our outer state, in this case it is the top
state which means that it is unhandled.

Finally on line **19** we return the status.  

Anyone familiar with the event processors described in the Miro Samek
tradition of dealing with hierarchical state machines will recognize the
structure of this method.  This is because the event processor used by the
miros library is a port of his work which has been written about in papers in
embedded journals and books.  I think it is important to keep the same
structure and semantics since many in our industry have become familiar with
them.  It will also ensure that if you port your work into the quantum
framework, the code will look about the same there as it does here.
