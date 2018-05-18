
Concurrency: the Good Parts
--------------------------
Your designs can be significantly simplified if you break them up into a
:ref:`collection of statecharts<interactingcharts-a-simple-example>`
(active-objects/factories), each running in their own thread.

If your statechart is interested in an event provided by the system, it can
:term:`subscribe<Subscribe>` to it.  If your statechart would like to provide
information to another statechart, it can :term:`publish<Publish>` an event.
By separating your design into parts like this it makes it much easier to test
and document your system.  More importantly, it makes it easier to maintain.
The majority of a software project's lifetime cost is spent in maintenance.

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

.. _on-firmware:

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

