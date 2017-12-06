
.. _interactingcharts-interacting-statecharts:

Interacting Statecharts
=======================

.. _interactingcharts-some-context-about-concurrency:

Some Context about Concurrency
------------------------------
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
(because of idiotic leadership at Netscape), it actually contained some really
really good pieces from which serious programs could be written.  He learned
about these good parts by writing a `Lint`_ tool in which he packed in
the JavaScript's community feedback about their best practices, then let this
program teach him how to program.

After years of learning from the community through his `Lint`_ tool he wrote his
great book.  His powerful engineering insight is this, just because it was
invented and available to you,  doesn't mean you have to use it.  Use the parts
that have been demonstrated to work well; proven through their interaction with
the world.  The parts that have caused problems should not be used, in fact
they should be discarded immediately.  Good design is the process of discovery.

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

Do you see it?  All that confusing shit that you were taught related to
concurrency has just been cargo-culting.  The embedded community has been
experiencing the pain from these bad ideas for years, these ideas that were
invented back in the 1960's (before anyone knew what they were doing).
Your instructors, who just read the textbooks and got good grades were not
practitioners, they were not engineering, they didn't realize that a lot of
these ideas were just bad.  They should be removed; Miro Samek provides a new
approach.  Use the Harel formalism and follow Miro Samek's "Concurrency the
good parts".

Interestingly, David Harel was asked to help the Israeli military build better
jet fighter software.  The Israeli military isn't fucking around like the
American's are.  It is interesting that the Israeli's achieved a 80-1 crushing
victory over the Arabs in the 1973, 6-day war.  When asked about it the
commander of the "Israeli Air Force (IAF), General Mordecai Hod, famously
remarked that the outcome would have been the same if both sides had swapped
planes." As the great engineer Pierre M. Sprey points out [1]_ , "He was exactly
correct, simply because the IAF had the most rigorous system in the world for
filtering out all of the most gifted pilots.  In every war, it's the few super
pilots that win the air battle.  A tiny handful of such pilots have dominated
every air-to-air battleground since World War I; roughly 10 percent of all
pilots (the "hawks") score 60 percent to 80 percent of the dogfight kills; the
other 90 percent of pilots ('doves') are fodder for the hawks on the opposite
side. Technical performance between opposing fighter planes pale in
comparison."

The pilot is the key piece of the design.  You are the pilot; if you aren't
already become a hawk and pick the strategies that work.  A pilot in the air
force doesn't have the luxury of building his own aircraft; you do.  We can
learn from the people who came before us and use the curated working subsets of
the technologies that we can choose from.  Back to the example:


:ref:`back to examples <examples>`

.. _Javascript The good Parts: http://shop.oreilly.com/product/9780596517748.do
.. _Douglas Crockford: https://www.crockford.com/
.. _Lint: http://www.jslint.com/
.. _Evaluating Weapons Sorting the Good from the Bad: http://pogoarchives.org/labyrinth/09-sprey-w-covers.pdf
.. [1] Pierre M. Sprey `Evaluating Weapons Sorting the Good from the Bad`_
