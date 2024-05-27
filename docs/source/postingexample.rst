:orphan:
  *The individual has always had to struggle to keep from being overwhelmed by the
  tribe.  If you try it, you will be frightened.  But no price is too high to pay
  for the privilege of owning yourself* -- Friedrich Nietzsche

.. _examples-simple-posting-example:

Simple Posting Example
======================

.. image:: _static/posting_example.svg
    :target: _static/posting_example.pdf
    :class: scale-to-fit

Here we see an active object.  To understand it, lets take the following steps:

1. Look at the states and see how they are related to one another in a hierarchy.
2. What external events exist and how the relate to the states.
3. What custom code has been placed within the hierarchy.

In the above example we see three different states interacting with 4 different
user defined events.  The outer state contains a middle state which contains an
inner state.

The event with signal name **A** will cause a transition from the middle state to
the inner state.  The event with signal name **B** will cause the outer event to
exit, print "flash b!" then enter back into the outer state.  Finally, the
event with the signal name **D** will cause the ``recall`` method to be triggered
in the outer state.

Now that we have a feeling for how the states relate and how they react to
events, lets look at the custom code that has been placed within the
hierarchical structure.

We see that, as previously mentioned, the outer state contains some signal
handling for the **D** named event.

The middle state has some code that is run upon entering the state.  It looks
like we are posting an event to the signal named **A**, that we want it to happen
3 times, with a period of 1 [second] and that we would like it to be deferred. The
entry condition also contains code which *augments* the chart with something.

The middle state has some exit code, where we are canceling an event.

Upon entering, the inner state, calls the defer method with an Event named **B**.
When the innner state is initialized, it prints ""flash B!" to the terminal,
then stops processing.

Generally speaking we have an idea about what is going on with the chart, now
let's look how to implement this design using the *miros* library, then start it
up in the ``outer`` state.  We will do this in three steps:

1. We will define the state methods and fill them with the custom code in the
   diagram.
2. We will create an active object
3. We will tie our active object to the state methods, by starting it within
   the ``outer`` state.
4. We will trigger an event and watch the chart react.

The **outer** state method would look like this:

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
of slide-method that can be shared between objects.  So long as we don't mark the
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

On line *7-8* we are saying, run no custom code upon exiting the state.  On
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

Now let's move on to the construction of the *middle* state:

.. code-block:: python
  :linenos:

  @spy_on
  def middle(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      multi_shot_thread = \
        ao.post_fifo(Event(signal=signals.A),
                        times=3,
                        period=1.0,
                        deferred=True)
      # We mark up the ao with this id, so that
      # this state function can be used by many different aos
      ao.augment(other=multi_shot_thread,
                    name='multi_shot_thread')
      status = state.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      ao.cancel_event(ao.multi_shot_thread)
      status = state.HANDLED

    if(e.signal == signals.INIT_SIGNAL):
      status = state.HANDLED
    elif(e.signal == signals.A):
      status = ao.trans(inner)
    else:
      status, ao.temp.fun = state.SUPER, outer
    return status

This method generally has the same structure as the outer state method.  Line
*1* instruments the method.  Line *2* has the same method signature.  Line *3*
uses the same way to set up are return variable.

On lines **4-14** we see the code which will be run  when this state is
entered.  Line **5** stores the ``multi_shot_thread`` id which is produced in
the call to ``post_fifo`` on line **6**.  The ``post_fifo`` call creates a
little parallel thread which will make events then send them back at our
statechart with no regard to what state our active object is in, it will just
place the event into the active object's first in first out buffer.

We see on lines **12-13** that we ``augment`` our ``ao`` with the attribute
called ``multi_shot_thread`` and give it the contents that was returned on line
**6**.  This was done to salt away this information so that it can be used in
the exit condition of this state method.  Now lets jump back to how the
``post_fifo`` event was called:

.. code-block:: python

        ao.post_fifo(Event(signal=signals.A),
                        times=3,
                        period=1.0,
                        deferred=True)

Here we see that it will be posting an Event with the signal name **A** to our
chart 3 times, with a period of 1 second and that it is deferred.  Here the
`deferred` input means that our parallel thread will wait the period duration
(1 second) before beginning its little job of posting the **A** event 3 times,
at a frequency of once per second.  There are lots of different ways to post
events, if you would like to investigate the other ways, look at the
:ref:`posting_events` recipes.

When this thread source has finished its job it will just stop running.
However, if the chart exits our middle state prior to our thread source
exhausting itself, it would start posting the *A* signal to the outer state.
This wouldn't be a big deal, since our state chart would just ignore the *A*
signal, but it would mean that we would be wasting cycles by making our event
processor search the chart's hierarchy with no hope of finding any useful work.

Let's talk about how this little thread can be canceled upon exiting our state.

On lines **10-11** we see this comment: "We mark up the ao with this id, so
that this state function can be used by many different aos."  Then we see some
code where the ``multi_shot_thread`` attribute is created an given the id of
the thread used to post the *A* events.  Remember, the ``ao`` variable
represents the ``self`` of your active object.  Here we are creating code that
could be written as this instead:

.. code-block:: python

    # Re-writing lines 12-13 as if they were in the active object class
    this.multi_shot_thread = multi_shot_thread

All we are doing is storing the multi_shot_thread id into the active object
that is using it, so that it can be canceled by the exit handler of the
**middle** state.  Now what is up with that comment?  When I first wrote the
example I wrote the thread id into the **middle** function's name space.  This
was a bug, since this **middle** state method could be used by many different
active objects.  When one exited it would use an id associate with a different
one.  Since this code can be re-used by many different active objects we need
to mark up those object's namespace and leave this functions' name space as is.
Never use static variables in the state method state space.

So we have created a little thread that can post events, we have stored its id
into a variable within the name space of the active object calling this state
method, so we can cancel it if we want to.  Now let's move on.

Line **14** tells the event processor that we have handled this signal and it
does not have to recurse the outer states of the chart.

Lines **16-18** describes what we want to do when this state is being exited.
On line **17** we see that we are using the thread id of our little event
posting thread to cancel that thread.  The ``cancel_event`` method needs a
specific thread id.  If you wanted to avoid all of this trouble of storing
event source ids into your active object, you could use the ``cancel_events``
method instead.  See the :ref:`recipes-cancelling-event-source-by-signal-name` recipe.

From line **20-21** we see that we don't have any special handling for the
initialization event for this state.

On lines **22-23** we see that when this state sees an **A** event it must
transition into the **inner** state.

On lines **24-25** we see how this state method handle's signals it does not
know what to do with, it sets the status to **SUPER** and sets the
``ao.temp.fun`` to the outer function.

With these bread crumbs the event processor will know what to do so that our
architecture can give us the dynamics of the Harel statechart formalism.

It is easy to forget that our statecharts are just programs that repeatedly
call methods with arguments.  They are structured programs pretending to be in
a different programming paradigm.  It is the event processor that allows this
to happen, the trade off is that we have to pepper our state methods with what
looks like strange syntax to give the event processor the ability to
traverse any of the topologies that we might want to build.

It is the event processor that calls our state methods over and over again to
build up lists of what functions should be called when and with what arguments.

This is what Miro Samek called an inversion of control.  By embedding his event
processing algorithm into their design, a developer can quickly construct any
sort of state chart topology knowing that the dynamics of the how and the when
things are called, will behave as they would expect them to.  By placing the
`control` of how things happen into the event processor, a developer can unload
their cognition, focusing on the design itself rather than how they are going
to implement it.

Let's describe the **inner** state as a state method:

.. code-block:: python
  :emphasize-lines: 4,8-10
  :linenos:

  def inner(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      ao.defer(Event(signal=signals.B))
      status = state.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = state.HANDLED
    if(e.signal == signals.INIT_SIGNAL):
      print("charging with B")
      status = state.HANDLED
    else:
      status, ao.temp.fun = state.SUPER, middle
    return status

We understand most of this code now, with the exception of line *4*.  We see
that it happens upon entering the state and that we are deferring an
event with the signal name **B**, but what does this mean?

To understand this, we have to know that an active object has a kind of
savings-account queue.  You can put things into it and nothing will happen.  The
active object won't react to them until you ask it to react to them with a call
to the ``recall`` method.  The recall method moves an item out of the
`deferred` queue and places it into the `fifo` queue.  The active object reacts
to elements in the `fifo` so when you call the ``recall`` method you are asking
the chart to react to the oldest thing that was placed into the deferred queue.

Ok, so ``defer`` stores an Event, so who recalls the event?  By examining our
state diagram, we see that the **outer** state has a ``recall`` method that it
calls upon receiving the event named **D**.  The entry of the ``inner``
entry handler also has the ``recall`` method.  That's kind of strange, but this
will make more sense once we reflect upon the dynamics of the active object.

Before we do that, let's look at lines **8-9**.  Here we see that once the state
is initialized we print, "charging with B" to the terminal.  Once again, this
is kind of strange.  On the diagram we see this expressed as the bit black dot
(the **init** signal) with an arrow labeled with the code we want to run, running
into a big black line.  This black line means stop there, you have done enough
processing.  This is the equivalent to line **10** in the above code snippet.

If you understand active objects look at the diagram and ask yourself, what
happens if I start this chart in the **middle** state, then what happens if I
wait about 4 seconds and then send an event named **D**?

.. image:: _static/posting_example.svg
    :target: _static/posting_example.pdf
    :class: scale-to-fit

*Hint: I modeled the diagram on a tazor.*

Let's see what happens using our state methods within an active object, then
reflecting upon its behavior.

.. code-block:: python
  :emphasize-lines: 7
  :linenos:

  import time
  ao = ActiveObject()
  ao.start_at(outer)
  ao.post_fifo(Event(signal=signals.C))
  time.sleep(4.0)
  ao.post_fifo(Event(signal=signals.D))
  time.sleep(0.1)

  print(ao.spy_full)

On line **1** we create an active object.  On line **2** we start it in the
**outer** state method.  The active object's event processor can now reach all
of the state methods (even though they are defined outside of its class)
because the state methods reference each other.  On line **3** we transition
into the **middle** state.  We wait for a while; **4** and then we send an event with
the **D** signal to the chart, line **6**.

Pay special attention to line **7**, because if you don't you might end up thinking
this whole example doesn't work at all.  I did this when I was constructing the
example and began a senseless investigation trying to figure out what was
wrong.

You need to wait for the active object threads to react to the items placed in
their queues.  All of the threads used within the miros library are `daemonic`
meaning that when your main program loop stops running, all of the threads it
created also stop running.  So, if you don't wait, the program will exit,
killing all of the threads before they can do anything useful.

Now let's break it down, thinking about a tazor as a metaphor.  A tazor is a
device that contains a small low voltage battery, a voltage amplifier circuit
and a capacitor.  You turn it on and it starts to whine.

This is the sound of a charge transfer from the small battery to the voltage
amplifier which separates the charge at a high voltage across the capacitor.
After this capacitor is charged up, you can zap somebody; the charge is coming
out of the capacitor in a hurry.

Line **9** shows us the action:

.. code-block:: shell
  :emphasize-lines: 1,7,13,21,29,35,46,53,58
  :linenos:

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:middle',
   'SEARCH_FOR_SUPER_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'ENTRY_SIGNAL:middle',
   'INIT_SIGNAL:middle',
   '<- Queued:(0) Deferred:(0)',
   'A:middle',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(1)',
   'A:inner',
   'A:middle',
   'EXIT_SIGNAL:inner',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(2)',
   'A:inner',
   'A:middle',
   'EXIT_SIGNAL:inner',
   'SEARCH_FOR_SUPER_SIGNAL:inner',
   'ENTRY_SIGNAL:inner',
   'POST_DEFERRED:B',
   'INIT_SIGNAL:inner',
   '<- Queued:(0) Deferred:(3)',
   'D:inner',
   'D:middle',
   'D:outer',
   'POST_FIFO:B',
   'D:outer:HOOK',
   '<- Queued:(1) Deferred:(2)',
   'B:inner',
   'B:middle',
   'B:outer',
   'EXIT_SIGNAL:inner',
   'EXIT_SIGNAL:middle',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'POST_FIFO:B',
   'RECALL:B',
   'INIT_SIGNAL:outer',
   '<- Queued:(1) Deferred:(1)',
   'B:outer',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'POST_FIFO:B',
   'RECALL:B',
   'INIT_SIGNAL:outer',
   '<- Queued:(1) Deferred:(0)',
   'B:outer',
   'EXIT_SIGNAL:outer',
   'ENTRY_SIGNAL:outer',
   'INIT_SIGNAL:outer',
   '<- Queued:(0) Deferred:(0)']

I have emphasized the beginning and ends of each run to completion event.  This
should make things easier to talk about.  So we entered our chart, waited then
sent a single event to it, and we got all of this action.

Lines **1-7** occurred as a result of us starting up the active object in the
**middle** state.  We entered the **outer** state, ran its entry code, then
entered the **middle** state and ran its entry code, then its **init** code.

The **entry** code for the **middle** state started up or ``post_fifo`` thread,
which would post an **A** signal to the chart once a second for 3 seconds.  We
are charging the capacitor.  To see how, look at lines **7-13**, we see that an
**A** event was fired, the chart transitioned into the **inner** state, the
**entry** condition for the **inner** placed the **B** event into the active
objects deferred queue.  Think of this as the battery pumping up the
capacitor's voltage with some charge.  It can only happen a little bit at a
time.

One second later we see the next pumping event on lines **13-21**, and then
one more time over lines **21-29**.  Notice that our `Deferred` queue is
getting bigger.

Now it is time to zap someone, so we would hold our tazor close to our
unsuspecting victim and trigger the **D** signal. We can see what happens in
the rest of the spy output.

Lines **29-35** shows the event processor searching for a state method that knows
what to do with the **D** signal.  On line **33** we see that the outer state
has posted a deferred signal **B** into our fifo buffer, then on line **34** we
see that this was done using a **HOOK** which means that the code that managed
it is an inherited behavior and that we aren't expected to transition because of
the **D** signal: the signal is `HANDLED`.

But the resulting **B** signal is not HANDLED, in fact it is going to create a
cascade of activity.

Lines **35-46** show the beginning of this activity.  Since the previous **D**
signal was HANDLED (see line **34**), the chart is still in its prior
**inner** state.  Lines **36-38** show the event processor searching the chart
to see if any of the state methods know how to handle the **B** signal.  It
finds the ``trans`` code in the **outer** state, builds up a strategy, then
starts to act on that strategy from lines **39-46**.  We see that it runs the
**exit** event against the **inner** method, then runs the **exit** event
against the **middle** method (which cancels our post_fifo thread if it is
still running), then it posts the **exit** event against the **outer** state,
then it posts the **entry** event against the **inner** state.  On lines
**43-44** we see that we are posting and recalling the next **B** signal from
our deferred event queue.

Since our statechart is now in the **outer** state this **B** signal just
leaves and re-enters the chart, triggering the next deferred **B** event to be
posted to the **fifo** queue of the active object.  This dynamic continues
until all of the deferred **B** items in the active object queue are expressed.
Your victim should be laying on the floor now.

So, there you have it, a very simple rendition of a tazor, our statechart could
have look like this:

.. _examples-tazor-example:

.. image:: _static/tazor.svg
    :target: _static/tazor.pdf
    :class: scale-to-fit

This diagram is almost topologically the same as the one described at the
beginning of our :ref:`examples-simple-posting-example`.  The only adjustment
was to add a new signal from re-arming our tazor (READY).

Here are the state methods for the diagram:

.. code-block:: python
  :emphasize-lines: 15-16

  @spy_on
  def tazor_operating(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      ao.recall()
      status = state.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = state.HANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = state.HANDLED
    elif(e.signal == signals.TRIGGER_PULLED):
      ao.recall()
      status = state.HANDLED
    # added this so we can rearm our tazor
    elif(e.signal == signals.READY):
      status = ao.trans(arming)
    elif(e.signal == signals.CAPACITOR_CHARGE):
      print("zapping")
      status = ao.trans(tazor_operating)
    else:
      status, ao.temp.fun = state.SUPER, ao.top
    return status

  @spy_on
  def arming(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      multi_shot_thread = \
        ao.post_fifo(Event(signal=signals.BATTERY_CHARGE),
                        times=3,
                        period=1.0,
                        deferred=True)
      # We mark up the ao with this id, so that
      # state function can be used by many different aos
      ao.augment(other=multi_shot_thread,
                    name='multi_shot_thread')
      status = state.HANDLED

    elif(e.signal == signals.EXIT_SIGNAL):
      ao.cancel_event(ao.multi_shot_thread)
      status = state.HANDLED

    if(e.signal == signals.INIT_SIGNAL):
      status = state.HANDLED
    elif(e.signal == signals.BATTERY_CHARGE):
      status = ao.trans(armed)
    else:
      status, ao.temp.fun = state.SUPER, tazor_operating
    return status


  @spy_on
  def armed(ao, e):
    status = state.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      ao.defer(Event(signal=signals.CAPACITOR_CHARGE))
      status = state.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = state.HANDLED
    if(e.signal == signals.INIT_SIGNAL):
      print("charging tazor")
      status = state.HANDLED
    else:
      status, ao.temp.fun = state.SUPER, arming
    return status

Now we will create an active object, link the above state methods into it by
starting it in the arming state:

.. code-block:: python
  :emphasize-lines: 3

  tazor = ActiveObject()
  tazor.start_at(arming)
  time.sleep(4.0)

Notice that we wait 3 seconds to let it charge up.

Now let's pull the trigger:

.. code-block:: python
  :emphasize-lines: 3

  tazor.post_fifo(Event(signal=signals.TRIGGER_PULLED))
  time.sleep(0.1)  # if you don't wait it won't look like it is working
  print(tazor.trace())

The highlighted code above shows that we used the trace to output a high level
view of what happened when we pulled the trigger:

.. code-block:: shell
  :emphasize-lines: 4,5
  :linenos:

  19:51:25.509209 [75c8c] None: top->arming
  19:51:26.511506 [75c8c] BATTERY_CHARGE: arming->armed
  19:51:27.512153 [75c8c] BATTERY_CHARGE: armed->armed
  19:51:28.512604 [75c8c] BATTERY_CHARGE: armed->armed
  19:51:29.512080 [75c8c] CAPACITOR_CHARGE: armed->tazor_operating
  19:51:29.513081 [75c8c] CAPACITOR_CHARGE: tazor_operating->tazor_operating
  19:51:29.514085 [75c8c] CAPACITOR_CHARGE: tazor_operating->tazor_operating

Notice that our **TRIGGER_PULL** signal did not show up in our trace.  We would
expect it to occur between lines *4* and *5*.  This is because the trace only
shows signals that cause state transition.  The **TRIGGER_PULL** signal was
handled by a HOOK and therefore didn't directly cause a transition.  Instead,
it cause the ``recall`` method to post a **CAPACITOR_CHARGE** signal, which
in turn causes two more state transitions.

To see our full spy log, we would use the following code:

.. code-block:: python

  pp(tazor.spy_full())

Which outputs the full story:

.. code-block:: shell
  :emphasize-lines: 1,7,13,21,29,35,46,53,58
  :linenos:

  ['START',
  'SEARCH_FOR_SUPER_SIGNAL:arming',
  'SEARCH_FOR_SUPER_SIGNAL:tazor_operating',
  'ENTRY_SIGNAL:tazor_operating',
  'ENTRY_SIGNAL:arming',
  'INIT_SIGNAL:arming',
  '<- Queued:(0) Deferred:(0)',
  'BATTERY_CHARGE:arming',
  'SEARCH_FOR_SUPER_SIGNAL:armed',
  'ENTRY_SIGNAL:armed',
  'POST_DEFERRED:CAPACITOR_CHARGE',
  'INIT_SIGNAL:armed',
  '<- Queued:(0) Deferred:(1)',
  'BATTERY_CHARGE:armed',
  'BATTERY_CHARGE:arming',
  'EXIT_SIGNAL:armed',
  'SEARCH_FOR_SUPER_SIGNAL:armed',
  'ENTRY_SIGNAL:armed',
  'POST_DEFERRED:CAPACITOR_CHARGE',
  'INIT_SIGNAL:armed',
  '<- Queued:(0) Deferred:(2)',
  'BATTERY_CHARGE:armed',
  'BATTERY_CHARGE:arming',
  'EXIT_SIGNAL:armed',
  'SEARCH_FOR_SUPER_SIGNAL:armed',
  'ENTRY_SIGNAL:armed',
  'POST_DEFERRED:CAPACITOR_CHARGE',
  'INIT_SIGNAL:armed',
  '<- Queued:(0) Deferred:(3)',
  'TRIGGER_PULLED:armed',
  'TRIGGER_PULLED:arming',
  'TRIGGER_PULLED:tazor_operating',
  'POST_FIFO:CAPACITOR_CHARGE',
  'TRIGGER_PULLED:tazor_operating:HOOK',
  '<- Queued:(1) Deferred:(2)',
  'CAPACITOR_CHARGE:armed',
  'CAPACITOR_CHARGE:arming',
  'CAPACITOR_CHARGE:tazor_operating',
  'EXIT_SIGNAL:armed',
  'EXIT_SIGNAL:arming',
  'EXIT_SIGNAL:tazor_operating',
  'ENTRY_SIGNAL:tazor_operating',
  'POST_FIFO:CAPACITOR_CHARGE',
  'RECALL:CAPACITOR_CHARGE',
  'INIT_SIGNAL:tazor_operating',
  '<- Queued:(1) Deferred:(1)',
  'CAPACITOR_CHARGE:tazor_operating',
  'EXIT_SIGNAL:tazor_operating',
  'ENTRY_SIGNAL:tazor_operating',
  'POST_FIFO:CAPACITOR_CHARGE',
  'RECALL:CAPACITOR_CHARGE',
  'INIT_SIGNAL:tazor_operating',
  '<- Queued:(1) Deferred:(0)',
  'CAPACITOR_CHARGE:tazor_operating',
  'EXIT_SIGNAL:tazor_operating',
  'ENTRY_SIGNAL:tazor_operating',
  'INIT_SIGNAL:tazor_operating',
  '<- Queued:(0) Deferred:(0)']

:ref:`back to examples <examples>`
