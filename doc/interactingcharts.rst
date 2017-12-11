A prophet is not someone with special visions, just someone blind to most of
what others see -- Nassim Nicholas Taleb

The individual has always had to struggle to keep from being overwhelmed by the
tribe.  If you try it, you will be frightened.  But no price is too high to pay
for the privilege of owning yourself -- Friedrich Nietzsche

.. _interactingcharts-interacting-statecharts:

Interacting Statecharts
=======================

.. _interactingcharts-some-context-about-concurrency:

Concurrency: the Good Parts
--------------------------
Your designs can be significantly simplified if you break them up into a
collection of statecharts (active-objects/factories), each running in their own
thread.

If your statechart is interested in an event provided by the system, it can
subscribe to it.  If your statechart would like to provide information to
another statechart, it can publish an event.  By separating your design into
parts like this it makes it much easier to test and document your system.  More
importantly, it makes it easier to maintain.  The majority of a software
project's lifetime cost is spent in maintenance.

In 2008 `Douglas Crockford`_ (the man who invented JSON) released a very important
book called, `JavaScript The Good Parts`_."  In his book he talked about how the
most successful programming language on our planet (written in 10 days) could
still be used to create powerful and expressive systems.  Douglas postulated
that despite the haste under which JavaScript was presented to humanity
(because of idiotic leadership at Netscape), it actually contained some really,
really good pieces from which serious programs could be written.  He learned
about these good parts by writing a `Lint`_ tool in which he packed in
the JavaScript's community feedback about their best practices, then let this
program teach him how to program.

After years of learning from the community through his `Lint`_ tool he wrote his
great book.  His powerful engineering insight is this, just because it was
invented and available to you,  doesn't mean you have to use it.  Use the parts
that have been demonstrated to work well; proven through their interaction with
the community.  The parts that have caused problems should not be used, in fact
they should be discarded immediately.  Good design is the process of discovery
and cultural editing and curation.

Miro Samek did the same thing with `concurrent systems`.  Unfortunately not a
lot of people were paying attention.  On page 444 of his book titled "Practical
UML STATECHARTS in C/C++" he writes, "you should heed to the following two
rules, without exception:

1. Active objects should interact only through an asynchronous event exchange
   and should `not` share memory or other resources.

2. Active objects should `not` block or busy-wait for events in the middle of
   RTC [run-to-completion] processing."

Then he says more on the same page, "I strongly recommend that you take these
rules seriously and follow them `religiously`.  In exchange [his framework] can
guarantee that your application [will be] free from the traditional perils of
preemptive multitasking, such as race conditions, deadlocks, priority
inversions, starvations, and nondeterminism. In particular, you will never need
to use mutexes, semaphores, monitors, or other such troublesome mechanisms at
the application level".

Many of the concurrency ideas come from the 1960's when it was very unlikely
that a software developer would write code which would run on two or more
processors at the same time.  Multitasking was invented to break problems apart
into threads (also called tasks) of operation to decouple designs.  Each thread
was intended to provide the illusion, that any code running within it, was
running in its own processor.

Things became extremely complicated when a designer needed to share resources
between two different threads, or when one thread had to operate with greater
access to the processor than another thread.  To manage this complexity,
preemptive multitasking was invented.  Preemption in this context means that
one thread of a higher priority can interrupt another causing it to store its
state, then take over the processor's time until it was done, then reconstruct
the state of the lower priority thread so it could run without knowing that it
hadn't been running the whole time.  Because this was such a daunting task,
completely dependent upon the hardware, it was managed within it's own software
(which had to be invented) called a real time operating system.

Real time operating systems would also have to manage how shared variables were
shared between tasks.  Shared variables that weren't protected by the operating
system were like super-globals that acted as little time bombs.  A corruption
might not happen until all of your threads happen to find the right beat; where
they all wrote to the same variable at the same time. So an unprotected
variable might not be corrupted until 10 months after you have turned on your
system, when your part is floating on it's way to Saturn.  Good luck getting to
the bottom of that problem.

So when you read, "race conditions, deadlocks, priority inversions, starvations
and nondeterminism" in his quote, just see them as billion dollar problems
pulled from the zoology of pain, on which careers have been waisted.  [I'm
feeling the pain right now, watching my neovim editor lock-up while trying to
copy text.]

So a lot of the ideas related to concurrency haven't worked, yet they haven't
been dropped either.  They continue to be cargo-cult-ed into our present from
the 1960's by well meaning instructors who are just teaching what they have
been taught.  Worse yet, the ideas are couched within pedantic wording which
make them seem holy to a beginner.   Their names and the bad writing describing
them defend them from criticism by obscuring them from view.

These ideas are also like little tar babies, they get tar on anything they
touch.  I can't guarantee that this library can follow the rules described by
Miro Samek because I haven't re-written the operating system you are using or
the Python threading library.  There are many libraries that you will use which
call out for resources and then block, like they ``http`` library; it is tarred
with these bad ideas.  If the Python language, the operating system that it
runs on or any of it's libraries call something which shares memory or blocks
in the middle of some run-to-completion processing then your design has broken
the Samek rules.  So we can't get dogmatic about things here.  Just follow the
rules within your own design.

If you are an embedded developer, pick a processor that Miro Samek has ported
his framework onto and then use his technology, you won't be sorry.

Jack Ganssle is another embedded developer who has been in the industry from
the beginning.  He says that embedded software, or firmware was invented to
make jet fighters infinitely expensive:

   In his book "Augustine's Laws," Norman Augustine, former Lockheed Martin
   CEO, tells a revealing story about a problem encountered by the defense
   community. A high performance fighter aircraft is a delicate balance of
   conflicting needs: fuel range vs. performance. Speed vs. weight. It seems
   that by the late 70s fighters were at about as heavy as they'd ever be.
   Contractors, always pursuing larger profits, looked in vain for something
   they could add that would cost a lot, but which weighed nothing.

   The answer: firmware. Infinite cost, zero mass. Avionics now accounts for
   more than half of a fighter's cost. That's a chunk of change when you
   consider the latest American fighter, the F-22, costs a cool $257m a pop.
   Augustine practically chortles with glee when he relates this story.

As you know the United States is the richest country in the world with a
corrupt military-industrial-complex.  The Pentagon spends ungodly amounts of
money purchasing weapon systems and yet it's staff is made up of government
workers being paid government salaries.  Their only hope at becoming rich is to
make a good impression on the defense contractors which they buy weapons from,
using other people's money, so that after they 'retire' from the government
service they can be re-hired into the defense business at executive rates of
compensation.

So it is safe to say there is very little incentive for the American defense
community to find a better way to write the most expensive parts of their
system.  Compare this to the Israeli military; they live in a country with an
area a-little-bit-bigger than New Jersey, surrounded by a billion enemies.

David Harel was paid by the Israeli military to help them build better jet
fighter software.  The Israeli military isn't fucking around like the
American's are.  "It is interesting that the Israeli's achieved a 80-1 crushing
victory over the Arabs in the 1973, 6-day war."  When asked about it the
commander of the "Israeli Air Force (IAF), General Mordecai Hod, famously
remarked that the outcome would have been the same if both sides had swapped
planes." As the great engineer Pierre M. Sprey points out [1]_ , "He was
exactly correct, simply because the IAF had the most rigorous system in the
world for filtering out all of the most gifted pilots.  In every war, it's the
few super pilots that win the air battle.  A tiny handful of such pilots have
dominated every air-to-air battleground since World War I; roughly 10 percent
of all pilots (the "hawks") score 60 percent to 80 percent of the dogfight
kills; the other 90 percent of pilots ('doves') are fodder for the hawks on the
opposite side.  Technical performance between opposing fighter planes pale in
comparison."

The pilot is a key piece of the design.  If you aren't already, become a hawk;
pick the strategies that work and avoid strategies that bring you into harm's
way.  Be aware of the cultural distortions.  We can learn from the people who
came before us and use their curated working subsets of our technologies and
avoid the parts that have been shown to cause trouble.

So when Miro Samek recommends his new approach to concurrency: Use the Harel
formalism and follow his commandments within your own design, we need to
remember where these innovations came from and who paid for them.

.. _interactingcharts-a-simple-example:

A Simple Example
----------------
The Miros library makes concurrency trivial.  You build up an active object,
provide it with a starting state (with it's connected map).  Then you post
events to it.

If it needs to communicate with other active objects it publishes an event with
a payload containing its information.  If an active object is interested in
information published by another active object, it would subscribe to that
event.  That's it.

Everything is managed in the background with threads and queues.  There are no
shared variables.  It is up to you not to busy weight within your state methods
or callback methods.

Here is a very simple example:

.. image:: _static/concurrency1.svg
    :align: center

Let's begin by importing the required libraries:

.. code-block:: python
  :emphasize-lines: 1

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

We will build up these charts using a
:ref:`factory<recipes-creating-a-state-method-from-a-factory>` (which is a type
of active object).  Now let's work on the ``b_chart``, I like to start with a
picture:

.. code-block:: python
  :emphasize-lines: 5-17

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  # 
  # 
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

Since we are using a factory, we write up some callback functions which will be
placed on the diagram as we build it out:

.. code-block:: python
  :emphasize-lines: 19-20, 22-23, 25-26, 28-31
  :linenos:

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  #
  #
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

  def trans_to_fb(chart, e):
    return chart.trans(fb)

  def trans_to_fb1(chart, e):
    return chart.trans(fb1)

  def trans_to_fb11(chart, e):
    return chart.trans(fb11)

  def publish_BB(chart, e):
    chart.publish(Event(signal=signals.BB,
      payload="information from b_chart riding within the BB signal"))
    return return_status.HANDLED

The highlighted code describes the callback signal methods that will be linked
into ``b_chart``.  Pay special attention to lines 29-31.  It is here that we
will :ref:`publish<recipes-publishing-event-to-other-active-objects>` a ``BB``
signal to the active fabric which connects all of the active objects in the
system.  If another active object has subscribed to this ``BB`` signal it will
receive this event with this payload.

Now let's use the factory and build the ``b_chart``.

.. code-block:: python
  :emphasize-lines: 33-36, 38-41, 43-44, 46-48

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  # 
  # 
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

  def trans_to_fb(chart, e):
    return chart.trans(fb)

  def trans_to_fb1(chart, e):
    return chart.trans(fb1)

  def trans_to_fb11(chart, e):
    return chart.trans(fb11)

  def publish_BB(chart, e):
    chart.publish(Event(signal=signals.BB,
      payload="information from b_chart riding within the BB signal"))
    return return_status.HANDLED

  b_chart = Factory('b_chart')
  fb = b_chart.create(state='fb'). \
          catch(signal=signals.a, handler=trans_to_fb1). \
          to_method()

  fb1 = b_chart.create(state='fb1'). \
          catch(signal=signals.b, handler=trans_to_fb11). \
          catch(signal=signals.INIT_SIGNAL, handler=publish_BB). \
          to_method()

  fb11 = b_chart.create(state='fb11'). \
          to_method()

  b_chart.nest(fb, parent=None). \
          nest(fb1, parent=fb). \
          nest(fb11, parent=fb1)

Now that we have built the ``b_chart`` let's build out the ``c_chart``:

.. code-block:: python
  :emphasize-lines: 51-101
  :linenos:

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  #
  #
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

  def trans_to_fb(chart, e):
    return chart.trans(fb)

  def trans_to_fb1(chart, e):
    return chart.trans(fb1)

  def trans_to_fb11(chart, e):
    return chart.trans(fb11)

  def publish_BB(chart, e):
    chart.publish(Event(
      signal=signals.BB,
        payload="information from b_chart riding within the BB signal"))
    return return_status.HANDLED

  b_chart = Factory('b_chart')
  fb = b_chart.create(state='fb'). \
          catch(signal=signals.a, handler=trans_to_fb1). \
          to_method()

  fb1 = b_chart.create(state='fb1'). \
          catch(signal=signals.b, handler=trans_to_fb11). \
          catch(signal=signals.INIT_SIGNAL, handler=publish_BB). \
          to_method()

  fb11 = b_chart.create(state='fb11'). \
          to_method()

  b_chart.nest(fb, parent=None). \
          nest(fb1, parent=fb). \
          nest(fb11, parent=fb1)

  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def bb_handler(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BB):
      chart.scribble(e.payload)
      status = chart.trans(fc)
    return status

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # 
  # 
  #
  #        +------------------ fc ---------------+
  #        |   +----- fc1----+   +-----fc2-----+ |
  #        | * |             |   |             | +----+
  #        | | |             +-a->             | |    |
  #        | +->             <-a-+             | |    BB
  #        |   |             |   |             | |    |
  #        |   |             |   |             | <----+
  #        |   +-------------+   +-------------+ |
  #        +-------------------------------------+
  #

  c_chart = Factory('c_chart')
  fc = c_chart.create(state='fc'). \
        catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
        catch(signal=signals.BB, handler=bb_handler). \
        to_method()

  fc1 = c_chart.create(state='fc1'). \
        catch(signal=signals.a, handler=trans_to_fc2). \
        to_method()

  fc2 = c_chart.create(state='fc2'). \
        catch(signal=signals.a, handler=trans_to_fc1). \
        to_method()

  c_chart.nest(fc,  parent=None). \
          nest(fc1, parent=fc). \
          nest(fc2, parent=fc)

  # subscribe to BB signals sent to the active fabric
  c_chart.subscribe(Event(signal=signals.BB))

Pay special attention to the last line.  This is where the ``c_chart`` is
:ref:`subscribing<recipes-subscribing-to-an-event-posted-by-another-active-object>`
to the ``BB`` signal.  I forgot to add this in the example and it took me a
long time to figure out why the statechart was not working. :)

The actual ``BB`` event handler for this signal is described on lines 57-62.
We see there that we follow the typical rules for structuring a state method.
It did not have to be written this way, it could have been written more
concisely as:

.. code-block:: python

  def bb_handler(chart, e):
    chart.scribble(e.payload)
    return chart.trans(fc)

How you write it is up to you, just ensure that you return the correct
:ref:`return_status<recipes-what-a-state-does-and-how-to-structure-it>` type.
In both examples we use the :ref:`scribble method<recipes-scribble-on-the-spy>`
so that we can write the ``BB`` event's payload directly onto the
:ref:`spy<recipes-using-the-spy>`

Now that the charts are written, let's turn them on and see what happens:

.. code-block:: python
  :emphasize-lines: 101-104, 106-110

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  #
  #
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

  def trans_to_fb(chart, e):
    return chart.trans(fb)

  def trans_to_fb1(chart, e):
    return chart.trans(fb1)

  def trans_to_fb11(chart, e):
    return chart.trans(fb11)

  def publish_BB(chart, e):
    chart.publish(Event(signal=signals.BB,
      payload="information from b_chart riding within the BB signal"))
    return return_status.HANDLED

  b_chart = Factory('b_chart')
  fb = b_chart.create(state='fb'). \
          catch(signal=signals.a, handler=trans_to_fb1). \
          to_method()

  fb1 = b_chart.create(state='fb1'). \
          catch(signal=signals.b, handler=trans_to_fb11). \
          catch(signal=signals.INIT_SIGNAL, handler=publish_BB). \
          to_method()

  fb11 = b_chart.create(state='fb11'). \
          to_method()

  b_chart.nest(fb, parent=None). \
          nest(fb1, parent=fb). \
          nest(fb11, parent=fb1)

  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def bb_handler(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BB):
      chart.scribble(e.payload)
      status = chart.trans(fc)
    return status

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  #
  #
  #
  #        +------------------ fc ---------------+
  #        |   +----- fc1----+   +-----fc2-----+ |
  #        | * |             |   |             | +----+
  #        | | |             +-a->             | |    |
  #        | +->             <-a-+             | |    BB
  #        |   |             |   |             | |    |
  #        |   |             |   |             | <----+
  #        |   +-------------+   +-------------+ |
  #        +-------------------------------------+
  #

  c_chart = Factory('c_chart')
  fc = c_chart.create(state='fc'). \
        catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
        catch(signal=signals.BB, handler=bb_handler). \
        to_method()

  fc1 = c_chart.create(state='fc1'). \
        catch(signal=signals.a, handler=trans_to_fc2). \
        to_method()

  fc2 = c_chart.create(state='fc2'). \
        catch(signal=signals.a, handler=trans_to_fc1). \
        to_method()

  c_chart.nest(fc,  parent=None). \
          nest(fc1, parent=fc). \
          nest(fc2, parent=fc)

  # subscribe to BB signals sent to the active fabric
  c_chart.subscribe(Event(signal=signals.BB))

  # Start up the charts and post an event to see # how they interact
  c_chart.start_at(fc)
  b_chart.start_at(fb)
  b_chart.post_fifo(Event(signal=signals.a))

  time.sleep(0.01)
  print(c_chart.trace())
  pp(c_chart.spy())
  print(b_chart.trace())
  pp(b_chart.spy())

Here start the ``c_chart`` at it's ``fc`` state and start the ``b_chart`` on
it's ``fb`` state, then we post an event with an ``a`` signal to ``chart_b``.
Let's look at the picture again so we can see what should happen.

.. image:: _static/concurrency1.svg
    :align: center

From visual inspection of the ``b_chart`` we would expect an ``a`` signal to
cause a transition into the ``fb1`` state, then run it's ``init`` signal.  This
would cause the ``chart.publish(Event(signal=signals.BB, payload="information
from b_chart riding within the BB signals"))`` code to run.  Then it would
transition into state ``fb11``.  

Looking at the other ``c_chart`` and knowing it started in ``fc``, we could
expect the ``BB`` signal would cause an exit from ``fc1``, and exit from ``fc``
and then an entry into ``fc``.  As for when it would run the code on the ``BB``
signal is not obvious.  Upon entering the ``fc`` state it would run it's
``init`` signal and enter ``fc1``.  That's a lot of behavioral complexity packed
into a little bit of code; all mapped and easy to understand.

Let's look at the output of our instrumentation:

.. code-block:: python
  :emphasize-lines: 15

  [2017-12-07 12:15:53.521431] [c_chart] e->start_at() top->fc1
  [2017-12-07 12:15:53.503913] [c_chart] e->BB() fc1->fc1

  ['SUBSCRIBING TO:(BB, TYPE:fifo)',
   'START',
   'SEARCH_FOR_SUPER_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'INIT_SIGNAL:fc',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)',
   'BB:fc1',
   'BB:fc',
   'information from b_chart riding within the BB signal',
   'EXIT_SIGNAL:fc1',
   'EXIT_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'INIT_SIGNAL:fc',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)']

  [2017-12-07 12:15:53.521431] [b_chart] e->start_at() top->fb
  [2017-12-07 12:15:53.503913] [b_chart] e->a() fb->fb1

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:fb',
   'ENTRY_SIGNAL:fb',
   'INIT_SIGNAL:fb',
   '<- Queued:(0) Deferred:(0)',
   'a:fb',
   'SEARCH_FOR_SUPER_SIGNAL:fb1',
   'ENTRY_SIGNAL:fb1',
   'INIT_SIGNAL:fb1',
   'PUBLISH:(BB, PRIORITY:1000)',
   '<- Queued:(0) Deferred:(0)']

We see the ``c_chart`` trace followed by the it's spy.  The highlighted line
shows us where the call on ``BB`` was made prior to the chart responding to the
signal.  This is explained in greate detail in :ref:`hacking to
learn<scribbleexample-hacking-to-learn-the-deeper-dynamics>`.

Other than that, the chart's are interacting exactly as we expect them to.  If
I was working within a team and had to explain this behavior to someone not
directly involved in the software, I would use the traces and the
:ref:`sequence<recipes-drawing-a-sequence-diagram>` tool and draw my collegue a
sequence diagram:

.. code-block:: python
  :emphasize-lines: 1

  # hot key in vim draws the pictures below
  [2017-12-07 12:15:53.521431] [c_chart] e->start_at() top->fc1
  [2017-12-07 12:15:53.503913] [c_chart] e->BB() fc1->fc1
  [2017-12-07 12:15:53.521431] [b_chart] e->start_at() top->fb
  [2017-12-07 12:15:53.503913] [b_chart] e->a() fb->fb1

  [ Chart: c_chart ] (?)
       top          fc1     
        +start_at()->|
        |    (?)     |
        |            +            
        |             \ (?)       
        |             BB()        
        |             /           
        |            <            
  
  [ Chart: b_chart ] (?)
       top          fb           fb1     
        +start_at()->|            |
        |    (?)     |            |
        |            +----a()---->|
        |            |    (?)     |
  
Then I would over-write the question marks with numbers and reference those
numbers in my documentation.

:ref:`back to examples <examples>`

.. _Javascript The good Parts: http://shop.oreilly.com/product/9780596517748.do
.. _Douglas Crockford: https://www.crockford.com/
.. _Lint: http://www.jslint.com/
.. _Evaluating Weapons Sorting the Good from the Bad: http://pogoarchives.org/labyrinth/09-sprey-w-covers.pdf
.. [1] Pierre M. Sprey `Evaluating Weapons Sorting the Good from the Bad`_
.. [#f1] They are named ``b`` and ``c`` because these are the topological names given to them on page 178 of "Practical UML STATECHARTS in C/C++"

