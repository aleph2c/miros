.. _zero_to_one-zero-to-one:

  *You should focus relentlessly on something that you're good at doing, but
  before that you must think hard about whether it will be valuable in the
  future.*

  -- Peter Thiel, Zero to One: Notes on Startups, or How to build the Future

.. role:: dead_spec
  :class: dead_spec

.. role:: new_spec
  :class: new_spec

Tutorial: Zero To One
=====================

This is not a 5-minute blog read.  But, if you want to learn how statecharts
work, this is your one-stop shop, it will take you from 0 to 1.  If you already
understand statecharts, and would like to just see how to use the syntax of this
library, reference the :ref:`quick start <quick-start>`.

If you are like me, learning something entirely new can be very exhausting.  You
need to learn new words, new ideas and you have to juggle them in your head
until you finally see how they interrelate.  This can be hard work.

But stories about people moving around on a small stage are much easier to
remember.  If it's a good story, it doesn't feel like work to remember its
details.

So lets use a :ref:`story <zero_to_one_story>` to explain the statechart
concepts, pictures and mechanics.  At the end of the story I'll describe how its
stage, characters and objects map back onto the technical things you need to
know.  Don't worry if you are a little bit confused after reading the story; if
a few things stick, great, push on.

Once we understand some basic statechart concepts, we will work through an
:ref:`example <zero-to-one-a-simple-example>`.  The example will be broken up
into a set of iterations and each iteration will be broken into 4 parts:

* `spec`: what are we trying to build and how do we know when we are done?
* `design`: a picture, as a formal description of the thing we are trying to
  build 
* `code`: the code required to manifest the design 
* `proof`: proof that our code is actually matching our design 
* `questions`: a list of questions and answers

The questions section will provide you with a dialogue driven style of
reading the documentation.  Each iteration is heavily linked so that you can
quickly bounce around between its various parts.

.. note::

  I will also pepper the story with boxes, like this one, translating a story
  part to the technical aspects of statecharts.  If the contents of these boxes
  don't make sense, don't worry.  Things will become clearer once you work
  through the examples.

.. _zero_to_one_story:

Story
^^^^^ 

.. raw:: html

   <div class="story">
   
   <p><span class="story-intro">Our story will be placed in a little universe.</span>  This little universe will
   consist of a heaven, an earth and an underworld.   The earth in the story
   isn't round like ours.  It's a very small flat platform, floating above the
   underworld.  On top of the earth are a set of pubs, arranged on different
   terraces.  Each terrace has one pub.
   </p>

   <p>
   To get to a higher pub, you would first have to walk through a lower pub.  The
   lower pubs are for a more general audience, while the higher pubs, though having
   less space have a more specialized aesthetic. 
   </p>
   
   <p>
   On every terrace, there will be two bouncers, a greeter and zero or more
   bartenders.  There will only be one set of stairs that can be used to enter or
   exit a pub, and this is where that pub's bouncers will sit.
   </p>

   <p>
   One bouncer will be facing in the direction of people entering the terrace and
   the other will be facing in the direction of people wanting to leave it.  The
   greeter will talk to anyone who has decided to stay on her terrace.  If there is
   a bartender on the terrace, he will serve drinks and sometimes he will have
   secrets.
   </p>
   </div>

.. image:: _static/md_terraced_pubs.svg
    :target: _static/md_terraced_pubs.pdf
    :align: center

.. admonition:: translation

  Each pub is a state in a statemachine.  You would program these states as
  functions that take two arguments, a reference to an ActiveObject and an event.

  These state functions will contain an if-elif structure which will have
  multiple clauses.  The greeter is the "init" clause, and the enter and exit
  bouncers are the "entry" and "exit" clauses.

  The "init", "enter", and "exit" clauses can be activated when the state
  function is given an event with an init, entry or exit name.

  Likewise, the bartender is a clause where the application developer sets the
  event name.

.. raw:: html

   <div class="story">

   <p>
   Now let's add some supernatural beings: three "gods" and a "spirit".
   </p>

   <p>
   The heaven will have one goddess, Eve, "the goddess of law and order" and the
   underworld will be ruled by Theo, "<a href="https://en.wikipedia.org/wiki/Solipsism">the solipsist.</a>" The earth
   will have a lazy god named Spike, "the source" who happens to be the only guy
   who can drink in the whole universe.  Spike will have a companion spirit,
   named Tara "the explorer."
   </p>

   <p>
   We know now about the entire cast of the story.  There are bouncers, greeters,
   bartenders, three gods and one spirit.
   </p>

   </div>

.. image:: _static/md_terraced_gods.svg
    :target: _static/md_terraced_gods.pdf
    :align: center

.. admonition:: translation

  Eve represents the "event processor", or the algorithm that sends the state
  functions different events.

  Spike, represents the "Source" state while the event processor is searching
  the statechart.  Think of Spike as the current state of the statemachine.
  
  Tara represents the "Target" state, which is used by the event processor to
  explore the statemachine while it is trying to figure out what to do.

  Theo is the "thread" in which all of the code is run.  The event processor and
  all of it's calls to the various state functions will be driven by this
  thread.  

  An application developer will not write code to change the internal behaviour
  of the event processor, the source and target states or the thread.  This is
  why these characters are supernatural in the story; it's a mnemonic.

.. raw:: html

   <div class="story">

   <p>
   Let's put our little universe into a small multiverse. Each universe will
   have it's own heaven and underworld, gods and explorer spirit, but its
   terraced architecture of pubs, and people (bartenders, greeters) can be
   shared across all connected universes.
   </p>

   <p>
   If this doesn't make any sense, don't worry about it.  Let's move on.
   </p>

   </div>

.. image:: _static/md_multiverse.svg
    :target: _static/md_multiverse.pdf
    :align: center

.. admonition:: translation

  Anytime a statechart references a callback (a pub), that callback will change
  the internal variable state of the ActiveObject that is passed in as its first
  argument -- the state callback functions themselves, do not have their own
  memory.

  Since the callback functions don't keep any information, they can be called by
  many different ActiveObjects (in that ActiveObjects's thread) and behave as
  expected; there are no side effects.  In this way, many different ActiveObjects
  can use the same set of state callback functions.

.. raw:: html

   <div class="story">

   <p>
   Eve, the goddess of heaven has a birds-eye view of our little world.  She rules
   over the people: the bouncers, greeters and bartenders and, Tara, "the explorer"
   spirit.  She took on her duty as "the goddess of law and order" with such gusto,
   that sometime in the world's history, she banned alcohol consumption for
   everyone on earth, except Spike, who she can't control.
   </p>

   </div>

.. image:: _static/md_eve.svg
    :target: _static/md_eve.pdf
    :align: center

.. admonition:: translation

  The if-elif clauses, represented by the people in the story, exist within each
  of the state functions.  These if-elif clauses only become active when the
  event processor (Eve) calls its function with an internal event, represented
  by one of the people in the story.

  Tara, the "target state" is used by the event processor when it is searching a
  statemachine to see which state handles an external event.  Since the event
  processor calls the function and change's its target state while it is
  searching through a statemachine, we say that Eve rules over the people and
  Tara the "explorer spirit".

.. raw:: html

   <div class="story">

   <p>
   Theo, "the solipsist" is the god of the underworld.  He is only called the
   "solipsist" by people outside of his universe, like you and me, because his
   universe only works and exists if he is thinking about it.  Nobody in his world
   is aware that he has this power.
   </p>

   <p>
   One of Theo's duties is to join the little universe with other universes.  Theo
   watches a portal, which is connected to a loading dock which receives
   messages from different worlds, including ours.  He is extraordinarily attentive
   and enthusiastic.  He can motivate anyone he talks to or even looks upon, in
   fact, this is his supernatural ability.
   </p>

   </div>

.. image:: _static/md_theo.svg
    :target: _static/md_theo.pdf
    :align: center

.. admonition:: translation

  Theo represents a "thread" pending on a queue.  The ActiveObject's ``post_fifo``
  and ``post_lifo`` methods allow an application developer to put events into
  this queue.  When the thread sees that a queue has an item, it will wake up,
  and drive the event processor, which in turn, will call the functions
  making up the statemachine.


.. raw:: html

   <div class="story">

   <p>
   When Theo receives a message from another universe, it appears as a round hollow
   orb which sometimes contains a scroll.  He calls these orbs "events", and if they
   have a scroll within them, he calls that scroll a "payload".
   </p>
   </div>

.. image:: _static/md_events.svg
    :target: _static/md_events.pdf
    :align: center

.. admonition:: translation
  
  An event has a name, called a signal, which can be a user defined name or it
  can be a predefined name (ENTRY_SIGNAL, EXIT_SIGNAL, INIT_SIGNAL, etc...).  An
  event with a user defined signal name is called an external event.  An event
  with a predefined name is called an internal event.

  The whole point of naming an event with a signal is so that a state function
  can use an if-elif clause to "catch" the event when it is given to that
  function.  When such an event is caught, your code is run.

.. raw:: html

   <div class="story">

   <p>
   When an "event" comes through the portal, Theo will pick it up, marvel at it,
   then in a reverent gesture, pass it to Eve.  They both become excited, maybe
   even a little nervous, because they know their universe is going to change; it
   will react to the event.
   </p>

   <p>
   Theo encourages Eve to "follow the laws." Then he will watch as she gives her
   minions their marching orders.  Only after all of the activity stops, will he
   focus his attention back on the portal.
   </p>

   <p>
   Feeling oddly refreshed and encouraged by Theo, Eve looks around the map until
   she sees Spike from her high vantage point.  Spike being the god of the earth,
   is easy to see and Eve knows that her underling-spirit Tara, "the explorer",  is
   always near him.
   </p>

   <p>
   Eve flies down to Tara and gives her the event.  She says, "I want you to go to
   the terrace where there is a bartender who knows what to do with this event.
   Then I want you to go to wherever he tells you to take it.  Good luck Tara, I
   believe in you."
   </p>

   <p>
   Tara enjoys Spike's company, but she also loves adventure.
   </p>

   <p>
   She looks down at the event to study it and notices that it has something written
   on it, a word, a phrase, it could be different every time, but it's a clue and
   Tara loves a puzzle.  She looks around the pub on her terrace and studies each
   of the bartender's name tags.  If she sees that a name tag matches the name on
   the event, she will approach that bartender and talk to him.
   </p>

   </div>

.. image:: _static/md_events_bartenders.svg
    :target: _static/md_events_bartenders.pdf
    :align: center

.. raw:: html

   <div class="story">

   <p>
   If there is no bartender to talk to on her terrace, she will go to its exit
   staircase and <strong>descends</strong> to the next terrace (Tara only ascends when given
   instructions to do so).  Being a spirit, she is hard to see and the bouncers
   and greeters leave her alone when she is by herself.
   </p>

   </div>

.. admonition:: translation

  The terraces are just callback functions containing if-elif-else clauses (pub
  == terrace == state == callback).
  
  The else clause of each callback function provides information about what
  other callback function should be called if it doesn't know what to do with a
  given event.  This other function, can be thought of as a lower terrace.

  The bartenders are named arrows on the HSM diagram.

  The bartender also represents an if-elif clause that matches the name of the
  event given to that function.  

.. raw:: html

   <div class="story">
   <p>
   She will continue to climb down the terraces until she comes to the edge of the
   universe.  If she can't find a bartender who can answer her question, she will
   take the event and throw it off the edge of the earth, into oblivion, then climb
   back up to rejoin Spike.  In such rare cases their universe doesn't react to the
   event.
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_oblivion.svg
    :target: _static/md_bartenders_on_the_hsm_oblivion.pdf
    :align: center

.. admonition:: translation

  Here we are starting to explore a statechart's dynamics.  If your statemachine
  doesn't handle an event in any of it's callback functions, the event will be
  ignored.

.. raw:: html

   <div class="story">
   <p>
   But if Tara does find a bartender who's name tag matches the name on the event,
   she will show it to him.  He will take it and study it, sometimes he might even
   take out it's scroll.  Then he will lean across the bar and whisper the answer
   into Tara's ear.
   </p>
   <p>
   Sometimes the bartender says, "give me the event I'll handle it, don't worry
   about it anymore."  When this happens, Tara passes over the event, then rejoins
   Spike, who rejoices because he doesn't have to do anything.  For some reason
   Spike calls this a "hook".
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_hook.svg
    :target: _static/md_bartenders_on_the_hsm_hook.pdf
    :align: center

.. admonition:: translation

  Tara, the "target state" is used by the event processor to find which state
  callback function knows how to handle a given event.  In the above picture we
  see that T started in "C pub", then the event processor recursed outward to "A
  pub" at which point it found an if-elif clause in the "A pub" callback that
  "handled" the event with the signal name of "Merve".  If the application
  developer placed code between the "Merve" clause and it's return statement,
  this code would be run while T is searching.

  When a state callback function returns "handled" the event processor pulls T
  back to where S is, then it stops searching.

  A state callback function can use the T state of the event processor to
  perform this type of event handling.  For more details about this programming
  technique, read about the :ref:`ultimate hook pattern.<patterns-ultimate-hook>`

.. raw:: html

   <div class="story">
   <p>
   Most of the time, however, the bartender will tell Tara where she has to take
   the event.  If she has to continue her journey, she will wait for Spike so she can
   tell him about it.
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_reaction_1.svg
    :target: _static/md_bartenders_on_the_hsm_reaction_1.pdf
    :align: center

.. raw:: html

   <div class="story">
   <p>
   Spike knows when Tara is waiting for him.  Though he is lazy, and drunk most of
   the time, he always has something interesting to say, and this is what Tara
   loves about him.  Having nothing else to do, he makes his way to the terrace
   where Tara has gotten her next clue.  He knows that she will want to talk to him
   about it.  As he approaches the exit, the exit bouncer puts up a hand, then
   looks at a clip board to see if Spike is on the guest list, which he always is,
   and then let's Spike pass to the next terrace.  You really can't stop the
   god of the earth.  For every terrace that Spike needs to leave so that he can
   rejoin with Tara, this futile ritual is repeated.
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_reaction_2.svg
    :target: _static/md_bartenders_on_the_hsm_reaction_2.pdf
    :align: center

.. admonition:: translation

  The target state is used by the event processor to recurse outward
  from C1 to find a state that knows what to do with the Event, who's signal
  name is Mary.  

  The A state has an if-elif clause which handles Mary, and within the clause
  there is a transition to the B2 state.  In this scenario, the A state is
  called the Least Common Ancestor, LCA of S and T.  S needs to exit all states,
  from it's current state, to the LCA.  However, it should not exit the LCA.

  As an application developer, you don't really care about the LCA acronym.  You
  just need to understand the dynamics of how exits work; your exit handlers
  will be called as your source state transitions out of the inner states to
  re-join the target state.

.. raw:: html

   <div class="story">
   <p>
   When Spike finally finds Tara he asks her what she learned.  Bubbling with
   excitement, she tells him about where the bartender said to take the event, to
   which he always says, "great I'll meet you there, but first I want to have a
   drink here."  Tara takes the event and makes her way to the location that the
   bartender told her about.
   </p>

   <p>
   Spike finishes his drink, then again starts to make his way toward Tara.  Before
   he can climb up to a new Terrace, he is stopped by the entry bouncer, who looks
   at his clip board to see if Spike is on the guest list, which he always is, then
   lets Spike proceed.  You really can't stop the god of the earth anyway.
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_reaction_3.svg
    :target: _static/md_bartenders_on_the_hsm_reaction_3.pdf
    :align: center

.. raw:: html

   <div class="story">

   <p>
   When Spike finally arrives on the Terrace where Tara is, a greeter approaches
   them.  She looks at Spike and feels slightly uncomfortable, because sometimes
   she needs to tell them that they can't stay on this terrace.  Instead of talking
   to Spike directly, gods are intimidating, she whisper's something into Tara's
   ear.  Both the greeter and Tara work for Eve after all.  Tara is always happy to
   hear that there is more to do, because she likes to explore the pubs on the
   different terraces.
   </p>

   <p>
   If the greeter tells Tara that she needs to climb higher, Tara will relay the
   message to Spike who will answer, "great, I'll meet you there, but first I want
   to have a drink".
   </p>

   <p>
   Tara climbs to the terrace where the greeter told her to go.  Spike finishes his
   drink and makes his way through the entry bouncers and finally arrives at the
   same terrace where Tara is waiting.  At which point there might be another
   greeter with another uncomfortable message.
   </p>
   </div>

.. image:: _static/md_bartenders_on_the_hsm_reaction_4.svg
    :target: _static/md_bartenders_on_the_hsm_reaction_4.pdf
    :align: center

.. raw:: html

   <div class="story">

   <p>
   If no greeter approaches them, Tara looks down at the event and watches with
   satisfaction, as it throbs with light, then slowly fades from existence.  To
   this, Spike smiles and looks towards heaven, as he raises a toast to Eve.  
   </p>

   <p>
   When Eve, the goddess of heaven, see's this her shoulder's relax and the tension
   releases from her back: The laws were followed.
   </p>

   <p>
   Theo, "the solipsist", god of the underworld, has been watching the whole scene,
   and its "run to completion".  Knowing there is nothing left to do in the
   universe, he turns his gaze back to the portal.  He waits patiently for an event
   to pass through the little universe's loading dock.  All is well.
   </p>
   </div>

.. admonition:: translation

  The run to completion, RTC, concept is very important to understand.  Your
  statechart will only react to one event at a time.  The thread will only
  process the next event when the event processor has run out of things to do
  with your old event.

  For this reason, you should not put `blocking code
  <https://en.wikipedia.org/wiki/Blocking_(computing)>`_ into your statecharts.
  If you do, they will stop reacting to events and become unresponsive.

.. raw:: html

   <div class="story">
   <p>
   But is it?  Sometimes when Theo, "the solipsist", god of the underworld, closes
   his eyes and daydreams; his attention briefly drifts back to his world.  This is
   enough to wake everyone up from their non-existence.
   </p>
   </div>


.. admonition:: translation
   
   Solipsism is the name of the philosophy where a person thinks they create the
   world when they open their eyes, and they destroy the world when they close
   their eyes.  It's delusional.  But Theo is actually a "solipsist" (though he
   doesn't know that he is) because he is a Python thread.  No code can run
   unless he grants CPU access to it.

.. raw:: html

   <div class="story">
   <p>
   When the people wake up, they become listless. The bouncers who have had nothing
   to do since the prohibition was announced by Eve, are particularly frustrated
   with the meaninglessness of their jobs.  They only have one customer now.  Even
   if Spike wasn't always permitted to pass them, there is no way they could stop
   the god of earth. Why have a universe full of pubs if only one guy can drink?
   It seems so pointless.  It's lame.
   </p>

   <p>
   Somehow, they find out about you and me, fellow humans called developers.
   </p>

   <p>
   They learn that we, despite being human, are very powerful.  That we can build
   the pub terrace system to which their gods are subservient; that we can send the
   event orbs and give the greeters and the bouncers their secret directions (arrows on
   the diagram).  That we can even build many different interconnected universes
   and have them communicate with each other.
   <p>

   <p>
   They challenge us to make something useful out of their existence, even if
   they can't understand it from where they are, they need something to
   <strong>have meaning</strong>.  So, they create an organized campaign: "hack
   the humans".  This is how it works: All of the humans in the little universe,
   open themselves to run code directly from our universe, while they are
   talking to either Tara or Spike.
   </p>
   </div>

.. image:: _static/md_hack_the_humans.svg
    :target: _static/md_hack_the_humans.pdf
    :align: center

.. raw:: html

   <div class="story">
   <p>
   To help us, they create a <a href="https://www.dictionary.com/browse/rosetta-stone">Rosetta stone</a>, translating the concepts of their
   universe into something legible for you and me:
   </p>
   </div>

.. _zero_to_one_rosetta:

+--------------------------------------+------------------------------------------+
| **Story Concept**                    | **Programming Concept**                  |
+======================================+==========================================+
| The terraced pubs, humans, Gods and  | A statechart                             |
| spirit                               |                                          |
|                                      |                                          |
+--------------------------------------+------------------------------------------+
| All the terraced pubs                | A set of all possible states that your   |
| (And all the humans)                 | design will have (pubs) and the code     |
|                                      | that makes each state run the way you    |
|                                      | want it to (the humans).  A              |
|                                      | state is an abstraction of a real world  |
|                                      | state of being, or how you would like to |
|                                      | group your program's functionality and   |
|                                      | behaviors.                               |
|                                      | A program                                |
|                                      | made up of a bunch of interacting states |
|                                      | is called a state machine.  Our programs |
|                                      | will be made up of layered states in a   |
|                                      | hierarchy, so our machine is called a    |
|                                      | hierachical state machine (HSM).         |
+--------------------------------------+------------------------------------------+
| A single pub and its humans          | A callback function with some code in it.|
|                                      | The callback function represents one of  |
|                                      | the states in our design.                |
|                                      | A callback function references its       |
|                                      | lower callback function (it knows about  |
|                                      | its lower pub, or its parent state).     |
+--------------------------------------+------------------------------------------+
| Gods and Spirit                      | An ActiveObject which uses the callback  |
|                                      | functions.                               |
|                                      | It provides a thread to run              |
|                                      | the state machine in, the rules on how   |
|                                      | it should run and it marks the state     |
|                                      | machine with a source state and a target |
|                                      | state.                                   |
|                                      | An ActiveObject can mark states but it   |
|                                      | does not have states, it attaches to a   |
|                                      | set of state callbacks with its          |
|                                      | ``start_at`` call which takes a state    |
|                                      | callback as an argument.                 |
+--------------------------------------+------------------------------------------+
| Eve, "the goddess of law and order", | The ActiveObject event processor, the    |
| goddess of heaven                    | algorithm that ensures we follow HSM     |
|                                      | transition rules                         |
+--------------------------------------+------------------------------------------+
| Spike, "the source",                 | There are many states in an HSM, we can  |
| god of the earth                     | not be in them all at the same time,     |
|                                      | **S**, the source state; is a variable   |
|                                      | holding the active state of our          |
|                                      | state machine before it reacts to an     |
|                                      | event. If the state machine is not       |
|                                      | reacting to an event **S** is the        |
|                                      | current state of the state machine.      |
+--------------------------------------+------------------------------------------+
| Theo, "the solipsist",               | The thread that the statechart runs in.  |
| god of the underworld                |                                          |
+--------------------------------------+------------------------------------------+
| Tara, "the explorer", spirit         | The target state, **T** (search aspect)  |
|                                      | of the event processor.  It is a         |
|                                      | variable that can hold different         |
|                                      | states while the state machine is        |
|                                      | figuring out how to transition from      |
|                                      | one state to another as it reacts to     |
|                                      | events.                                  |
+--------------------------------------+------------------------------------------+
| bartender                            | Arrow or hook on the HSM diagram,        |
|                                      | represented as a conditional statement   |
|                                      | for a user defined event.                |
|                                      | Any hook code associated with this       |
|                                      | conditional statement is run when        |
|                                      | touched by **T**.                        |
+--------------------------------------+------------------------------------------+
| greeter                              | ``INIT_SIGNAL`` event given to a         |
|                                      | callback by the event processor when     |
|                                      | **S** stabilizes in a new state.         |
+--------------------------------------+------------------------------------------+
| exit bouncer                         | ``EXIT_SIGNAL`` event given to a         |
|                                      | callback by the event processor when     |
|                                      | **S** exits a state.                     |
+--------------------------------------+------------------------------------------+
| exit bouncer                         | ``ENTRY_SIGNAL`` event given to          |
|                                      | a callback by the event processor when   |
|                                      | **S** enters a state.                    |
+--------------------------------------+------------------------------------------+
| run to completion, RTC:              | The thread will only handle one event    |
| Theo keeps his attention on the      | a time. This is called RTC.  An RTC      |
| universe's activities until the      | process is over when the event processor |
| action stops                         | can no longer cause state transitions    |
|                                      | and the statechart settles on a new      |
|                                      | state.                                   |
+--------------------------------------+------------------------------------------+
| Top level view of terraced bar       | UML statechart drawings                  |
| universe                             |                                          | 
+--------------------------------------+------------------------------------------+

.. raw:: html

   <div class="story">
   <p>
   The human's find a drawing technology in our world that can be used to
   describe theirs, it is called the UML statechart diagram.
   
   But before we go any further, let's examine some of the information that is
   missing from a typical UML statechart drawing:
   </p>
   </div>

.. image:: _static/md_translation_with_notes.svg
    :target: _static/md_translation_with_notes.pdf
    :align: center

.. raw:: html

   <div class="story">

   <p>
   The picture describes some class information, and a behavioural specification
   for the states as a bird's eye view of the terraced bar system, but
   there is no information about the thread, <strong>S</strong>,
   <strong>T</strong>, the deques, the events or any of the dynamics of the
   statechart.  
   </p>
   
   <p>
   So the UML statechart diagram acts as a stage in a play, with the full script
   being broken into pieces and given to each human actor in the play in the
   location where it can be read.  We can see all of this information in the
   diagram: the stage, the human actors, where they stand on the stage and what
   they will read when it is their turn to talk.
   </p>

   <p>
   The diagram describes everything that is possible, but it doesn't tell how a
   specific story plays out; this requires our own world to send an event (an
   orb) into theirs, and it requires work by their gods and their explorer
   spirit.
   </p>

   <p id="zero-to-one-spy-carpet">
   To help us see and hear a specific story from the many possible stories, they
   invent a <a
   href="https://www.aetv.com/real-crime/a-surveillance-expert-on-planting-bugs-in-carpets-cats-and-cockroaches-to-nab-suspects">spy-carpet</a>.
   To use this carpet, you place the <strong>@spy_on</strong> decorator above
   any callback function representing a pub, or state in the HSM.  This is
   called instrumentation.
   </p>

   <p id="zero-to-one-spy-carpet">
   If you lay this carpet down, it will record and report all activity that
   transpired between <strong>T</strong>, <strong>S</strong> and any human
   within that pub.  This information can be read during or after their universe
   has reacted to the events send from our world.
   </p>

   <p>
   Now that we understand a bit more about statecharts, let's use one of their
   universes to make a toaster oven.
   </p>
   </div>

.. _zero-to-one-a-simple-example:

A Simple Example: Toaster Oven
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To make this toaster oven statechart example seem like a real software project,
I will break it's design process up into 6 steps, or iterations.

Each iteration will have a specification, a design diagram and the code needed
to match the design diagram.  Then I will prove that the code works and I'll
provide links to a bunch of questions and answers about the code.

Each iteration is heavily linked so that you can quickly bounce around in its
documentation.

.. _iter1:

Iteration 1: setup
------------------
In this iteration I will talk about setting up our development environment.  We
will build a very simple statechart and confirm that it is working.

.. _iter1_spec:

Iteration 1 specification
"""""""""""""""""""""""""

* Ensure our Python version is 3.5 or greater
* :ref:`Install miros <installation>`
* Import the required statechart components
* Build a ToasterOven class which inherits from an ActiveObject
* Make a single state, and start the statechart in that state
* Add instrumentation to our state
* Use the instrumentation to confirm that the statechart is working.

.. include:: i_navigation_1.rst

To confirm that Python is version 3.5 or greater, in your terminal type:

.. code-block:: bash

  python3 --version

To install miros, use pip (included in Python 3.5 or greater).  For this example
I will install it in a virtual environment.

.. code-block:: bash

  python3 -m venv venv
  . ./venv/bin/activate
  pip install miros

.. note::
  Miros is not dependent on any other packages.

.. _iter1_design:

Iteration 1 design
""""""""""""""""""

Here is the design we will use to confirm that miros is working on your computer:

.. image:: _static/ToasterOven_0.svg
    :target: _static/ToasterOven_0.pdf
    :align: center

.. include:: i_navigation_1.rst

.. _iter1_code: 

Iteration 1 code
""""""""""""""""

.. code-block:: python
  :linenos:

  # file named toaster_oven_1.py
  import time

  from miros import Event
  from miros import spy_on
  from miros import signals
  from miros import ActiveObject
  from miros import return_status

  class ToasterOven(ActiveObject):
    def __init__(self, name):
      super().__init__(name)

  @spy_on
  def some_state_to_prove_this_works(oven, e):
    status = return_status.UNHANDLED
    if e.signal == signals.ENTRY_SIGNAL:
      print("hello world")
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(some_state_to_prove_this_works)

    time.sleep(0.1)

.. include:: i_navigation_1.rst

.. _iter1_proof:

Iteration 1 proof
"""""""""""""""""

Now to prove that the code works, in your terminal, run the program:

.. code-block:: bash

  python toaster_oven_1.py
  hello world
  [2018-09-11 09:35:10.011526] [oven] \
    e->start_at() top->some_state_to_prove_this_works

.. include:: i_navigation_1.rst

.. _iter1_questions:

Iteration 1 questions
"""""""""""""""""""""

Questions and Answers about the code and the results:

* :ref:`Why is miros only supported in Python 3.5 or greater?<why_is_miros_onl>`                                                 
* :ref:`Can you explain what is going on with the imports on lines 1-7?<can_you_explain_>`
* :ref:`Why bother making a ToasterOven that inherits from the ActiveObect, why not just use the ActiveObject?<why_bother_making>`
* :ref:`You keep calling the state functions callbacks, what do you mean by this?<you_keep_calling>`
* :ref:`What do you mean by a function signature?<what_do_you_mean>`
* :ref:`How am I going to remember to structure my callback functions with all of these rules?<how_am_i_going_t>`
* :ref:`This seems strange to me, I haven't seen Python that looks like this before.  Why do it this way?<this_seems_stran>`
* :ref:`Where is the thread, event processor and queues in the diagram?<where_is_the_thr>`
* :ref:`Can you explain what is happening in the entry clause?<can_you_explain_what_is_happening_in_the_entry_clau>`
* :ref:`Can you explain where the init and exit clauses are?<can_you_explain_where_the_init_and_exit_clauses_a>`
* :ref:`Can you explain what is going on with the else clause?<can_you_explain_what_is_going_on_with_the_else_clau>`
* :ref:`How does the live_trace call work?<how_does_the_live_trace_call_wo>`
* :ref:`What happens when the start_at method is called?<what_happens_when_the_start_at_method_is_call>`
* :ref:`Why are you placing a delay at the end of the code sample?<why_are_you_placing_a_delay_at_the_end_of_the_code_samp>`
* :ref:`How did your prove that your code worked?<how_did_your_prove_that_your_code_work>`
* :ref:`Why are you using threads and not asyncio?<why_are_you_using_threads>`
* :ref:`When is it going to be done?<when_is_it_going_to_be_do>`

.. include:: i_navigation_1.rst

.. _why_is_miros_onl:

**Why is miros only supported in Python 3.5 or greater?**

I originally wrote and tested miros in Python 3.5.  I didn't know it at the
time, but I used the Python 3.5 feature of avoiding circular imports.  When I
tried to run miros in 3.4 I got a lot of ImportErrors.  So there you go, it was
an accidental limitation.

.. include:: i_navigation_1.rst

.. _can_you_explain_:

**Can you explain what is going on with the imports on lines 1-7?**

I'll answer this question by putting a lot of comments into the code:

.. code-block:: python

  # ActiveObject contains the thread, event processor, and queues
  # it also contains the miros API
  from miros import ActiveObject

  # return_status contains information on how a state callback 
  # should respond when called by the event processor
  from miros import return_status

  # Event is the miros Event class, use this to make a new event object
  from miros import Event

  # signals, contains all of the signal names in the system
  # it also automatically constructs new signals names if it
  # is used with a name that hasn't been used before:
  #   example:
  #     e = Event(signal=signals.NEW_NAME)
  from miros import signals

  # spy_on is a decorator which when applied to state callback
  # function will let use used the spy and trace instrumentation
  # on that callback
  from miros import spy_on

  # time is imported so that the program can be delayed
  import time

.. include:: i_navigation_1.rst

.. _why_bother_making:

**Why bother making a ToasterOven that inherits from the ActiveObect, why not just use the ActiveObject?**

The ActiveObject doesn't know anything about being a toaster oven.  It knows
about queues and threads and it knows how to drive a state machine using a set
of callback functions.  If you wanted to give an instantiated ActiveObject, a
method or an attribute, you could use the :ref:`augment
<recipes-markup-your-event-processor>`_ method; but a more traditional way of
giving it toaster-like features, is to sub-class it, then add these features to
that subclass.

.. include:: i_navigation_1.rst

.. _you_keep_calling:

**You keep calling the state functions callbacks, what do you mean by this?**

A callback function is just a function that is given to another function, so
that it can be called later:

.. code-block:: python

  import time

  # this will be our callback
  def print_msg(message):
    print(message)

  def call_something_later(callback):
    time.sleep(1)
      callback("hello world")

  # wait one second then print "hello world"
  call_something_later(print_msg)

The states in our diagram are constructed as callback functions with a given
signature.  The event processor will call these functions when it needs to.

.. include:: i_navigation_1.rst

.. _what_do_you_mean:

**What do you mean by a function signature?**

A function signature describes the arguments that a function can take and the
type of items it can return.

Our state callback functions will always have the same signature:

.. code-block:: python

  # The event processor will call this function when it needs to 
  # because the  function isn't called right away,
  # it is called a callback function

  # 1st part of the function signature, it's arguments.
  # Our state callback functions will always take two arguments:
  # 1) a reference to a state_chart_object 
  # 2) an event
  def some_state_function(state_chart_object, e):
    status = return_status.UNHANDLED
    # do useful work, then

    # set the status variable to an attribute of return_status
    # to tell the event processor how your function responded
    # to its call

    # 2nd part of the function signature: it will always return
    # an attribute of the return_status object
    return status

For a real state function, it's signature would be expressed like this:

.. code-block:: python
  :emphasize-lines: 1, 2, 5, 8, 9
  :linenos:

  def some_state_to_prove_this_works(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("hello world")
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

To make our state callback function have the right signature, we ensure that it
takes two arguments, a statechart object and an event, line 1.  Then, depending
on how the function reacts, we either return:

  * ``return_status.UNHANDLED`` if we want an event to bubble outward in the
    chart.  Typically this is the default value of the item you will return from
    a statechart callback.  See line 2.
  * ``return_status.HANDLED`` when we want the event processor to stop searching
    for an event.  See line 3.
  * ``return_status.SUPER`` when we don't know what to do to the event, so we
    return information that will tell the event processor to try our super state. See line 8.

There are more things that can be returned, we will address them as the example continues.

.. include:: i_navigation_1.rst

.. _this_seems_stran:

**This seems strange to me, I haven't seen Python that looks like this before.  Why do it this way?**

The miros library is intended to serve two different audiences:

* Embedded programmers who need to quickly prototype their designs, then port
  the work to c/C++ using the QP framework.  
* Python developers who want to use statecharts.

This way of writing statecharts -- by using callbacks with if-elif structures,
working with an ActiveObject -- will make code that is extremely easy to port
back to the QP framework.

If you would like to program in a more "Pythonic" way, you can inherit from the
miros Factory class instead of the ActiveObject.  Under the hood, the Factory
class is just making the kinds of callback functions we are talking about here.

It is easier to explain this library using the traditional techniques of engaging
with the Miros Samek event processing algorithm than by just jumping into the
Factory class. (I only program the statecharts using the Factory class)

.. include:: i_navigation_1.rst

.. _how_am_i_going_t:

**How am I going to remember to structure my callback functions with all of these rules?**

Once you do it a few times you will remember it.  To begin with just reference
the :ref:`boiler plate example <recipes-boiler-plate-state-method-code>`, and change it
to match your design.

Also, it is relatively easy to add this boiler plate code to whatever snippet
technology you are using with your editor. I use Ultisnips in Vim.

.. include:: i_navigation_1.rst

.. _where_is_the_thr:

**Where is the thread, event processor and queues in the diagram?**

The thread is missing from the UML:

.. image:: _static/ToasterOven_0_1.svg
    :target: _static/ToastOven_0_1.pdf
    :align: center

Unlike the thread the, event processor is actually shown on the picture:

.. image:: _static/ToasterOven_0_2.svg
    :target: _static/ToastOven_0_2.pdf
    :align: center

I leave the event processor on my pictures so I can show the starting state of
the active object.

The queues are missing from the UML as well, but they are contained within the
ActiveObject class:

.. image:: _static/ToasterOven_0_3.svg
    :target: _static/ToastOven_0_3.pdf
    :align: center

.. include:: i_navigation_1.rst

.. _can_you_explain_what_the_spy_on_decorator_is_doing:

**Can you explain what the spy_on decorator is doing?**

The spy_on decorator wraps a state's callback function with some code that lets
you log the output of the event processor as it follows its rules, making **T**
and **S** move around the HSM.

.. code-block:: python
  :emphasize-lines: 1,3

  from miros import spy_on

  @spy_on
  def some_state_to_prove_this_works(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("hello world")
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

By using the decorator you can debug, test and document the behavior of your
statechart.

If you don't include the decorator, the statechart will work a little bit
faster, but it will be harder to debug.

.. note::

  The spy_on decorator needs to be placed on every callback that you want to
  monitor.  I usually place the spy_on decorator on all of the state callbacks.

.. include:: i_navigation_1.rst

.. _can_you_explain_what_is_happening_in_the_entry_clau:

**Can you explain what is happening in the entry clause?**

When the event processor sends an event with the signal name ``ENTRY_SIGNAL``
the if clause of the state callback will print "hello world" to the terminal
then it will set the status variable to ``return_status.HANDLED``.  This status value
is returned to the event processor, letting it know to stop processing the
``ENTRY_SIGNAL`` event.

.. code-block:: python
  :emphasize-lines: 3-5

  def some_state_to_prove_this_works(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("hello world")
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

The entry signal is sent to the callback as a result of the HSM being started in
the ``some_state_to_prove_this_works`` state.

.. include:: i_navigation_1.rst

.. _can_you_explain_where_the_init_and_exit_clauses_a:

**Can you explain where the init and exit clauses are?**

We don't need the init and exit clauses in the design, so we don't include them
in the if-elif structure of the state's callback function.  The event processor
will still call the function with the event named ``INIT_SIGNAL``, after it has
entered the ``some_state_to_prove_this_works`` state, but it will be ignored.

By only including the events that we need we keep our callback function small
and easy to read.

.. include:: i_navigation_1.rst

.. _can_you_explain_what_is_going_on_with_the_else_clau:

**Can you explain what is going on with the else clause?**

A callback function can land in its `else` clause for one of two reasons:

1. The event processor is explicitly asking it for its super state callback function.
2. The event processor has sent it an event it has received in the hopes that it
   knows what to do with it, but the current state doesn't know what to do with
   it.

.. note::
  
   In the second case, :ref:`T <zero_to_one_rosetta>` has not found anything in the
   current state that can handle its event and it needs to know how to descent outward in the HSM.

Thankfully, your callback function doesn't have to care which of these two
reasons were behind why it has landed in its ``else`` clause.  It just has set
the ``tem.fun`` attribute of its first argument to the its parent callback
function, and return ``return_status.SUPER``.

.. code-block:: python
  :emphasize-lines: 6-8

  def some_state_to_prove_this_works(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("hello world")
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top  # no outer state
      status = return_status.SUPER
    return status

But in our example, the ``some_state_to_prove_this_works`` state doesn't have an outer
state, so we set the ``oven.temp.fun`` attribute to ``oven.top``, to let the event
processor know it has reached the outermost state of the HSM.

.. image:: _static/ToasterOven_0_4.svg
    :target: _static/ToastOven_0_4.pdf
    :align: center

The returned value of the state callback function is set to
``return_status.SUPER`` so that your function can notify the event processor
that it set the ``oven.temp.fun`` to its superstate's function.

.. note::

  How the else clause is called doesn't really matter to you as an application
  developer.  You just have to follow some rules:

  * set the ``oven.temp.fun`` to the callback function representing the
    superstate
  * if there is no superstate, set it to the ``top`` attribute of the first
    argument given to the callback function
  * ensure that the callback function returns, return_state.SUPER if the else
    clause is reached.

.. _how_does_the_live_trace_call_wo:

.. include:: i_navigation_1.rst

**How does the live_trace call work?**

The :ref:`live_trace <recipes-tracing-live>` attribute needs to be set before the
statechart's thread is started:

.. code-block:: python

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(some_state_to_prove_this_works)

    time.sleep(0.1)

It output's the trace log as your statechart is reacting to events.  It can only
work if the ``@spy_on`` decorator is placed above the state functions in your HSM.

There are two different types of instrumentation output provided by miros.  The
:ref:`trace <recipes-using-the-trace>` and the :ref:`spy
<recipes-using-the-spy>`.  The trace provides information only if a state
transition has occurred.  It reports if :ref:`S <zero_to_one_rosetta>`
has moved.  For each line in a trace log,  describes:

  * The time stamp of when the event was reacted to
  * The name of the statechart
  * The event that caused the transition
  * The starting state of :ref:`S <zero_to_one_rosetta>` 
  * The ending state of :ref:`S <zero_to_one_rosetta>`

Our minimal example doesn't do much, it starts from outside of the HSM and then
transitions into the ``some_state_to_prove_this_works``.

.. code-block:: python

  [2018-09-11 09:35:10] [oven] e->start_at() top->some_state_to_prove_this_works

In this example we see: when I ran the test.  That the statechart is called oven,
that the starting state of :ref:`S <zero_to_one_rosetta>` in this oven instance was ``top`` and the
ending state of :ref:`S <zero_to_one_rosetta>` was ``some_state_to_prove_this_works``.

There is no ``start_at`` event in miros.  But to keep the trace output useful, I
write a fake ``start_at`` event as the cause of the initial transition into the
HSM.  On the diagram, this will be where the event processor attachment point
touches the HSM.

.. note:: 

  I might remove some information from the timestamp in this documentation to make
  the text fit on the screen.

.. include:: i_navigation_1.rst

.. _what_happens_when_the_start_at_method_is_call:

**What happens when the start_at method is called?**

The ``start_at`` method links the oven object to the HSM, then it starts the
statechart.  It does this by creating a new thread, then running the oven's
event processor in that thread.

.. code-block:: python

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(some_state_to_prove_this_works)

    time.sleep(0.1)

Before a statechart is started, :ref:`T <zero_to_one_rosetta>` and :ref:`S <zero_to_one_rosetta>`
exist outside of the outermost
state.  The ``start_at`` call, places :ref:`T <zero_to_one_rosetta>` into the
``some_state_to_prove_this_works``.  :ref:`S <zero_to_one_rosetta>`
marches towards :ref:`T <zero_to_one_rosetta>`, triggering as
many needed entry events as required, then the init event in the state that
:ref:`T <zero_to_one_rosetta>` is in.

In our example there isn't much to talk about.  The entry clause of the
``some_state_function`` is called, printing "hello world".

.. include:: i_navigation_1.rst

.. _why_are_you_placing_a_delay_at_the_end_of_the_code_samp:

**Why are you placing a delay at the end of the code sample?**

.. code-block:: python
  :emphasize-lines: 6
  :linenos:

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(some_state_to_prove_this_works)

    time.sleep(0.1)

The delay is placed at the bottom of the file to ensure that the statechart's
thread can react, and produce some live trace feedback, before the main thread
exits the program.

.. note::

  The miros package uses daemonic threads, which means that they will be shut
  down with the main thread stops running.  

.. include:: i_navigation_1.rst

.. _how_did_your_prove_that_your_code_work:

**How did your prove that your code worked?**

Looking at the design, we see that the starting state should be
``some_state_to_prove_this_works`` and that when it enters this state it should
print "hello world" to the terminal.

.. image:: _static/ToasterOven_0.svg
    :target: _static/ToasterOven_0.pdf
    :align: center

The output is:

.. code-block:: bash

  hello world
  [2018-09-11 09:35:10.011526] [oven] \
    e->start_at() top->some_state_to_prove_this_works

Which is exactly what were were expecting.

.. include:: i_navigation_1.rst

.. _why_are_you_using_threads:

**Why are you using threads and not asyncio?**

Asyncio is cool, but it doesn't work with everything yet.  It may be the future
of Python, but to use it all of your libraries will have to be asyncio
compliant.  I wrote miros so that it can use as much existing Python as possible.

If you want to check out another implementation of the Miro Samek event
processing algorithm in Python, written with asyncio, check out `Dean Hall's pq.
<https://github.com/dwhall/pq>`_

In the future I might port the miros threads to David Beazley's `thredo <https://github.com/dabeaz/thredo>`_ technology.

.. _when_is_it_going_to_be_do:

**When is it going to be done?**

I'm not answering this question

.. include:: i_navigation_1.rst

.. _iter2:

Iteration 2: basic oven
-----------------------
Now that we know miros will run on our system, lets use it to build a very basic
toaster oven with a working HSM.

.. _iter2_spec:

Iteration 2 specification
"""""""""""""""""""""""""

* :new_spec:`The toaster oven will have a door, it will always be closed (for now)`
* :new_spec:`The toaster oven will have an oven light, which can be turned on and off`
* :new_spec:`The toaster oven will have a heater, which can be turned on and off`
* :new_spec:`It will have two different heating modes, baking which can bake a potato
  and toasting which can toast some bread`
* :new_spec:`The toaster oven should start in the off state`
* :new_spec:`The toaster can only heat when the door is closed`
* :new_spec:`The toaster's light should be off when the door is closed`

.. include:: i_navigation_2.rst

.. _iter2_design:

Iteration 2 design
"""""""""""""""""""

.. image:: _static/ToasterOven_2.svg
    :target: _static/ToasterOven_2.pdf
    :align: center

.. include:: i_navigation_2.rst

.. _iter2_code:

Iteration 2 code
""""""""""""""""

.. code-block:: python

  # file named toaster_oven_2.py
  from miros import ActiveObject
  from miros import return_status
  from miros import Event
  from miros import signals
  from miros import spy_on
  import time

  class ToasterOven(ActiveObject):
    def __init__(self, name):
      super().__init__(name)

    def light_on(self):
      print("light_on")

    def light_off(self):
      print("light_off")

    def heater_on(self):
      print("heater_on")

    def heater_off(self):
      print("heater_off")

  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("baking")
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("toasting")
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("off")
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(off)
    # toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # turn the oven off
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)

.. include:: i_navigation_2.rst

.. _iter2_proof:

Iteration 2 proof
"""""""""""""""""

.. code-block:: bash

	python3 toaster_oven_2.py
	off
	[2018-09-12 13:54:51.890583] [oven] e->start_at() top->off
	heater_on
	toasting
	[2018-09-12 13:54:51.891473] [oven] e->Toasting() off->toasting
	heater_off
	heater_on
	baking
	[2018-09-12 13:54:51.891989] [oven] e->Baking() toasting->baking
	heater_off
	off
	[2018-09-12 13:54:51.892568] [oven] e->Off() baking->off

.. include:: i_navigation_2.rst

.. _iter2_questions:

Iteration 2 questions
"""""""""""""""""""""

Questions and Answers about code and results (iteration 2):

* :ref:`Can you explain how the picture meets the design specification?<can_you_explain_how_the_picture_meets_the_design_specification>`
* :ref:`How do I write my state callback functions based on the HSM diagram?<can_you_explain_how_the_callbacks_are_arranged_relative_to_each_other>`
* :ref:`How do I use the return_status with these callbacks?<how_do_i_use_the_return_status_with_the_callbacks>`
* :ref:`How does this toaster oven example relate to humans in the story?<how_does_this_toaster_oven_example_relate_to_humans_in_the_story>`
* :ref:`What does posting the events do?<what_does_posting_the_events_do>`
* :ref:`Where are the event names defined?<where_are_the_signal_names_defined>`
* :ref:`What are S and T exactly? Why no just talk about S?<what_are_s_and_t_exactly_why_not_just_talk_about_s>`
* :ref:`Can you explain how this statechart starts?<can_you_explain_how_this_statechart_starts>`
* :ref:`Can you explain how this statechart can transition from off to toasting?<can_you_explain_how_this_statechart_toasts>`
* :ref:`Is there a way I can get miros to show me what happened and how it happened?<is_there_a_way_i_can_get_miros_to_show_me_what_happened_and_how_it_happened>`
* :ref:`Can you explain how this statechart bakes?<can_you_explain_how_this_statechart_bakes>`
* :ref:`Can you explain how this statechart turns off?<can_you_explain_how_this_statechart_turns_off>`
* :ref:`Why are you putting state information into the ToasterOven and not its HSM?<why_are_you_putting_state_into_the_toasteroven_and_not_its_hsm>`
* :ref:`How does your proof show that you met your specification?<how_does_your_proof_show_that_you_met_your_specification_2>`
* :ref:`How do I put something in the oven and cook it?<how_do_i_put_something_in_the_oven_and_cook_it>`

.. _can_you_explain_how_the_picture_meets_the_design_specification:

**Can you explain how the picture meets the design specification?**

Let's break it down:

**The toaster oven will have a door, it will always be closed**

The door_closed state will contain all of the behavior that the system will have
while the door is closed in the toaster oven.

.. image:: _static/ToasterOven_2_spec_1.svg
    :target: _static/ToasterOven_2_spec_1.pdf
    :align: center

All of the statemachine's states exist within this door_closed state, and the
machine is started in the off state.  So the door will always be closed.

**The toaster oven will have an oven light, which can be turned off and on**

The ``light_on`` and ``light_off`` methods are within the ToasterOven class which is
inherited from the ActiveObject class.  The statemachine can access these
methods at anytime.  We see that when the door_closed state is entered, it uses
one of them to shut off the oven light.

.. image:: _static/ToasterOven_2_spec_2.svg
    :target: _static/ToasterOven_2_spec_2.pdf
    :align: center

**The toaster oven will have a heater, which can be turned off and on**

The ``heater_on`` and ``heater_off`` methods are within the ToasterOven class
which is inherited from the ActiveObject class.  The statemachine can access
these methods at anytime.  We see that when the heating state is entered, it
uses one of them to turn on the heater, and when it is exited, it uses the other
one to turn off the heater.

.. image:: _static/ToasterOven_2_spec_3.svg
    :target: _static/ToasterOven_2_spec_3.pdf
    :align: center

**It will have two different heating modes, baking which can bake a potato and toasting which can toast some bread**

The toasting and baking states exist within the heating state.  To get to the
states we need to invent two different events, named, "Baking" and "Toasting".
To allow our statechart to respond to these events, two different arrows are
drawn from the door_closed state into the baking and toasting states.

.. image:: _static/ToasterOven_2_spec_4_1.svg
    :target: _static/ToasterOven_2_spec_4_1.pdf
    :align: center

What these arrows mean in English is, "while I'm in any state within the
door_closed state, a "Baking" event will cause me to enter the baking state, and a
"Toasting" event will cause me to enter the toasting state.

If you haven't seen an HSM before, placing the arrows from the outer state
pointing to an inner state, is the equivalent of drawing these arrows from all
of the states within the outer state to the target inner state.  That last
sentence is hard to parse; its idea is best explained with a picture:

.. image:: _static/ToasterOven_2_spec_4_2.svg
    :target: _static/ToasterOven_2_spec_4_2.pdf
    :align: center

So now we have two different heating modes, but do they behave differently?  No,
they pretty much do the same thing, they are just called different names.

We will add different behaviors to these states in one of the next iterations of
the design.

**The toaster oven should start in the off state**

Before the HSM can start reacting to events, a starting state needs to be
selected.  Here we see we start in the off state, and this meets the
specification.

.. image:: _static/ToasterOven_2_spec_5.svg
    :target: _static/ToasterOven_2_spec_5.pdf
    :align: center

You can see while the unit is off, it is not heating.

**The toaster can only heat when the door is closed**

You can see how we meet this specification item in the picture:

.. image:: _static/ToasterOven_2_spec_6.svg
    :target: _static/ToasterOven_2_spec_6.pdf
    :align: center

**The toaster's light should be off when the door is closed**

We can see that we have met this specification because the oven light is turned
off as the HSM transitions into the off state:

.. image:: _static/ToasterOven_2_spec_7.svg
    :target: _static/ToasterOven_2_spec_7.pdf
    :align: center

.. include:: i_navigation_2.rst

.. _can_you_explain_how_the_callbacks_are_arranged_relative_to_each_other:

**How do I write my state callback functions based on the HSM diagram?**

Consider the HSM part of the statechart:

.. image:: _static/ToasterOven_2_0.svg
    :target: _static/ToasterOven_2_0.pdf
    :align: center

Now lets make a side projection of the HSM (the side projection is not UML):

.. image:: _static/ToasterOven_2_1.svg
    :target: _static/ToasterOven_2_1.pdf
    :align: center

Here is how you would construct the ``door_closed`` state callback:

.. image:: _static/ToasterOven_2_2_door_closed.svg
    :target: _static/ToasterOven_2_2_door_closed.pdf
    :align: center

The callback's if-elif clauses handle the events that interact with the state.
You can see what these events are, by doing the following:

* Trace your eyes around the state boundary, and identify all the arrows that
  start from this boundary.
* Identify all, hooks, entry, exit and init event handlers drawn within the
  state's region.

To build your else clause:

* set the oven.temp.fun to the callback function representing the superstate
* if there is no superstate, set it to the ``top`` attribute of the first argument given to the callback
* ensure that the callback function returns, return_state.SUPER if the else clause is reached.

Now let's see how we would construct the off state callback:

.. image:: _static/ToasterOven_2_2_off.svg
    :target: _static/ToasterOven_2_2_off.pdf
    :align: center

The same rules apply to the other states in the HSM.

So, you can think of the callback functions as actually existing in two
dimensions as a type of DAG:

.. image:: _static/ToasterOven_2_3.svg
    :target: _static/ToasterOven_2_3.pdf
    :align: center

The event processor will use this structure to determine how to behave.

.. include:: i_navigation_2.rst

.. _how_do_i_use_the_return_status_with_the_callbacks:

**How do I use the return_status with these callbacks?**

The event processor will send events to your state callback function.  Your
state callback function will return information to the event processor telling
it how it responded to that event.  There are only certain types of responses
that are permitted with the Miros Samek event processor, and this information is
enumerated in the ``return_status`` object.

The event processor flips back and forth between searching the graph and
sending events to your callbacks to provide the expected behavior of your HSM.

As an application developer you shouldn't care about the inner workings of the
event processing algorithm.  So just follow some simple conventions:

* set status to ``UNHANDLED`` at the top of your callback: 
  ``status = return_status.UNHANDLED``
* if your callback handles an internal event, ``ENTRY_SIGNAL``, ``EXIT_SIGNAL``
  or ``INIT_SIGNAL`` set status to ``HANDLED``:
  ``status = return_status.HANDLED``
* if your callback uses a hook, set the status to ``HANDLED``:
  ``status = return_status.HANDLED``
* if your callback needs to transition to another state, let the ``trans`` set
  the status variable:
  ``status = oven.trans(<some_state>)``
* in the else clause also set the status to ``SUPER``:
  ``status = return_status.SUPER``

.. code-block:: python
  :emphasize-lines: 2-4, 6-8, 10-13, 15-18, 20-22, 24-27, 29-32

  def door_closed(oven, e):
    # set the status variable to the default
    # UNHANDLED attribute
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      # this is an internal event so we set
      # the status to the HANDLED attribute
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      # this is an external event causing a transition
      # so we let the trans method set the status
      # attribute
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      # this is an external event causing a transition
      # so we let the trans method set the status
      # attribute
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      # this is an internal event so we set
      # the status to the HANDLED attribute
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      # this is an external event causing a transition
      # so we let the trans method set the status
      # attribute
      status = oven.trans(off)
    else:
      # this is the else clause, set your status
      # to SUPER
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status


.. note::

  I haven't talked about how to implement a hook yet, you will see this in a
  future design iteration.

.. include:: i_navigation_2.rst

.. _how_does_this_toaster_oven_example_relate_to_humans_in_the_story:

**How does this toaster oven example relate to humans in the story?**

Let's consider the HSM:

.. image:: _static/ToasterOven_3_0.svg
    :target: _static/ToasterOven_3_0.pdf
    :align: center

The humans in the story are the bouncers, the greeters and the bartenders, they
all exist on the earth, which is just the HSM in the metaphor.

The entry and exit bouncers and the greeters are internal events:

.. image:: _static/ToasterOven_3_1.svg
    :target: _static/ToasterOven_3_1.pdf
    :align: center

The bartenders, are the user defined arrows and hooks, they are the external
events:

.. image:: _static/ToasterOven_3_2.svg
    :target: _static/ToasterOven_3_2.pdf
    :align: center

Each of these humans exist as a cause in your callback's if-elif clause
structure.  To participate in their "hack the human" campaign, to give their life
some meaning, you place your code between their clause and how you set the return
status for that clause.  To give the bartenders their secrets, you use the
``trans`` method, to transition to a different state.  To have a greeter move
Spike and Tara along, again, you use the ``trans`` method.

.. code-block:: python

  def door_closed(oven, e):
    status = return_status.UNHANDLED

    # entry bouncer clause
    if(e.signal == signals.ENTRY_SIGNAL):
      # hacking this human
      # Every time he talks to Spike he
      # will turn our oven light's off!
      oven.light_off()
      status = return_status.HANDLED

    # a bartender named 'Baking'
    elif(e.signal == signals.Baking):
      # his secret to Tara is to go to the baking terrace
      status = oven.trans(baking)

    # a bartender named 'Toasting'
    elif(e.signal == signals.Toasting):
      # his secret to Tara is to go to the toasting terrace
      status = oven.trans(toasting)

    # This is the terrace's greeter
    elif(e.signal == signals.INIT_SIGNAL):
      # if Spike and Tara arrive and settle on the terrace
      # will will tell Tara they need to proceed to the
      # off terrace
      status = oven.trans(off)

    # A bartender named 'Off'
    elif(e.signal == signals.Off):
      # his secret to Tara is to go to the off terrace
      status = oven.trans(off)

    else:
      # Tara can't find her answer, so she throw's her
      # event into oblivion
      oven.temp.fun = oven.top
      status = return_status.SUPER

    return status

.. include:: i_navigation_2.rst

.. _what_does_posting_the_events_do:

**What does posting the events do?**

We post the events at the bottom part of our file:

.. code-block:: python
  :emphasize-lines: 4

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(off)
    # toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # turn the oven off
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)

The above code is running in the main thread.  The statechart's thread is
started with the ``start_at`` call.  After this call, your program is running
two threads.

Your oven thread starts up it's event processor, attaches to your callback
graph, searches it and determines how to get ``off``. ;)

While this is happening your main thread is posting events into the oven
thread's first in first out queue. 

.. code-block:: python
  :emphasize-lines: 6, 8, 10

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.start_at(off)
    # toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # turn the oven off
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)

This queue is "thread safe", which means that it can be shared across two
threads.

When the oven's thread finally finishes processing your ``start_at`` call, and it has
situated, **S** and **T** in the off state, it checks it's queue to see if
anything is there.

Remember this picture from the story?

.. image:: _static/md_theo.svg
    :target: _static/md_theo.pdf
    :align: center

The Theo in our toaster oven example is the oven thread, and after finishing its
``start_at`` call, it's queue will look like this:

.. image:: _static/ToasterOven_2_4.svg
    :target: _static/ToasterOven_2_4.pdf
    :align: center


It sees the first posted event,
``Event(signal=signals.Toasting))`` and it passes this information to the event
processor which eventually causes a transition into the ``baking`` state.

Meanwhile your main thread has probably finished processing, and it would like
to exit.  If it were to exit, the oven thread wouldn't get a chance to do all of
it's work.  It still needs to process the "Baking" and "Off" events.

So, we place a ``time.sleep(0.01)`` at the end of our file, to let the oven
thread finish its work before the main thread exits and kills the oven thread.

.. include:: i_navigation_2.rst

.. _where_are_the_signal_names_defined:

**Where are the event names defined?**

The event names are called signals.  A signal has a name and a number.  The
number needs to be unique for each signal.

If you were making your statecharts in c/C++ your signal numbers would be
defined as an enumeration.  But miros is written in Python, so the signals are
objects just like everything else.

The internal signal names, ``EXIT_SIGNAL``, ``ENTRY_SIGNAL``, ``INIT_SIGNAL``
are defined within the miros.event package, but you can access them by importing
``signals`` into your program:

.. code-block:: python

  from miros import signals

To get access to the internal signal objects:

.. code-block:: python

  signals.EXIT_SIGNAL
  signals.ENTRY_SIGNAL
  signals.INIT_SIGNAL

The external signals, or the events that you define in your program, are created
at the moment they are used.   Specifically when you reference an attribute of
the ``signals`` object that doesn't exist within it.  This creation only happens
once, so the signal's name and number remain unique across the life of the
program.

.. code-block:: python

  # signals object does not have a New signal
  some_event_the_system_has_never_seen = Event(signal=signals.New)
  # signals object now has a New signal, it has been assigned a unique number
  # and the name "New"

So do you need to care about this?  No, you just need to remember to type,
``Event(signal=signals.<whatever_name_you_want>)`` and not worry about defining
things before you use them.

.. include:: i_navigation_2.rst

.. _what_are_s_and_t_exactly_why_not_just_talk_about_s:

**What are S and T exactly?  Why not just talk about S?**

The event processor performs two different tasks, it discovers how your HSM is
structured and it follows the entry, exit and init rules described above.  You
can think of these tasks in more general terms as, *planning* and *acting*.

The current state of your statemachine is called **S**, or the *source state*.
If your statechart receives an event that is not handled within it's source state,
the event processor will have to search the next most outer state, then its next
most outer state, until it finds code that knows what to do with the event.
While it searches a state, it marks them as **T**, which stands for the *target
state*.

The event processor's planning phase involves it moving **T** from **S**, and
making a list of the things it needs to do.  When **T** stops on an outer state
that can handle the event, by finding a ``trans`` call, the event processor
stops planning and starts to act.

To act on the plan, the event processor marches **S** outward, towards **T**.
It's plan would be made up of a list of functions that need to be exited. 

Once **S** is positioned in the state that had the ``trans`` call, the event
processor would begin another planning stage.  It would place **T** on the inner
target state, the argument to the ``trans`` call, and make a list of functions that
have to be entered for **S** to march toward **T**.

.. note::

  The only way that the event processor knows that a ``trans`` call was found is
  by monitoring the callback's return_status

  .. code-block:: python

      # ..
      elif(e.signal == signals.Baking):
        status = oven.trans(baking)
      # ..
      return status

It would then act on the plan, and march **S** inward, back to **T**.

Once **S** and **T** are back within the same state, the event processor looks
to see if its init condition, the big black dot on the diagram, has another
``trans`` call, or arrow pointing to another inner state.  If it does, it
creates another plan and then acts on this plan, and re-settles deeper within
the HSM.  This process would repeat until there was nothing left to do.  

If this isn't clear, the upcoming examples will show how these dynamics work.

So why even mention **T**?  As an application developer, you only really care
about **S** right?  Well, no, you can hack the planning stage of the event
processor and make it do useful work.

While **T** is leaving an inner state, looking for an outer state with a
``trans`` call, you can create an elif clause that handles this event in an
outer state, then instead of calling ``trans``, you just return HANDLED.  This
will run your code then snap **T** back to **S** and the process is completed,
this is called a hook.

.. code-block:: python

    # ..
    elif(e.signal == signals.Baking):
      # add your hook code here
      # the planning state of the event processor will
      # run this code, then just snap back to S
      status = return_status.HANDLED
    # ..
    return status

You can use hooks to define common behaviors in the outer states of your HSM.
These behaviors can be shared by all of the inner states.  To get access to this
behavior, you would send your statechart an event that would trigger the hook
and your state machine would run the hook's code and not change states.

This plan-hacking is a very powerful feature of the Miro Samek algorithm.  There
are no hooks in this iteration.  They will be introduced in a future iteration.

.. include:: i_navigation_2.rst

.. _can_you_explain_how_this_statechart_starts:

**Can you explain how this statechart starts?**

I'll answer this question in two different ways, with a short answer and a long
answer.

**Here is the short answer:**

* The oven statechart is instantiated
* **S** and **T** are outside the door_closed state
* the ``start_at`` method of oven is called, it starts the oven's thread and
  places **T** in the off state.
* **S** begins to walk toward **T**, by sending an ENTRY_SIGNAL
  event to the door_closed state callback function.
* **S** lands in the same state as **T**, by sending an ENTRY_SIGNAL event to
  the off state callback function.
* Since **S** and **T** have settled in the same state, the event processor
  sends an INIT_SIGNAL event to the off callback handler; the event is ignored.
* The statechart stops processing and it's thread pends on it's queue

**Here is the long answer:**

Let's talk about how the statechart starts.  In code we see it build an oven,
then started it in its off state:

.. code-block:: python

  oven = ToaterOven(name='oven')
  oven.start_at(off)

Before the oven is started, both **S** and **T**, start outside of the HSM:

.. image:: _static/ToasterOven_2_5_1.svg
    :target: _static/ToasterOven_2_5_1.pdf
    :align: center

The ``start_at`` call places **T** in the off state, starts the thread and begins
the event processor:

.. image:: _static/ToasterOven_2_5_2.svg
    :target: _static/ToasterOven_2_5_2.pdf
    :align: center

The event processor constructs a plan for how to get **S** to **T**.

Next, the plan is put into action;  **S** will start walking through
the entry conditions to re-join **T**; it's first step will trigger the entry
condition of the door_closed state:

.. image:: _static/ToasterOven_2_5_3.svg
    :target: _static/ToasterOven_2_5_3.pdf
    :align: center

This means that the event processor will call the door_closed state with an
ENTRY_SIGNAL event:

.. code-block:: python
  :emphasize-lines: 3,4,5

  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

Your ``door_closed`` callback will catch this event with its if clause, use the
active object's ``light_off`` method to turn off the light, then return
``return_status.HANDLED``, to let the event processor know it handled the
ENTRY_SIGNAL event.

Next, **S** rejoins **T** in the off state, this will trigger the off state's
entry condition:

.. image:: _static/ToasterOven_2_5_4.svg
    :target: _static/ToasterOven_2_5_4.pdf
    :align: center

To trigger the off state's entry condition the event processor will send the
``off`` state callback an ENTRY_SIGNAL event.

.. code-block:: python
  :emphasize-lines: 3-5

  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("off")
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

The ``off`` callback catches the ENTRY_SIGNAL event in its if clause, prints
"off" to the terminal and let's the event processor know it handled the event.

Next, the event processor calls the ``off`` state with an INIT_SIGNAL event.
There is no if-elif clause for this event in the ``off`` function, because we
don't need to initialize the off state in this design.  So the callback notifies
the event processor that it doesn't handle this condition by returning
``return_status.SUPER``; in effect the event is ignored:

.. code-block:: python
  :emphasize-lines: 8

  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("off")
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

Now the event processor has finished its ``start_at`` work.  The first run RTC
process is completed and the oven's thread pends on its queue.

.. image:: _static/ToasterOven_2_5_5.svg
    :target: _static/ToasterOven_2_5_5.pdf
    :align: center

.. include:: i_navigation_2.rst

.. _can_you_explain_how_this_statechart_toasts:

**Can you explain how this statechart can transition from off to toasting?**


I'll answer this question in two different ways, with a short answer and a long
answer.

**Here is the short answer:**

* **S** and **T** are in the off state
* A Toasting event is created an posted to the statechart's first in first out
  queue.
* This causes the event processor to react to the Toasting event in the off
  state.
* **T** begins its search in the off state callback, but no Toasting event handler is
  found
* **T** searches the ``door_closed``, finds that it wants to react to the
  Toasting event by transitioning into the toasting state.
* **T** stops in the door_closed state and waits for **S**
* **S** exits the off state, by sending the EXIT_SIGNAL event to the off
  callback, this event is ignored
* **S** joins **T** in the door_closed state.
* The event processor places **T** into the toasting state.
* **S** starts marching to **T** by first entering the heating state, it does
  this by sending an ENTRY_SIGNAL event to the heating state callback.
* **S** enters the toasting state by sending it's callback an ENTRY_SIGNAL
  event.
* **S** and **T** are both settled in the toasting state so the event processor
  sends an INIT_SIGNAL event to the toasting state callback, this event is
  ignored.
* The RTC process is finished, the oven thread pends on it's queue

**Here is the long answer:**

The starting state is ``off``, meaning that both **S** and **T** are in the off
state.

.. image:: _static/ToasterOven_2_6_1.svg
    :target: _static/ToasterOven_2_6_1.pdf
    :align: center

To toast, we need to send the oven a Toasting event.  This is how we do it with
the miros package:

.. code-block:: python

  oven.post_fifo(Event(signal=signals.Toasting))

The above code places the "Toasting" event into the oven's FIFO:

.. image:: _static/ToasterOven_2_6_2.svg
    :target: _static/ToasterOven_2_6_2.pdf
    :align: center

The oven's thread takes the Toasting event off the queue and passes it to the
event processor.  **T** begins its search; the event processor calls the
``off`` state with a Baking event.

.. image:: _static/ToasterOven_2_6_3.svg
    :target: _static/ToasterOven_2_6_3.pdf
    :align: center

There is no if-elif clause in the ``off`` state callback, so it's else clause is
triggered:

.. code-block:: python
  :emphasize-lines: 6-9

  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("off")
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

This notifies the event processor that the ``off`` state can't handle the Baking
event, and it sets the next place to look to ``door_closed``.  Here we see the
power of the HSM.

Next, **T** checks the ``door_closed`` state to see if it can handle ``Event(signal=signals.Baking)``:

.. image:: _static/ToasterOven_2_6_4.svg
    :target: _static/ToasterOven_2_6_4.pdf
    :align: center

To do this, the event processor calls the ``door_closed`` callback with a Baking event,
which is caught by an elif clause:

.. code-block:: python
  :emphasize-lines: 6,7

  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

The ``door_closed`` function reacts to the Baking event by using the oven's
``trans`` method to request a transition to the ``baking`` state.  It places the
value of the ``trans`` method into it's status variable and returns whatever
this information is, to the event processor.

.. note::
  
  This means that ``door_closed`` is the least common ancestor, LCA, of ``off``
  and ``baking``.

Next, **S** begins moving to rejoin **T**.  It's first step is to call the exit
condition of the off state:

.. image:: _static/ToasterOven_2_6_5.svg
    :target: _static/ToasterOven_2_6_5.pdf
    :align: center

There is no exit condition in the ``off`` state code so it's else clause is
triggered:

.. code-block:: python
  :emphasize-lines: 6-9

  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("off")
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

Next, **S** then rejoins **T**, and they are now both in the ``door_closed``
state.

.. image:: _static/ToasterOven_2_6_6.svg
    :target: _static/ToasterOven_2_6_6.pdf
    :align: center

Next, the event processor places **T** into baking:

.. image:: _static/ToasterOven_2_6_7.svg
    :target: _static/ToasterOven_2_6_7.pdf
    :align: center

Next, **S** begins to climb into the chart so that it can rejoin **T**. It
start's this journey by triggering the entry event of the heating state.  

.. image:: _static/ToasterOven_2_6_8.svg
    :target: _static/ToasterOven_2_6_8.pdf
    :align: center

To do this, the event processor sends an ENTRY_SIGNAL event to the ``heating`` state callback:

.. code-block:: python
  :emphasize-lines: 3-5

  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

The ENTRY_SIGNAL is caught by an elif clause, which will turn the heater on and
tell the event processor it handled the event.

Next, **S** enters the heating state to rejoin **T**

.. image:: _static/ToasterOven_2_6_9.svg
    :target: _static/ToasterOven_2_6_9.pdf
    :align: center

To do this the event processor calls the ``baking`` callback with an ENTRY_SIGNAL event:

.. code-block:: python
  :emphasize-lines: 3-5

  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      print("baking")
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

**S** and **T** are now settled in the baking state, so the event processor
sends an INIT_SIGNAL to the ``baking`` callback to see if it needs to transition
deeper into the statechart.  There is no init handle for this state, so this
event is ignored.

.. note::

  There is only one handled init signal in the whole design and it's in the
  door_closed state.  It will never be called because we start the statechart in
  the off state.  If were where to start the statechart in the door_closed
  state, this init event would be triggered, causing the statemachine to
  ultimately settle into the off state.


Another run to completion process has been finished, so the oven thread, looks
back to it's queue to see if any other thread posted event's to it while it was
trying to toast something:

.. image:: _static/ToasterOven_2_5_5.svg
    :target: _static/ToasterOven_2_5_5.pdf
    :align: center

.. include:: i_navigation_2.rst

.. _is_there_a_way_i_can_get_miros_to_show_me_what_happened_and_how_it_happened:

**Is there a way I can get miros to show me what happened and how it happened?**

Yes, in fact there are two different ways to show you what happened and how it
happened.  If you instrument your state callbacks using the ``@spy_on``
decorator, you can use either the ``trace`` or ``spy`` output.

I will break this answer up into two parts, what you can see with either a
trace or a spy, and how you can use these tools to make sense of your own
designs.

.. note::

  The trace tracks movement of **S** through your HSM.  While the spy tracks
  movements of **T**.  So, to remember which is which, remember that when it
  comes to instrumentation there is an anti-mnemonic at play, ``spy`` tracks **T**
  and the ``trace`` tracks **S**.

  The ``spy`` name was used in miros, because the qp framework uses the word spy
  to output how the event processor is working (how it tracks T).  I wanted the
  concepts to remained consistent for embedded developers who were going to port the
  Python designs into qp, so I kept the spy name, even though it's hard to
  remember.
  
  The last time I checked there was no ``trace`` feature in the qp framework.

**What you can see with a trace:**

We have talked about how the statecharts starts in the off state, now let's look
at how this was reported by the ``trace``:

.. code-block:: python

	[2018-09-12 13:54:51.890583] [oven] e->start_at() top->off

It describes:

  * when the event happened,
  * in what statechart: oven
  * what event caused the transition: start_at
  * the starting state: top
  * the ending state: off.

We have also talked about how the oven transitions from off to the toasting
state.  Here is what was reported by the ``trace``:

.. code-block:: python

	[2018-09-12 13:54:51.891473] [oven] e->Toasting() off->toasting

It describes:

  * when the event happened,
  * in what statechart: oven,
  * what event caused the transition: "Toasting"
  * the starting state: off
  * the ending state: toasting

The ``trace`` is a useful tool to get a very rough understanding about what has
happened with a statechart, but consider all of the information that is missing:

  * It does not report on the entry triggers and init triggers.  
  * It does not describe how the event processor searched your callbacks to discover how the
    HSM is structured.  

To see this information you can use the ``spy`` instrumentation.

**What you can see with the spy:**

Here is the spy output resulting from the ``oven.start_at(off)`` call: 

.. code-block:: python

  START
  SEARCH_FOR_SUPER_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  ENTRY_SIGNAL:door_closed
  ENTRY_SIGNAL:off
  INIT_SIGNAL:off
  <- Queued:(0) Deferred:(0)

The spy output describes an event's signal name and which state it is expressed in.

From the spy output we can monitor the event processor planning and acting
stages.  For instance in the above spy output, we can see the event processor
query the off state and door_closed state with the SEARCH_FOR_SUPER_SIGNAL
event.  This is done so that it can know how to enter the statemachine, then it
acts on this plan by entering the door_closed state, then the off state, then it
settles into the off state by sending it an INIT_SIGNAL event.

At the end of this RTC process, we see what is waiting in the queues for the next
run of the event processor.  We have only been talking about one queue so far, and that is the
first queue in the listing.  The Deferred queue is something you will learn
about in the patterns section.

Here is the spy output for the chart transitioning from the off state to the
toasting state:

.. code-block:: python

  Toasting:off
  Toasting:door_closed
  EXIT_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:toasting
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:heating
  ENTRY_SIGNAL:heating
  ENTRY_SIGNAL:toasting
  INIT_SIGNAL:toasting
  <- Queued:(2) Deferred:(0)

The SEARCH_FOR_SUPER_SIGNAL event lines in the spy output can be confusing to look at.  Miro
Samek's event processing algorithm has to consider 7 different graph topologies,
so as an application developer you might know how and why these calls are taking
place.  Instead, pay attention to the other things in the output:

  * The off state is sent the Toasting event signal (which it doesn't handle)
  * The door_closed state is sent the Toasting event (which causes a trans)
  * The off state is sent the EXIT_SIGNAL event
  * The heating state is sent the ENTRY_SIGNAL event
  * The toasting state is sent the ENTRY_SIGNAL event
  * The toasting state is sent the INIT_SIGNAL

Finally, we see the line describing the state of the queues.  In this case their
are two events pending in the queue, due to our code calling the ``post_fifo``
method with a "Baking" and "Off" event.

To turn on a live spy, replace the live_trace call with the live_spy call in
your code:

.. code-block:: python

  oven.list_spy = True
  oven.start_at(off)

.. include:: i_navigation_2.rst

.. _can_you_explain_how_this_statechart_bakes:

**Can you explain how this statechart bakes?**

To get the statechart to bake, you just send a Bake event to it.  (you can't
open the door and puts things into your oven yet, so there little point to
baking).

Now that we know how to use the trace tool, let's look at the trace output for
this type of transition:

.. code-block:: python

	[2018-09-12 13:54:51.891989] [oven] e->Baking() toasting->baking

We see that the Baking event will cause the statemachine to leave toasting, and
enter the baking state.

For more details, we could look at the spy output for the same transition:

.. code-block:: python
  
  Baking:toasting  # T searching for Baking event in toasting state 1
  Baking:heating   # T searching for Baking event in heating state  2
  Baking:door_closed  # T searching for Baking in door_closed       3
  EXIT_SIGNAL:toasting # S in toasting, exit event sent to toasting 4
  EXIT_SIGNAL:heating  # S in heating, exit even sent to heating    5
  SEARCH_FOR_SUPER_SIGNAL:heating # event processor searching ...   6
  SEARCH_FOR_SUPER_SIGNAL:baking      #  ...
  SEARCH_FOR_SUPER_SIGNAL:door_closed #  ...
  SEARCH_FOR_SUPER_SIGNAL:heating     #  ...
  ENTRY_SIGNAL:heating # S in heating, entry event sent to heating  7
  ENTRY_SIGNAL:baking # S in baking, entry event sent to baking     8
  INIT_SIGNAL:baking # S and T settled, init event sent to baking   9

.. image:: _static/ToasterOven_2_7_1.svg
    :target: _static/ToasterOven_2_7_1.pdf
    :align: center

.. include:: i_navigation_2.rst

.. _can_you_explain_how_this_statechart_turns_off:

**Can you explain how this statechart turns off?**

The oven can be turned off while it already is off, or when it's baking or
toasting.  We will examine how it is turned off while it is baking.

As you have learned from the previous explanations, with a bit of practice, you
can just see how your statechart will react to an event.

To see what has happened this time, let's turn on the ``live_trace`` and
``live_spy`` and examine their outputs.  Here is how to turn on both types of
live instrumentation:

.. code-block:: python
  :emphasize-lines: 3,4,11
  :linenos:

  if __name__ == "__main__":
    oven = ToasterOven(name="oven")
    oven.live_trace = True
    oven.live_spy = True
    oven.start_at(off)
    # toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # turn the oven off
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)

To answer this question, we will be examining the behavior caused by the
transition on line 11.  The system's reaction line 11 will have a trace and spy
which will look like this:

.. code-block:: python

  [2018-09-20 07:55:43.449132] [oven] e->Off() baking->off
  Off:baking
  Off:heating
  Off:door_closed
  EXIT_SIGNAL:baking
  EXIT_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:off
  ENTRY_SIGNAL:off
  INIT_SIGNAL:off
  <- Queued:(0) Deferred:(0)

.. image:: _static/ToasterOven_3_0.svg
    :target: _static/ToasterOven_3_0.pdf
    :align: center


The trace output describes that the "Off" event caused a transition from baking
to off: ``e-Off() baking->off``.  

The spy output describes some of the specifics about how the baking to off
transition took place:

    In a nutshell, it received the "Off" event in the baking state, then it let
    **T** fall outward until it reached the door_closed state, which knew what
    to do with the event.  The event processor moves **S** through the required
    exit conditions until it settles in the door_closed state.  Then it
    places **T** in the off state, and creates a plan for how **S** can be with
    **T** again.  It acts on this plan by sending an ENTRY_SIGNAL to the off
    state.  Both **S** and **T** are settled in the off state, so the event
    processor sends it an INIT_SIGNAL, which is not handled so it is ignored.
    The RTC process is completed and the thread goes back to pending on the
    queue.

You have now examined all of the possible transitions of this statemachine.

.. include:: i_navigation_2.rst

.. _why_are_you_putting_state_into_the_toasteroven_and_not_its_hsm:

**Why are you putting state information into the ToasterOven and not its HSM?**

You can see that we have a ``light_on`` and ``light_off`` method, and the ``heater_on`` and
``heater_off`` method in the ToasterOven's object:

.. image:: _static/ToasterOven_2.svg
    :target: _static/ToasterOven_2.pdf
    :align: center

If this were a real toaster oven, it's state would occur in two different
places.  The first would be in the physical world.  The actual light would be on
or the light would be off.  The physical heater would be heating or that heater
wouldn't be heating.  The second, would be in our software.  The HSM would be in
a state where the light/heater would either be on or off.  The code in the
ToasterOven class would contain the drivers for making the physical equipment do
what our HSM wants it to do.  So, the state would be kept in the HSM not within the
ToasterOven object.

This isn't to say that you can't track state information in your derived
ActiveObject.  There may be situations where you want to do this, it is up to
you.  For instance, if we added a bit more complexity to our design we could set
the oven's temperature.  This could be held in an attribute of the ToasterOven.
You can think of a temperature value as being a kind of state, so, it is
possible to smear state information between your HSM and your object.

HSM's are good at reacting to event's and changing state: As a designer
using miros, you would consider the trade-offs between putting state information
in your object and into your HSM.  The goal would be to meet your specification
while minimizing your design's complexity.  To do this well will require you to
practice.

.. include:: i_navigation_2.rst

.. _how_does_your_proof_show_that_you_met_your_specification_2:

**How does your proof show that you met your specification?**

From this design:

.. image:: _static/ToasterOven_2.svg
    :target: _static/ToasterOven_2.pdf
    :align: center

We preform these actions:

.. code-block:: python

  if __name__ == "__main__":
      oven = ToasterOven(name="oven")
      oven.live_trace = True
      oven.start_at(off)
      # toast something
      oven.post_fifo(Event(signal=signals.Toasting))
      # bake something
      oven.post_fifo(Event(signal=signals.Baking))
      # turn the oven off
      oven.post_fifo(Event(signal=signals.Off))
      time.sleep(0.01)

We see this output to our terminal, which I have called proof that the design
works:

.. code-block:: python

  > python3 toaster_oven_2.py
  off
  [2018-09-12 13:54:51.890583] [oven] e->start_at() top->off
  heater_on
  toasting
  [2018-09-12 13:54:51.891473] [oven] e->Toasting() off->toasting
  heater_off
  heater_on
  baking
  [2018-09-12 13:54:51.891989] [oven] e->Baking() toasting->baking
  heater_off
  off
  [2018-09-12 13:54:51.892568] [oven] e->Off() baking->off

The trace output happens after the statechart has reacted to an event, so all
of the print statements should happen before the trace reports on what happened.

We see that the oven starts in the off state, which reports an "off" to the
terminal.  

The oven is then sent a "Toasting" event.  This causes a transition from the off
state to the toasting state. To perform this transition the oven turns the
heater on with its entry condition to the heating state.  We see this happened
because our ToasterOven's ``heater_on`` driver just writes "heater_on" to the
terminal.  Then the toasting state's entry condition prints "toasting" to the
terminal.

Next, we send a "Baking" event.  It exits the heating state, causing the
"heater_off" to print, then it re-enters to the heating state, which causes the
"heater_on" to print and the enters the baking state, causing it's entry
condition to print "baking".

Finally, we send the "Off" event to oven.  This causes a transition from baking
to off.  To do this it prints "heater_off" from the exit condition of the
heating state and prints "off" from the entry condition of the off state.

.. include:: i_navigation_2.rst

.. _how_do_i_put_something_in_the_oven_and_cook_it:

**How do I put something in the oven and cook it?**

You can't, we don't even know if our customer's want to cook anything, so we
will ship it, discover what our customers want through the customer discovery
process, then pivot if the need arises.

.. include:: i_navigation_2.rst

.. _iter3:

Iteration 3: history
--------------------
So far, we have miros working on our system and we have build a simple toaster
oven. But, as it is currently written, the toaster oven is useless, because
there is no way to open and close the door.

So, in this design iteration we will add the ability to open and close the door.  

.. include:: i_navigation_3.rst

.. _iter3_spec:

Iteration 3 specification
"""""""""""""""""""""""""
The toaster oven spec:

* :dead_spec:`The toaster oven will have a door, it will always be closed`
* The toaster oven will have an oven light, which can be turned on and off
* The toaster oven will have a heater, which can be turned on and off
* It will have two different heating modes, baking which can bake a potato
  and toasting which can toast some bread
* The toaster oven should start in the off state
* The toaster can only heat when the door is closed
* The toaster's light should be off when the door is closed
* :new_spec:`The toaster should turn on its light when the door is opened`
* :new_spec:`A customer should be able to open and close the door of our toaster oven`
* :new_spec:`When a customer closes the door, the toaster oven should go back to behaving
  like it did before.`

----

**Technical Improvments**

* :new_spec:`Remove the print statements from your production code.`

.. include:: i_navigation_3.rst

.. _iter3_design:

Iteration 3 design
""""""""""""""""""

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

.. include:: i_navigation_3.rst

.. _iter3_code:

Iteration 3 code
""""""""""""""""

.. code-block:: python
  :emphasize-lines: 1, 12, 15, 18, 21, 24, 40-41, 65, 66, 78, 89, 90, 97-107 
  :linenos:

   # toaster oven iteration 3
   from miros import ActiveObject
   from miros import return_status
   from miros import Event
   from miros import signals
   from miros import spy_on
   import time

   class ToasterOven(ActiveObject):
     def __init__(self, name):
       super().__init__(name)
       self.history = None

     def light_on(self):
       self.scribble("light_on")

     def light_off(self):
       self.scribble("light_off")

     def heater_on(self):
       self.scribble("heater_on")

     def heater_off(self):
       self.scribble("heater_off")

   @spy_on
   def door_closed(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.light_off()
       status = return_status.HANDLED
     elif(e.signal == signals.Baking):
       status = oven.trans(baking)
     elif(e.signal == signals.Toasting):
       status = oven.trans(toasting)
     elif(e.signal == signals.INIT_SIGNAL):
       status = oven.trans(off)
     elif(e.signal == signals.Off):
       status = oven.trans(off)
     elif(e.signal == signals.Door_Open):
       status = oven.trans(door_open)
     else:
       oven.temp.fun = oven.top
       status = return_status.SUPER
     return status

   @spy_on
   def heating(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.heater_on()
       status = return_status.HANDLED
     elif(e.signal == signals.EXIT_SIGNAL):
       oven.heater_off()
       status = return_status.HANDLED
     else:
       oven.temp.fun = door_closed
       status = return_status.SUPER
     return status

   @spy_on
   def baking(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.scribble("baking")
       oven.history = baking
       status = return_status.HANDLED
     else:
       oven.temp.fun = heating
       status = return_status.SUPER
     return status

   @spy_on
   def toasting(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.scribble("toasting")
       oven.history = toasting
       status = return_status.HANDLED
     else:
       oven.temp.fun = heating
       status = return_status.SUPER
     return status

   @spy_on
   def off(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.scribble("off")
       oven.history = off
       status = return_status.HANDLED
     else:
       oven.temp.fun = door_closed
       status = return_status.SUPER
     return status

   @spy_on
   def door_open(oven, e):
     status = return_status.UNHANDLED
     if(e.signal == signals.ENTRY_SIGNAL):
       oven.light_on()
     elif(e.signal == signals.Door_Close):
       status = oven.trans(oven.history)
     else:
       oven.temp.fun = oven.top
       status = return_status.SUPER
     return status

.. include:: i_navigation_3.rst

.. _iter3_proof:


Iteration 3 proof
"""""""""""""""""
To prove our design works we could turn on the spy, then:

   * start the oven 
   * open the door
   * close the door
   * bake something
   * open the door
   * close the door
   * toast something
   * open the door
   * close the door

But the spy output would be tedious for you to read, so instead, I'll just
turn on the trace, toast something, open the door, then close the door again,
then ship the product. HeeHaw.

.. code-block:: python

   oven = ToasterOven(name="oven")
   oven.live_trace = True
   oven.start_at(off)

   # toast something
   oven.post_fifo(Event(signal=signals.Toasting))
   # open the door
   oven.post_fifo(Event(signal=signals.Door_Open))
   # close the door
   oven.post_fifo(Event(signal=signals.Door_Close))

   time.sleep(0.01)

Here are the results:

.. code-block:: python
   
  [2019-01-31 06:32:28.095880] [oven] e->start_at() top->off
  [2019-01-31 06:32:28.098218] [oven] e->Toasting() off->toasting
  [2019-01-31 06:32:28.099014] [oven] e->Door_Open() toasting->door_open
  [2019-01-31 06:32:28.099489] [oven] e->Door_Close() door_open->toasting

That's kind of hard to read too, so here is a sequence diagram expressing the same
information:

.. code-block:: python

  [Statechart: oven]
         top              off           toasting         door_open
          +---start_at()-->|                |                |
          |      (1)       |                |                |
          |                +---Toasting()-->|                |
          |                |      (2)       |                |
          |                |                +---Door_Open()->|
          |                |                |      (3)       |
          |                |                +<-Door_Close()--|
          |                |                |      (4)       |

1-2.  Same behavior as the previous design

3. The ``door_open`` state can be transitioned to.

4. While in the ``door_open`` state, a ``Door_Close`` event causes the unit to
   go back into its previous state, the toasting state.

As a first pass, this is looking good, but is it a proof that our system is
working.  Not even close.

We will get serious about :ref:`testing in the next iteration <iter4_proof>`.

.. include:: i_navigation_3.rst

.. _iter3_questions:

Iteration 3 questions
"""""""""""""""""""""

* :ref:`Can you show the full proof that the system works? <zero_to_one-can-you-show-the-proof-that-the-system-works3>`
* :ref:`What does the H with a star beside it mean? <zero_to_one-what-does-the-h-with-a-star-beside-it-mean3>`
* :ref:`How does your code give me the deep history feature? <zero_to_one-how-does-your-code-give-me-the-deep-history-feature3>`
* :ref:`Why don't you set the history attribute in the door_closed and heating states? <zero_to_one-why-don-t-you-set-the-history-attribute-in-the-door_closed-off-and-heating-states3>`
* :ref:`If you are removing unneeded things from your code, then what is the init event for? <zero_to_one-if-you-are-removing-unneeded-things-from-your-code,-then-what-is-the-init-signal-for3>`
* :ref:`Why is the state pattern oval put on the diagram? <zero_to_one-why-is-the-state-pattern-oval-put-on-the-diagram3>`
* :ref:`Isn't the Deep history icon and the call to oven history redundant?  <bbbbbbbbbbbbbbb>`
* :ref:`Why isn't the deep history handled by the framework? <zero_to_one-why-isn't-the-deep-history-handled-by-the-framework3>`
* :ref:`What is the difference between deep and shallow history? <zero_to_one-what-is-the-difference-between-deep-and-shallow-history3>`
* :ref:`Can you map this history idea back onto the story? <zero_to_one-can-you-map-this-history-idea-back-onto-the-story3>`

.. include:: i_navigation_3.rst

.. _zero_to_one-can-you-show-the-proof-that-the-system-works3:

**Can you show the full proof that the system works?**

We can turn on the `spy` and `trace` instrumentation and run the design
through all of it's state transitions.  Then we can look at the
instrumentation's output to see if it worked as expected.

.. code-block:: python

   oven = ToasterOven(name="oven")
   oven.live_spy = True
   oven.live_trace = True  # I'll add this to interleave the trace

   # Start the oven in the Off state
   oven.start_at(off)
   # Open the door
   oven.post_fifo(Event(signal=signals.Door_Open))
   # Close the door
   oven.post_fifo(Event(signal=signals.Door_Close))
   # Bake something
   oven.post_fifo(Event(signal=signals.Baking))
   # Open the door
   oven.post_fifo(Event(signal=signals.Door_Open))
   # close the door
   oven.post_fifo(Event(signal=signals.Door_Close))
   # Toast something
   oven.post_fifo(Event(signal=signals.Toasting))
   # Open the door
   oven.post_fifo(Event(signal=signals.Door_Open))
   # Close the door
   oven.post_fifo(Event(signal=signals.Door_Close))

   time.sleep(0.1)

Here is the instrumentation's live output:

.. code-block:: python
  :emphasize-lines: 1, 6, 11, 19, 22, 29, 34, 47, 59, 62, 70, 77, 94, 106, 109, 117
  :linenos:
   
  [2019-01-31 08:30:22.869093] [oven] e->start_at() top->off
  START
  SEARCH_FOR_SUPER_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  ENTRY_SIGNAL:door_closed
  light_off
  ENTRY_SIGNAL:off
  off
  INIT_SIGNAL:off
  <- Queued:(0) Deferred:(0)
  [2019-01-31 08:30:22.873013] [oven] e->Door_Open() off->door_open
  Door_Open:off
  Door_Open:door_closed
  EXIT_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_closed
  ENTRY_SIGNAL:door_open
  light_on
  INIT_SIGNAL:door_open
  <- Queued:(7) Deferred:(0)
  [2019-01-31 08:30:22.874019] [oven] e->Door_Close() door_open->off
  Door_Close:door_open
  SEARCH_FOR_SUPER_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_open
  ENTRY_SIGNAL:door_closed
  light_off
  ENTRY_SIGNAL:off
  off
  INIT_SIGNAL:off
  <- Queued:(6) Deferred:(0)
  [2019-01-31 08:30:22.875289] [oven] e->Baking() off->baking
  Baking:off
  Baking:door_closed
  EXIT_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:baking
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:heating
  ENTRY_SIGNAL:heating
  heater_on
  ENTRY_SIGNAL:baking
  baking
  INIT_SIGNAL:baking
  <- Queued:(5) Deferred:(0)
  [2019-01-31 08:30:22.876085] [oven] e->Door_Open() baking->door_open
  Door_Open:baking
  Door_Open:heating
  Door_Open:door_closed
  EXIT_SIGNAL:baking
  EXIT_SIGNAL:heating
  heater_off
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_closed
  ENTRY_SIGNAL:door_open
  light_on
  INIT_SIGNAL:door_open
  <- Queued:(4) Deferred:(0)
  [2019-01-31 08:30:22.877258] [oven] e->Door_Close() door_open->baking
  Door_Close:door_open
  SEARCH_FOR_SUPER_SIGNAL:baking
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_open
  ENTRY_SIGNAL:door_closed
  light_off
  ENTRY_SIGNAL:heating
  heater_on
  ENTRY_SIGNAL:baking
  baking
  INIT_SIGNAL:baking
  <- Queued:(3) Deferred:(0)
  [2019-01-31 08:30:22.878420] [oven] e->Toasting() baking->toasting
  Toasting:baking
  Toasting:heating
  Toasting:door_closed
  EXIT_SIGNAL:baking
  EXIT_SIGNAL:heating
  heater_off
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:toasting
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:heating
  ENTRY_SIGNAL:heating
  heater_on
  ENTRY_SIGNAL:toasting
  toasting
  INIT_SIGNAL:toasting
  <- Queued:(2) Deferred:(0)
  [2019-01-31 08:30:22.879734] [oven] e->Door_Open() toasting->door_open
  Door_Open:toasting
  Door_Open:heating
  Door_Open:door_closed
  EXIT_SIGNAL:toasting
  EXIT_SIGNAL:heating
  heater_off
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_closed
  ENTRY_SIGNAL:door_open
  light_on
  INIT_SIGNAL:door_open
  <- Queued:(1) Deferred:(0)
  [2019-01-31 08:30:22.880552] [oven] e->Door_Close() door_open->toasting
  Door_Close:door_open
  SEARCH_FOR_SUPER_SIGNAL:toasting
  SEARCH_FOR_SUPER_SIGNAL:door_open
  SEARCH_FOR_SUPER_SIGNAL:heating
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  EXIT_SIGNAL:door_open
  ENTRY_SIGNAL:door_closed
  light_off
  ENTRY_SIGNAL:heating
  heater_on
  ENTRY_SIGNAL:toasting
  toasting
  INIT_SIGNAL:toasting
  <- Queued:(0) Deferred:(0)

I have highlighted the lines the show us it is working.

This is a reasonable spot check, but it's not really something you would want to
leave as a regression test.

A better testing approach is :ref:`demonstrated in the next iteration. <iter4_proof>`

.. include:: i_navigation_3.rst

.. _zero_to_one-what-does-the-h-with-a-star-beside-it-mean3:

**What does the H with a star beside it mean?**

The H with a star beside it is called the :ref:`deep history <deep-history-icon>` pseudostate.  A
pseudostate is any useful glyph that touches an arrow or event on a statechart, that isn't actually a state.

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

When an arrow points to a deep history pseudostate, it means, go back to the
last activated state that was used in that region of the statechart.  

.. image:: _static/ToasterOven_3_Span.svg
   :target: _static/ToasterOven_3_Span.pdf
   :align: center

In our example this could be anyone of the ``heating``, ``baking``, ``toasting``
or ``off`` states.

.. image:: _static/ToasterOven_3_Possible_States.svg
   :target: _static/ToasterOven_3_Possible_States.pdf
   :align: center


.. include:: i_navigation_3.rst

.. _zero_to_one-how-does-your-code-give-me-the-deep-history-feature3:

**How does your code give me the deep history feature?**

The event processor in miros doesn't support the deep history pattern directly.  

To make a statechart that gives you the deep-history behaviour you can:

   * add a ``history`` attribute to your ActiveObject derived class, in this
     example the ToasterOven class.

   * upon entering a state that is within a region spanned by a deep history
     pseudostate, assign the state's name to the history attribute in that
     state's entry condition.

   * when you want to transition to history, transition to the state held in the
     ``history`` attribute: ``status = oven.trans(oven.history)``

If you look at the :ref:`code <iter3_code>` and compare it to the :ref:`design <iter3_design>` you will see that this is what I have done.

.. include:: i_navigation_3.rst

.. _zero_to_one-why-don-t-you-set-the-history-attribute-in-the-door_closed-off-and-heating-states3:

**Why don't you set the history attribute in the door_closed and heating states?**

The ``door_closed`` and ``heating_states`` are transitory states; the toaster
oven can't settle into either of these states.  So, the history attribute
doesn't need to be assigned for them.

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

By making this design decision I am breaking the Harel formalism, a deep history
icon should be able to go to the ``heating`` state too.  I'm not going to
include it because I don't need it, and I can't test it anyway.

.. include:: i_navigation_3.rst

.. _zero_to_one-if-you-are-removing-unneeded-things-from-your-code,-then-what-is-the-init-signal-for3:

**If you are removing unneeded things from your code, then what is the init event for?**

Good point, if you look at the design, you see that the statechart starts in the
``off`` state: ``oven.start_at(off)``.  There is no need for the init
pseudostate in the ``door_closed`` region, at least when looking at how the
toaster oven turns on.

How about after the door has been closed?  Well as discussed in the previous
answer, the unit can only transition back into the ``baking``, ``toasting`` or
``off`` states after the door is closed; we still don't need that init pseudostate.

Are there any other ways we can get into the ``door_closed`` region?  No.  So,
this design doesn't need the ``door_closed`` init signal.

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

But if a maintenance developer were to change the ``oven.start_at(off)`` code to
``oven.start_at(door_closed)`` our design would still work, because the init
pseudostate would cause the system to settle into the off state.

What would happen if the maintenance developer changed the
``oven.start_at(off)`` to ``oven.start_at(heating)``?  Well, this would be a
bug.  The unit would heat in an undefined way, it wouldn't be baking or
toasting.

.. note::

  As a design evolves you will end up with a lot of vestigial parts.  Things
  that used to be needed, but aren't needed anymore, like an appendix, or
  tonsils.

This illustrates two different design philosophies, we can be:

   * minimalist

   * or, hardened

The minimalist approach would try to reduce the design to just what it needs to
work.  The hardened approach would try and kind of future proof the design
against changes made by a maintenance developer:

.. image:: _static/ToasterOven_3_Hardened.svg
   :target: _static/ToasterOven_3_Hardened.pdf
   :align: center

The above diagram describes a hardened design: all the intermediate states have
init signals and all of the states in the deep history region assign their
callback function's address to the ``oven.history`` attribute in their entry conditions.

If we were to use the above design, we would now have a bug in our
specification: there a is no description of the default
behavior of our heating state. We could just go back and fix it, but this will
clutter our specification with unneeded complexity.  We should keep the
specifications short and legible.

At first glance you might be tempted to take the hardened approach; but over a
long period of time, your statecharts will have more and more unused, untested and
unneeded code within them.  You will accumulate some technical debt.

There is no right answer to this, but personally I lean towards keeping a design
as simple as possible, I lean towards minimalism.  If I'm conscious of a choice between
a complicated thing and a simple thing, I will pick the simple thing.

I'll change the design in the next iteration so that the unit starts in the
``door_closed`` state.  (I want that init event to be useful, because I'm
trying to explain how statecharts work here)

.. include:: i_navigation_3.rst

.. _zero_to_one-why-is-the-state-pattern-oval-put-on-the-diagram3:

**Why is the state pattern oval put on the diagram?**

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

The statechart patterns use different parts of the diagram to work together to
provide a global behavior described by that pattern.  To make it easier for
someone to understand this, the oval is put on the diagram to announce what
is going on.  

If you don't know what the transition to history is, you can just :ref:`look it
up <patterns>` and understand the designer's intention, then look and see how
that pattern applies to the specific design.

.. include:: i_navigation_3.rst


.. _bbbbbbbbbbbbbbb:

**Isn't the Deep history icon and the call to oven history redundant?**

When we put our other arrows on this chart we didn't write their ``trans`` calls on
them.  So, yes, the call to ``oven.trans(oven.history)`` is kind of
redundant; the arrow to the deep history icon should be enough.  But, remember
that the deep history feature isn't supported by this version of the statechart
algorithm; so, let's help the person reading the page see explicitly how we are
going to make the pattern work.

We need the deep history icon as a clean shorthand, or we would have to draw
arrows to all of our states (Super Ugly):

.. image:: _static/ToasterOven_3_Redundant.svg
   :target: _static/ToasterOven_3_Redundant
   :align: center

Versus (less Ugly):

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

So yes, the diagram has some redundancy in it and it is useful.

.. include:: i_navigation_3.rst

.. _zero_to_one-why-isn't-the-deep-history-handled-by-the-framework3:

**Why isn't the deep history handled by the framework?**

The event processor in this library is based on the work published by Miro
Samek, who is coming from an embedded background.  His algorithm is blazingly
fast and his code had a tiny memory footprint; he wanted it to work on small
processors.

You can use his framework instead of having a real time operating system.  It
includes it's own event loop and software bus.  It's really cool.

What it didn't have was the high level statechart features like transition to
deep history and transition to shallow history, or orthogonal regions, but he
gave them to his audience through app-notes; "just write your code like this and
you get the same effect".

I haven't looked at his stuff lately, it wouldn't surprise me if he has the
history features in his contemporary framework.  (embedded processors are much
more powerful now).

.. include:: i_navigation_3.rst

.. _zero_to_one-what-is-the-difference-between-deep-and-shallow-history3:

**What is the difference between deep and shallow history?**

Shallow history pseudostates, only cause transitions into the first level of states within
the region they span.   The shallow history icon is an H in a circle **without** the
star beside it.

If we replaced the deep history icon in this diagram with a shallow history
icon, only the ``heating`` and ``off`` states could be reached with a Door_Close
event.

.. image:: _static/ToasterOven_3.svg
   :target: _static/ToasterOven_3.pdf
   :align: center

I'm sure there are applications where the shallow history icon is useful; but I
have never used one.

.. include:: i_navigation_3.rst

.. _zero_to_one-can-you-map-this-history-idea-back-onto-the-story3:

**Can you map this history idea back onto the story?**

Imagine that the bartender named ``Door_Close`` in the ``door_open`` bar has a
pair of binoculars hanging around his neck (with a deep history icon painted on
them as their brand).  He uses them to watch where Tara and Spike drink when
they are in any bar above the door_closed terrace, taking note of their last
location.

When Tara asks him for directions he whispers his answer in her ear.

(if you can think of a better way of adding to this story email me)

.. include:: i_navigation_3.rst

.. _iter4:

Iteration 4: hook, testing and hardware abstraction
------------------------------------------
So far we have built a very basic toaster oven using a statechart.

In this iteration we will change the design so that:

* The unit can make a buzzing sound from any state of operation.
* We can decouple our hardware tests from our statemachine tests.

.. include:: i_navigation_4.rst

.. _iter4_spec:

Iteration 4 specification
"""""""""""""""""""""""""

The toaster oven spec:

* The toaster oven will have an oven light, which can be turned on and off
* The toaster oven will have a heater, which can be turned off and on
* It will have two different heating modes, baking which can bake a potato
  and toasting which can toast some bread
* The toaster oven should start in the off state
* The toaster can only heat when the door is closed
* The toaster's light should be off when the door is closed
* The toaster should turn on its light when the door is opened
* A customer should be able to open and close the door of our toaster oven
* When a customer closes the door, the toaster oven should go back to behaving
  like it did before
* :new_spec:`While the toaster oven is in any state the customer should be able to press a
  buzzer which will get the attention of anyone nearby`

**Technical Improvements**

* :new_spec:`Start the toaster oven in the door_closed state`
* :new_spec:`Test the statechart off of the hardware target`
* :new_spec:`Test the code the controls the hardware in isolation from the statechart code`

.. _iter4_design:

Iteration 4 design
""""""""""""""""""

.. image:: _static/ToasterOven_4.svg
    :target: _static/ToasterOven_4.pdf
    :align: center

.. include:: i_navigation_4.rst

.. _iter4_code:

Iteration 4 code
""""""""""""""""

.. code-block:: python
  :emphasize-lines: 9-27, 29-52, 54-64, 83, 142
  :linenos:

  # iteration 4 
  from miros import ActiveObject
  from miros import return_status
  from miros import Event
  from miros import signals
  from miros import spy_on
  import time
  
  class ToasterOvenMock(ActiveObject):
    def __init__(self, name):
      super().__init__(name)
      self.history = None
  
    def light_on(self):
      self.scribble("light_on")
  
    def light_off(self):
      self.scribble("light_off")
  
    def heater_on(self):
      self.scribble("heater_on")
  
    def heater_off(self):
      self.scribble("heater_off")
      
    def buzz(self):
      self.scribble("buzz")
      
  class ToasterOven(ActiveObject):
    def __init__(self, name):
      super().__init__(name)
      self.history = None

    def light_on(self):
      # call to your hardware's light_on driver
      pass

    def light_off(self):
      # call to your hardware's light_off driver
      pass
      
    def heater_on(self):
      # call to your hardware's heater on driver
      pass

    def heater_off(self):
      # call to your hardware's heater off driver
       pass
      
    def buzz(self):
      # call to your hardware's buzzer
      pass
  
  @spy_on
  def common_features(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Buzz):
      print("buzz")
      oven.buzz()
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status
  
  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    elif(e.signal == signals.Door_Open):
      status = oven.trans(door_open)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status
  
  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status
  
  @spy_on
  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = baking
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = toasting
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status
  
  @spy_on
  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = off
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status
  
  @spy_on
  def door_open(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_on()
    elif(e.signal == signals.Door_Close):
      status = oven.trans(oven.history)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status

.. include:: i_navigation_4.rst

.. _iter4_proof:

Iteration 4 proof
"""""""""""""""""
To satisfy our modularity requirement, we create a new class called
ToasterOvenMock.  The word `mock` is a common word in software testing, it
describes any piece of code that can stand in for another more complicated piece
of code. You would use a software mock to test one part of the system in
isolation from another part of the system.

.. image:: _static/ToasterOven_4.svg
    :target: _static/ToasterOven_4.pdf
    :align: center

To separate the code that controls the hardware from the code that manages the
feature-state of the product, we create a new class called ToasterOvenMock.  It
will have the exact same API as the real ToasterOven class, but its methods
won't make hardware calls that turn on and off lights/heaters and make buzzing sounds,
instead they will drop debug-strings into the spy instrumentation stream using
the ``scribble`` method.

To test our actual hardware features, we would instantiate the ToasterOven class
on our hardware and call the ``buzz``, ``heater_on``, ``heater_off``,
``light_on`` and ``light_off`` methods and see if they work as advertised. (I
won't show how to do this)

To test the statemachine, we would use the ToasterOvenMock class, because all of
it's hardware dependent calls have been mocked.  That makes the code portable,
so it can be tested anywhere Python can run.

We want to confirm that the code works like we have drawn it on our diagram.  We
don't need to test the event processor because we trust that it is working, and
we trust the formal set of behaviors that it follows.  This let's us simplify
things a lot.

Here is a regression test for this design:

.. _iter4_proof_code:

.. code-block:: python

    import re
    from miros import stripped

    # test helper functions
    def trace_through_all_states():
      oven = ToasterOvenMock(name="oven")
      oven.start_at(door_closed)
      # Open the door
      oven.post_fifo(Event(signal=signals.Door_Open))
      # Close the door
      oven.post_fifo(Event(signal=signals.Door_Close))
      # Bake something
      oven.post_fifo(Event(signal=signals.Baking))
      # Open the door
      oven.post_fifo(Event(signal=signals.Door_Open))
      # Close the door
      oven.post_fifo(Event(signal=signals.Door_Close))
      # Toast something
      oven.post_fifo(Event(signal=signals.Toasting))
      # Open the door
      oven.post_fifo(Event(signal=signals.Door_Open))
      # Close the door
      oven.post_fifo(Event(signal=signals.Door_Close))
      time.sleep(0.01)
      return oven.trace()
    
    def spy_on_light_on():
      oven = ToasterOvenMock(name="oven")
      oven.start_at(door_closed)
      # Open the door to turn on the light
      oven.post_fifo(Event(signal=signals.Door_Open))
      time.sleep(0.01)
      # turn our array into a paragraph
      return "\n".join(oven.spy())
    
    def spy_on_light_off():
      oven = ToasterOvenMock(name="oven")
      # The light should be turned off when we start
      oven.start_at(door_closed)
      time.sleep(0.01)
      # turn our array into a paragraph
      return "\n".join(oven.spy())

    def spy_on_heater_on():
      oven = ToasterOvenMock(name="oven")
      # The light should be turned off when we start
      oven.start_at(door_closed)
      oven.post_fifo(Event(signal=signals.Toasting))
      time.sleep(0.01)
      # turn our array into a paragraph
      return "\n".join(oven.spy())

    def spy_on_heater_off():
      oven = ToasterOvenMock(name="oven")
      # The light should be turned off when we start
      oven.start_at(door_closed)
      oven.post_fifo(Event(signal=signals.Toasting))
      oven.clear_spy()
      oven.post_fifo(Event(signal=signals.Off))
      time.sleep(0.01)
      # turn our array into a paragraph
      return "\n".join(oven.spy())
      
    def spy_on_buzz():
      oven = ToasterOvenMock(name="oven")
      # Send the buzz event
      oven.post_fifo(Event(signal=signals.Buzz))
      time.sleep(0.01)
      # turn our array into a paragraph
      return "\n".join(oven.spy())

    # Tests start here
    # Confirm our state transitions work as designed
    trace_target = """
    [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
    [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
    [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
    [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
    [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
    [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
    [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
    [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
    [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
    """

    with stripped(trace_target) as stripped_target, \
         stripped(trace_through_all_states()) as stripped_trace_result:
      
      for target, result in zip(stripped_target, stripped_trace_result):
        assert(target == result)

    # Confirm our light turns off
    assert re.search(r'off', spy_on_light_off())

    # Confirm our light turns on
    assert re.search(r'on', spy_on_light_on())

    # Confirm the heater turns on
    assert re.search(r'heater_on', spy_on_heater_on())

    # Confirm the heater turns on
    assert re.search(r'heater_off', spy_on_heater_off())

    # Confirm our buzzer works
    assert re.search(r'buzz', spy_on_buzz())

.. include:: i_navigation_4.rst

.. _iter4_questions:

Iteration 4 questions
"""""""""""""""""""""
* :ref:`Can you explain how the unit can buzz from any state? <zero_to_one-can-you-explain-how-the-unit-can-buzz-from-any-state4>`
* :ref:`Can you relate the buzz hook to the story? <zero_to_one-can-you-relate-the-buzz-hook-to-the-story4>`
* :ref:`The buzz seems like a pointless feature, what's going on? <zero_to_one-the-buzz-seems-like-a-pointless-feature,-what's-going-on4>`
* :ref:`Are entry and exit events hooks too? <zero_to_one-are-entry-and-exit-events-hooks-too4>`
* :ref:`Why are you showing two classes on the diagram? <zero_to_one-why-are-you-showing-two-classes-on-the-diagram4>`
* :ref:`What is a hardware abstraction layer? <zero_to_one-what-is-a-hardware-abstraction-layer4>`
* :ref:`Where is the hardware abstraction you listed in your title? <zero_to_one-where-is-the-hardware-abstraction-layer-you-listed-in-your-title4>`
* :ref:`Why do you break the transition-tests apart from the other tests? <zero_to_one-in-your-tests,-why-do-you-break-transition-tests-apart-from-calls-to-light_on,-light_off-and-so-on4>` 
* :ref:`Why don't you just copy out your spy output and use it as the test target? <zero_to_one-why-don't-you-just-copy-out-your-spy-output-and-use-it-as-the-test-target4>`
* :ref:`Where did you get your trace-test-target, and what is going on with that stripped call? <zero_to_one-where-did-you-get-your-trace-test-target,-and-what-is-going-on-with-that-stripped-call4>`
* :ref:`Why don't you just copy out your trace output and use it as a test target? <zero_to_one-why-don't-you-just-copy-out-your-trace-output-and-use-it-as-a-test-target4>`
* :ref:`Your light_on, light_off ... tests seem pretty light, are you sure you are testing these features? <zero_to_one-your-light_on,-light_off-...-tests-seem-pretty-light,-are-you-sure-you-are-testing-these-features4>`

.. _zero_to_one-can-you-explain-how-the-unit-can-buzz-from-any-state4:

**Can you explain how the unit can buzz from any state?**

Let's send some Buzz events to our statechart and see how it behaves:

.. code-block:: python

   oven = ToasterOven(name="oven")

   # start our oven
   oven.start_at(door_closed)
   time.sleep(0.01)  # let the oven thread catch up to main

   # What state?
   print(oven.state_name)

   # Trigger the buzzer
   oven.post_fifo(Event(signal=signals.Buzz))
   time.sleep(0.01)

   # What state?
   print(oven.state_name)

   # Toast something
   oven.post_fifo(Event(signal=signals.Toasting))
   time.sleep(0.01)

   # What state?
   print(oven.state_name)

   # Trigger the buzzer
   oven.post_fifo(Event(signal=signals.Buzz))
   time.sleep(0.01)

   # What state?
   print(oven.state_name)

.. code-block:: python

   off
   buzz
   off
   toasting
   buzz
   toasting

The statechart reacts to the ``Buzz`` event without changing state.

.. image:: _static/ToasterOven_4.svg
   :target: _static/ToasterOven_4.pdf
   :align: center

The buzz code is being hooked by the ``common_features`` state, you can see this
by looking at the top left corner of its rectangle in the diagram:

.. code-block:: python

   # short hand for what we see in the
   Buzz /
     print("buzz")
     oven.buzz()

To see how the code in the picture is manifested in our actual code, look at the
``common_features`` callback function that represents this state:

.. code-block:: python
   :emphasize-lines: 10,11-13,17
   :linenos:

   # Legend for mapping code onto diagram:
   # s: draw as shorthand on your diagram
   # f: completely write as code on your diagram
   # g: drawn as a graph element on your diagram
   # !: don't draw this code on your diagram

   @spy_on                             # !
   def common_features(oven, e):       # g
     status = return_status.UNHANDLED  # !
     if(e.signal == signals.Buzz):     # s
       print("buzz")                   # f
       oven.buzz()                     # f
       status = return_status.HANDLED  # !
     else:                             # !
       oven.temp.fun = oven.top        # g
       status = return_status.SUPER    # !
     return status                     # !

We see that when the ``Buzz`` event is reacted to by this function (10), it
prints ``buzz`` (11) then calls the ``oven.buzz()`` code of it's derived
class (12), then returns ``return_status.HANDLED`` (13,17).

When the event processor receives a ``return_status.HANDLED`` it knows it can
stop searching, leaving its source state as it was.   Upon completing its search
the event processor relinquishes control back to its thread, which in turn goes
back to pending on its input queue.

But how did the event processor call the ``common_features`` callback in the
first place?

I'll answer this by first imagining that our oven has settled in the
``toasting`` state when it receives a ``Buzz`` event:

.. image:: _static/ToasterOven_4_Hook.svg
   :target: _static/ToasterOven_4_Hook.pdf
   :align: center

1. The source state **S** and target state **T** are both set to the
   ``toasting`` state before the reaction.  Then the statechart receives the
   ``Buzz`` event from the ``post_fifo`` call.  
   
   The event processor begins its reaction to the ``Buzz`` event by sending the
   callback pointed to by **T** two arguments, a reference to the ToasterOven
   object which is called ``oven`` and ``e`` set to ``Event(signal=signals.Buzz)``.

   The ``toaster`` callback's if-elif logical structure doesn't handle a
   ``Buzz`` event so it passes control to its ``else`` clause.  The ``else``
   clause updates the **T** to the parent state of the ``toasting`` state:
   ``heating``.  The ``toasting`` callback returns ``return_status.SUPER``,
   telling the event processor that the event was not handled.  The event
   processor continues searching.

.. code-block:: python
  :emphasize-lines: 7-9

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = toasting
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating  # T is now set to heating
      status = return_status.SUPER
    return status
   

2. The source state **S** is ``toasting`` and the target state **T** is ``heating``.

   The event processor sends the callback pointed to by **T** two arguments, a
   reference to the ToasterOven object which is called ``oven`` and ``e`` set to
   ``Event(signal=signals.Buzz)``.

   The ``heating`` callback's ``if-elif`` logical structure doesn't handle a
   ``Buzz`` event so it passes control to its ``else`` clause.  The ``else``
   clause updates the **T** to the parent state of the ``heating`` state:
   ``door_closed``.  The ``heating`` callback returns ``return_status.SUPER``,
   telling the event processor that the event was not handled.  The event
   processor continues searching.
   
.. code-block:: python
  :emphasize-lines: 10-12

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed  # T is not set to door_closed
      status = return_status.SUPER
    return status
   
   
3. The source state **S** is ``toasting`` and the target state **T** is
   ``door_closed``. 

   **T** doesn't handle ``Buzz``, **T** is set to ``common_features`` in the
   ``else`` clause. (same logic as above).  The ``door_closed`` callback returns
   return_status.SUPER, telling the event processor that the event was not
   handled. The event processor continues searching.

.. code-block:: python
  :emphasize-lines: 17-19
   
  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    elif(e.signal == signals.Door_Open):
      status = oven.trans(door_open)
    else:
      oven.temp.fun = common_features  # T set to common_features
      status = return_status.SUPER
    return status

4.  The source state **S** is ``toasting`` and the target state **T** is ``common_features``.

   The event processor sends the callback pointed to by **T** two arguments, a
   reference to the ToasterOven object which is called ``oven`` and ``e`` set to
   ``Event(signal=signals.Buzz)``.
   
   The ``common_features`` callback's ``if-elif`` logical structure handles
   a ``Buzz`` event.  It prints "buzz" then calls the ``buzz`` method of the
   oven object, then returns ``return_status.HANDLED``.

   The event processor knows its search is complete.

.. code-block:: python
  :emphasize-lines: 4-7

  @spy_on                           
  def common_features(oven, e):     
    status = return_status.UNHANDLED
    if(e.signal == signals.Buzz):   
      print("buzz")                 
      oven.buzz()                   
      status = return_status.HANDLED
    else:                           
      oven.temp.fun = oven.top      
      status = return_status.SUPER  
    return status                   

5. **T** snaps back to **S**, ``toasting``, the event processor stops searching
   and the RTC process is finished.

Because the ``common_features`` state encloses all of the other states (all
``else`` clauses lead to it), it can hook any ``Buzz`` event from any state.

This is an example of **behavioral inheritance**.

.. include:: i_navigation_4.rst

.. _zero_to_one-can-you-relate-the-buzz-hook-to-the-story4:

**Can you relate the buzz hook to the story?**

**T** represents Tara, the explorer spirit, in our story.

.. raw:: html

   <div class="story">
   
   <p><span class="story-intro">While Tara and Spike</span> were spending time together on an
   upper terrace, someone from our world, put a "Buzz" event into their
   universe's portal.
   </p>

   <p>
   Theo, the god of their underworld (the statechart's thread), immediately notices
   this and pulls the event out of his side of the portal. He casts his gaze up
   into the sky to see Eve, the goddess of heaven (event processor). Eve awakens
   and takes the event from Theo. She looks down on the earth until she sees Spike,
   and beside him Tara.
   </p>

   <p>
   Eve flies done to Tara and gives her the event. Eve says, "Tara, I want you
   to go to the terrace where there is a bartender who knows what to do with
   this event.  Then I want you to go to wherever he tells you to take it. Good
   luck Tara, I believe in you."
   </p>

   <p>
   Tara, upon seeing that there was no bartender named Buzz on her current
   terrace, descends outward and downwards in the bar system.  She does this
   until she is at the lowest bar on the earth, the common_feature.  There she
   see's that there is a bartender named Buzz. she approaches him and asks if he
   knows what to do with the event.   He says, "give me the event, I'll handle it,
   don't worry about it anymore".
   </p>

   <p>
   What Tara and the gods don't know is that Buzz is a member of a subversive
   society called hack-the-humans.  He has some secret code which he will run
   when he is activated by Tara's event and awakened from nonexistence by Theo's
   attention.
   </p>

   <p>
   He carefully pulls his code out of his jacket pocket so nobody can see what
   he is doing, especially Eve, who he considers to be the worst kind of boss --
   a micromanager. He runs "print("oven"); oven.buzz()", smiles, then destroys
   the event.
   </p>

   <p>
   Meanwhile, Tara has gone back up the terrace system to rejoin Spike.  He asks
   her what happened (even though he knows already) and she tells him that the
   bartender handled the event, to which he yells out "hook!" and is happy,
   because he doesn't have to move.  Instead he orders another drink.
   </p>

   <p>
   Theo, the solipsist, sees that the work is done.  He pulls his gaze from his
   universe, freezing it into non-existence, and puts all of his attention back
   onto the portal connecting him with you and me.
   </p>
   </div>

.. include:: i_navigation_4.rst

.. _zero_to_one-the-buzz-seems-like-a-pointless-feature,-what's-going-on4:

**The buzz seems like a pointless feature, what's going on?**

In the next iteration we will tie the buzz event to a timer.  In this iteration
I'm trying to focus on hooks in isolation to make them easier to understand.

.. include:: i_navigation_4.rst

.. _zero_to_one-are-entry-and-exit-events-hooks-too4:

**Are entry and exit events hooks too?**

I can see why you asked this.  It looks like they are, doesn't it? 

We can see this in the ``heating`` callback, which uses both an ENTRY_SIGNAL and
an EXIT_SIGNAL:

.. code-block:: python
  :emphasize-lines: 4, 6, 7, 9, 13
  :linenos:

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

We see that the ``ENTRY_SIGNAL`` is caught by the if statement on line 4 and the
status is set to ``return_status.HANDLED``.  Likewise the ``EXIT_SIGNAL`` is
caught by line 7 and the status is set to ``return_status.HANDLED`` on line 9.

And this looks the same as our hook in the ``common_features`` callback: 

.. code-block:: python
  :emphasize-lines: 4, 7
  :linenos:

  @spy_on                           
  def common_features(oven, e):     
    status = return_status.UNHANDLED
    if(e.signal == signals.Buzz):   
      print("buzz")                 
      oven.buzz()                   
      status = return_status.HANDLED
    else:                           
      oven.temp.fun = oven.top      
      status = return_status.SUPER  
    return status                   

So are the entry and exit events hooks?  

No, they aren't.  If you don't include the ``ENTRY_SIGNAL`` or ``EXIT_SIGNAL``
catches in the ``if-elif`` logical structure of your callback, the entry and
exit events will not propagate outward to be handled by some super state;
instead, these events will just be ignored.

If this weren't the case, you would have to include the ``ENTRY_SIGNAL``,
``EXIT_SIGNAL``, not to mention the ``INIT_SIGNAL`` in every single callback in
your design.  That would be annoying.

.. include:: i_navigation_4.rst

.. _zero_to_one-why-are-you-showing-two-classes-on-the-diagram4:

**Why are you showing two classes on the diagram?**

There are two classes on the diagram to show how we can test our design.

We would like to test the code that is specific for the hardware, on that
hardware and we would like to be able to test the statechart's statemachine
anywhere where Python can run.

.. image:: _static/ToasterOven_4.svg
   :target: _static/ToasterOven_4.pdf
   :align: center

The ToasterOvenMock class is used to confirm that our statechart is working, and
it can be run anywhere where Python can run, you can see the test code that
confirms our design is working :ref:`here <iter4_proof_code>`.

The ToasterOven object would run on the computer inside of our toaster oven.
The ``buzz``, ``light_on``, ``light_off``, ``heater_on`` and ``heater_off``
methods of this ToasterOven object would call out to hardware abstraction layer.

.. include:: i_navigation_4.rst

.. _zero_to_one-what-is-a-hardware-abstraction-layer4:

**What is a hardware abstraction layer?**

The hardware abstraction layer (HAL) is code that separates your software from
the hardware it runs on.

If we were building a real toaster oven, the code would run on a processor
inside of the toaster oven.  If you were making a toaster oven using the
Raspberry Pi 3, this processor would be a quad-core ARM Cortext-A53 CPU.  Any
code running inside of a CPU that is shipped with the product, is called
embedded code, because it's embedded in the processor which is embedded in a
product.

Typically embedded projects, put a layer of software between the code that
provides the features that their customer's want from the code that is needed to
drive the CPU to do what it needs. This software acts as a buttress against the
hardware. It doesn't take a lot of effort to build, and it acts as cheap
insurance for your company. But why would you want to protect your software from
your CPU?  It's not the CPU you have to worry about, it's the price of the CPU
that you have to worry about.

Suppose that Larry Ellison, the guy currently `shaking down
<https://en.wikipedia.org/wiki/Extortion>`_ the Java ecosystem, finds out that a
lot of products have been built using the Raspberry Pi.  He discovers companies
like using the Raspberry Pi, because it is cheap, has a nice stable version of
Linux and is easy to use.  Smelling an opportunity, he buys up the Raspberry Pi
foundation and immediately cranks up the price of the part from $35 to $500.

If we wrote our embedded code using a hardware abstraction layer, we could
quickly port our code over to the BeagleBoard-X15, which has an ARM Cortext-At15
CPU and is also $35.  Sure, it would cost us a bit of money to switch our
hardware and re-write the hardware drivers and part of the HAL, but we would
rather do that than lose $465 per unit.

.. image:: _static/HAL.svg
  :target: _static/HAL.pdf
  :align: center

.. include:: i_navigation_4.rst

.. _zero_to_one-where-is-the-hardware-abstraction-layer-you-listed-in-your-title4:

**Where is the hardware abstraction you listed in your title?**

In our design we present two different classes and an HSM.

.. image:: _static/ToasterOven_4.svg
   :target: _static/ToasterOven_4.pdf
   :align: center

The purpose of the ToasterOvenMock class is to give us the ability to watch how
our statemachine would call out to the HAL as it reacts to different events.

.. image:: _static/ToasterOven_4_With_HAL.svg
   :target: _static/ToasterOven_4_With_HAL.pdf
   :align: center

The ToasterOvenMock object calls out to the ``spy`` instrumentation, which acts
as a fake HAL. This fake HAL can be queried by our test code, to see if a call
to the hardware was made when we needed it to be made.

The ToasterOvenMock object can be tested on your development machine, or on a
continual integration server.  Once its statemachine has been proven to work,
you can confidently attach it to the ToasterOven object running on the computer
embedded in your product.

So, the hardware abstraction described in the title of this iteration, is
provided by the ToasterOvenMock and the code used to test it.

.. include:: i_navigation_4.rst

.. _zero_to_one-in-your-tests,-why-do-you-break-transition-tests-apart-from-calls-to-light_on,-light_off-and-so-on4:

**Why do you break the transition-tests apart from the other tests?**

The transition-tests confirm that we can transition between all of the different parts of the state machine:

.. code-block:: python

  from miros import stripped

  # test helper functions
  def trace_through_all_states():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    time.sleep(0.01)
    return oven.trace()

  # Confirm our state transitions work as designed
  trace_target = """
  [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
  [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
  [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
  [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
  [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
  [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
  [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
  [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
  [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
  """

  with stripped(trace_target) as stripped_target, \
       stripped(trace_through_all_states()) as stripped_trace_result:

    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

They test the statemachine's graphical structure, using the ``trace``
instrumentation.

They don't test the statemachine's hooks or the use of the ToasterOven's methods.

The are pulled out from the other tests, that use the ``spy`` instrumentation to
keep the test code organized into two different ways of thinking:

1. Is the graph working?
2. Is the statechart making the correct calls to the ToasterOven class when they
   need to be made?

.. include:: i_navigation_4.rst

.. _zero_to_one-why-don't-you-just-copy-out-your-spy-output-and-use-it-as-the-test-target4:

**Why don't you just copy out your spy output and use it as the test target?**

You could do this, but then your tests would be testing the event processor too.
I'm trying to show how you can test your code so that it is just coupled to your
design and not to the design of the miros library.  

.. include:: i_navigation_4.rst

.. _zero_to_one-where-did-you-get-your-trace-test-target,-and-what-is-going-on-with-that-stripped-call4:

**Where did you get your trace-test-target, and what is going on with that stripped call?**

I got the trace-test-target by running a live trace on the code. I visually
inspected it and convinced myself that it was working.

The ``stripped`` context manager pulls the time stamp off the front of the trace
strings.  Once you get rid of the timestamps you can compare a new trace output
against and old trace output:

.. code-block:: python

  from miros import stripped

  # test helper functions
  def trace_through_all_states():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    time.sleep(0.01)
    return oven.trace()

  # Confirm our state transitions work as designed
  trace_target = """
  [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
  [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
  [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
  [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
  [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
  [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
  [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
  [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
  [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
  """

  with stripped(trace_target) as stripped_target, \
       stripped(trace_through_all_states()) as stripped_trace_result:

    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)


.. include:: i_navigation_4.rst

.. _zero_to_one-why-don't-you-just-copy-out-your-trace-output-and-use-it-as-a-test-target4:

**Why don't you just copy out your trace output and use it as a test target?**

The timestamps wouldn't match, so your tests would always fail.

.. include:: i_navigation_4.rst

.. _zero_to_one-your-light_on,-light_off-...-tests-seem-pretty-light,-are-you-sure-you-are-testing-these-features4:

**Your light_on, light_off ... tests seem pretty light, are you sure you are testing these features?**

Let's break down one of these tests, while looking at the toaster oven design:

.. image:: _static/ToasterOven.svg
   :target: _static/ToasterOven.pdf
   :align: center

Suppose we want to test that the heater will turn on when we toast or bake
something.  Let's toast something, and run a test:

.. code-block:: python
  :emphasize-lines: 14
  :linenos:

  import re

  # make an oven and put it into a heating state
  def spy_on_heater_on():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
  
  # Confirm the heater turns on in a heating state
  assert re.search(r'heater_on', spy_on_heater_on())

The highlighted code matches the ``heater_on`` string against the output of the
``spy_on_heater_on`` test helper.  If this helper function weren't a part of the
``assert`` statement, it would have outputted this string:

.. code-block:: python
  :emphasize-lines: 19
  :linenos:

  START
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:common_features
  ENTRY_SIGNAL:common_features
  ENTRY_SIGNAL:door_closed
  light_off
  INIT_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:off
  ENTRY_SIGNAL:off
  INIT_SIGNAL:off
  <- Queued:(0) Deferred:(0)
  Toasting:off
  Toasting:door_closed
  EXIT_SIGNAL:off
  SEARCH_FOR_SUPER_SIGNAL:toasting
  SEARCH_FOR_SUPER_SIGNAL:door_closed
  SEARCH_FOR_SUPER_SIGNAL:heating
  ENTRY_SIGNAL:heating
  heater_on
  ENTRY_SIGNAL:toasting
  INIT_SIGNAL:toasting
  <- Queued:(0) Deferred:(0)

So our test code: ``assert re.search(r'heater_on', spy_on_heater_on())``, just
searches through a bunch of lines from our spy instrumentation and returns
``True`` if it sees, ``heater_on``, which it does, so the test passes.

Should we now start our test again and send our statechart a `Bake`` event?  No,
that would be a waste of time.  We tested that our transitions worked, so the
graph is correct: Bake is inside of Heating.  We tested that the entry condition
of the heating state calls out to our ``heater_on()`` code in the ToasterOvenMock, the
formalism of the Harel statecharts says if it happens for one thing inside of a
state, it will happen for all things inside that state.

We are done testing this thing.

The ``light_on``, ``light_off``, ``heater_off`` and ``buzz`` tests follow a very similar pattern.

It is important to note that statecharts pack a lot of feature complexity into a
very small amount of code.  If you over-test your statecharts, your test code
will quickly balloon in size.  So use the statechart formalism to keep your test
suites under control.

.. include:: i_navigation_4.rst

.. _iter5:

Iteration 5: time and one-shots
-------------------------------
Now we have two different software artifacts, the production code from which we
can make our toaster oven and some test code we can use to verify its
state machine.

In this iteration let's add the dimension of time.  Let's have the buzzer sound
20 seconds after a Baking event and 10 seconds after a Toasting event.

.. include:: i_navigation_5.rst

.. _iter5_spec:

Iteration 5 specification
"""""""""""""""""""""""""
The toaster oven spec:

* The toaster oven will have an oven light, which can be turned on and off
* The toaster oven will have a heater, which can be turned on and off
* It will have two different heating modes, baking which can bake a potato
  and toasting which can toast some bread
* The toaster oven should start in the off state
* The toaster can only heat when the door is closed
* The toaster's light should be off when the door is closed
* The toaster should turn on its light when the door is opened
* A customer should be able to open and close the door of our toaster oven
* When a customer closes the door, the toaster oven should go back to behaving
  like it did before
* :dead_spec:`While the toaster oven is in any state the customer should be able to press a
  buzzer which will get the attention of anyone nearby.`
* :new_spec:`The buzzer will sound 20 seconds after a Baking event`
* :new_spec:`The buzzer will sound 10 seconds after a Toasting event`

.. include:: i_navigation_5.rst

.. _iter5_design:

Iteration 5 design
""""""""""""""""""

.. image:: _static/ToasterOven_5.svg
   :target: _static/ToasterOven_5.pdf
   :align: center

.. include:: i_navigation_5.rst

.. _iter5_code:

Iteration 5 code
""""""""""""""""

.. code-block:: python
  :emphasize-lines: 12-13, 15, 18-21, 23-24, 48-49, 51-69, 71-95, 97-128, 130-161, 163-180, 249-254, 271-276
  :linenos:
   
  import re
  import time
  from miros import Event
  from miros import spy_on
  from miros import signals
  from datetime import datetime
  from miros import ActiveObject
  from miros import return_status

  class ToasterOven(ActiveObject):
    
    TOAST_TIME_IN_SEC = 10
    BAKE_TIME_IN_SEC = 20
    
    def __init__(self, name, toast_time_in_sec=None, bake_time_in_sec=None):
      super().__init__(name)
    
      if toast_time_in_sec is None:
        toast_time_in_sec = ToasterOven.TOAST_TIME_IN_SEC
      if bake_time_in_sec is None:
        bake_time_in_sec = ToasterOven.BAKE_TIME_IN_SEC
        
      self.toast_time_in_sec = toast_time_in_sec
      self.bake_time_in_sec = bake_time_in_sec
      self.history = None

    def light_on(self):
      # call to your hardware's light_on driver
      pass

    def light_off(self):
      # call to your hardware's light_off driver
      pass
      
    def heater_on(self):
      # call to your hardware's heater on driver
      pass

    def heater_off(self):
      # call to your hardware's heater off driver
       pass
      
    def buzz(self):
      # call to your hardware's buzzer
      pass
    
  class ToasterOvenMock(ToasterOven):
    def __init__(self, name, toast_time_in_sec=None, bake_time_in_sec=None):
      super().__init__(name, toast_time_in_sec, bake_time_in_sec)
     
    @staticmethod
    def prepend_trace_timestamp(string):
      '''Prepend the trace-style timestamp in front of a string

      **Args**:
         | ``string`` (str): a string you would like timestamped

      **Returns**:
         (string): datetime stamp prepended to input string

      **Example(s)**:
        
      .. code-block:: python

        ToasterOven.prepend_trace_timestamp("example")
        # => [2019-02-04 06:37:04.542346] example

      '''
      return "[{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), string)

    @staticmethod
    def get_100ms_from_timestamp(timestamp_string):
      '''Get the 100ms part of a timestamp provided in the trace style

      **Args**:
         | ``timestamp_string`` (str): string with prepended timestamp

      **Returns**:
         | (string): The first three digits after the seconds decimal point
         | (None): If no match

      **Example(s)**:
        
      .. code-block:: python

        get_my_ms =  "[2019-02-04 06:37:04.542346] example"
        ToasterOven.prepend_trace_timestamp(get_my_ms) # => 542

      '''
      pattern = re.compile(r'\[.+\.([0-9]{3}).+\]')
      try:
        result = pattern.search(timestamp_string).group(1)
      except:
        result = None
      return result

    @staticmethod
    def time_difference(time_1_string, time_2_string, modulo_base=None):
      '''Return the time difference between to ms readings of a timestamp

      **Args**:
         | ``time_1_string`` (str|int): part of a timestamp
         | ``time_2_string`` (str|int): part of a timestamp
         | ``modulo_base`` (int):  defaults to 1000, allows for time raps

      **Returns**:
         (int): (int(time_1_string) - int(time_2_string)) % modulo_base

      **Example(s)**:
        
      .. code-block:: python
        
        # typical usage
        ToasterOvenMock.time_difference('500', '300') #=> 200
        ToasterOvenMock.time_difference('500', '300', modulo_base=1000) #=> 200

        # time wrap
        # time_1_string from 1.010
        # time_2_string from 0.790
        ToasterOvenMock.time_difference('010', '790') #=> 200

      '''
      if modulo_base is None:
        modulo_base = 1000
      time_1 = int(time_1_string)
      time_2 = int(time_2_string)
      diff = time_2 - time_1 if time_1 <= time_2 else (time_2 - time_1) % modulo_base
      return diff

    @staticmethod
    def instrumentation_line_of_match(spy_or_trace, string):
      '''Get the line from a instrumentation collection

      **Args**:
         | ``spy_or_trace`` (str|list): instrumentation output
         | ``string`` (str): thing to search for in the instrumentation output

      **Returns**:
         (str): part of the instrumentation that matches the string

      **Example(s)**:
        
      .. code-block:: python
         
        spy_of_trace = """
          [2019-02-09 10:50:07.784989] [oven] e->start_at() top->off
          [2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting"""

        ToasterOvenMock.instrumentation_line_of_match(
          spy_of_trace, "Toasting") 
        # => '[2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting'

      '''
      result = None
      i_list = spy_or_trace.split("\n") if type(spy_or_trace) is str else spy_or_trace
      pattern = re.compile(string)
      for line in i_list:
        if pattern.search(line):
          result = line
          break
      return result

    def scribble(self, string):
      '''prepend a scribble string with the trace instrumentation style timestamp

      **Args**:
         | ``string`` (str): String to add to the scribble

      **Example(s)**:
        
      .. code-block:: python

         oven = ToasterOvenMock(name='oven')

         # calls ActiveObject's scribble with something like:
         # "[2019-02-09 10:50:07.785844] buzz"
         oven.scribble("buzz") 

      '''
      super().scribble(ToasterOvenMock.prepend_trace_timestamp(string))
      
    def light_on(self):
      self.scribble("light_on")

    def light_off(self):
      self.scribble("light_off")

    def heater_on(self):
      self.scribble("heater_on")

    def heater_off(self):
      self.scribble("heater_off")
      
    def buzz(self):
      self.scribble("buzz")
      
      
  @spy_on
  def common_features(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Buzz):
      oven.buzz()
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    elif(e.signal == signals.Door_Open):
      status = oven.trans(door_open)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = baking
      oven.post_lifo(
        Event(signal=signals.Buzz),
        times=1,
        period=oven.bake_time_in_sec,
        deferred=True
      )
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.cancel_events(
        Event(signal=signals.Buzz)
      )
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = toasting
      oven.post_lifo(
        Event(signal=signals.Buzz),
        times=1,
        period=oven.toast_time_in_sec,
        deferred=True
      )
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.cancel_events(
        Event(signal=signals.Buzz)
      )
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = off
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def door_open(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_on()
    elif(e.signal == signals.Door_Close):
      status = oven.trans(oven.history)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status

.. include:: i_navigation_5.rst

.. _iter5_proof:

Iteration 5 proof
"""""""""""""""""

.. include:: i_navigation_5.rst

Here are our test helpers

.. code-block:: python
  :emphasize-lines: 72-92, 94-114
  :linenos:

  import re
  from miros import stripped
  
  def trace_through_all_states():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    time.sleep(0.01)
    return oven.trace()
  
  def spy_on_light_on():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door to turn on the light
    oven.post_fifo(Event(signal=signals.Door_Open))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
  
  def spy_on_light_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
    
  def spy_on_buzz():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Send the buzz event
    oven.post_fifo(Event(signal=signals.Buzz))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
  
  def spy_on_heater_on():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(0.02)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
  
  def spy_on_heater_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    oven.clear_spy()
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
  
  def test_toaster_buzz_one_shot_timing():
    # set toasting time to 100 ms
    oven = ToasterOvenMock(name="oven", toast_time_in_sec=0.100)
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
  
    time.sleep(0.106)  
  
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Toasting")
    toasting_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
  
    spy_line = ToasterOvenMock.instrumentation_line_of_match(oven.spy(), "buzz")
    buzz_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(spy_line))
  
    delay_in_ms = ToasterOvenMock.time_difference(toasting_time_ms, buzz_time_ms)
  
    # allow for 5 milliseconds of jitter (needed in jupyter)
    try:
      assert(100 <= delay_in_ms <= 105)
    except:
      print(delay_in_ms)
  
  def test_baking_buzz_one_shot_timing():
    # set bake time to 200 ms
    oven = ToasterOvenMock(name="oven", bake_time_in_sec=0.200)
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Baking))
  
    time.sleep(0.206)
  
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Baking")
    baking_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
  
    spy_line = ToasterOvenMock.instrumentation_line_of_match(oven.spy(), "buzz")
    buzz_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(spy_line))
  
    delay_in_ms = ToasterOvenMock.time_difference(baking_time_ms, buzz_time_ms)
  
    # allow for 5 milliseconds of jitter (needed in jupyter)
    try:
      assert(200 <= delay_in_ms <= 205)
    except:
      print(delay_in_ms) 

Calling our test helper functions to prove our design works:

.. code-block:: python
  :emphasize-lines: 38-40
  :linenos:

  import re
  from miros import stripped

  # Confirm our graph's structure
  trace_target = """
  [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
  [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
  [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
  [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
  [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
  [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
  [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
  [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
  [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
  """

  with stripped(trace_target) as stripped_target, \
       stripped(trace_through_all_states()) as stripped_trace_result:
    
    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

  # Confirm the our statemachine is triggering the methods we want when we want them
  assert re.search(r'light_off', spy_on_light_off())

  # Confirm our light turns on
  assert re.search(r'light_on', spy_on_light_on())

  # Confirm the heater turns on
  assert re.search(r'heater_on', spy_on_heater_on())

  # Confirm the heater turns off
  assert re.search(r'heater_off', spy_on_heater_off())

  # Confirm our buzzer works
  assert re.search(r'buzz', spy_on_buzz())

  # Confirm time features work
  test_toaster_buzz_one_shot_timing()
  test_baking_buzz_one_shot_timing()


.. _iter5_questions:

Iteration 5 questions
"""""""""""""""""""""
* :ref:`What happens if they don't take out there food after a buzz rings? <zero_to_one-what-happens-if-they-don't-take-out-there-food-after-a-buzz-rings5>`
* :ref:`What is a one shot? <zero_to_one-what-is-a-one-shot5>`
* :ref:`How does a one shot work? <zero_to_one-how-does-a-one-shot-work5>`
* :ref:`Why do you cancel the events in the exit states? <zero_to_one-why-do-you-cancel-the-events-in-the-exit-states5>`
* :ref:`Can you relate a one shot to the story? <zero_to_one-can-you-relate-a-one-shot-to-the-story5>`
* :ref:`What is the remind pattern? <zero_to_one-what-is-the-remind-pattern5>`
* :ref:`Why did you turn ToasterOvenMock into a subclass of ToasterOven? <zero_to_one-why-did-you-turn-toasterovenmock-into-a-subclass-of-toasteroven5>`
* :ref:`Why do you have docstrings in the test code and not elsewhere? <zero_to_one-why-do-you-have-docstrings-in-the-test-code-and-not-elsewhere5>`
* :ref:`What is jitter? <zero_to_one-what-is-jitter5>`
* :ref:`Why is your tolernance of jitter so high? <zero_to_one-why-is-your-tolernance-of-jitter-so-high5>`
* :ref:`How can I reduce the jitter? <zero_to_one-how-can-i-reduce-the-jitter5>`


.. _zero_to_one-what-happens-if-they-don't-take-out-there-food-after-a-buzz-rings5:

**What happens if they don't take out there food after a buzz rings?**

The toaster oven would continue to cook.  This will be fixed in the next iteration.

.. include:: i_navigation_5.rst

.. _zero_to_one-what-is-a-one-shot5:

**What is a one shot?**

It is the code that issues an event to the statechart at a predetermined time in
the future.

Here is an example, when the following code is run, a ``Buzz`` event will be
sent to the statechart in 10 seconds:

.. code-block:: python

  # send an Buzz event to this chart, 10 seconds from now
  oven.post_fifo(
    Event(signal=signal.Buzz),
    times=1,
    period=10.0,
    deferred=True)

An event which is issued by a one shot looks just like any other event that has
been received from outside of the statechart.  Our design already accomodates
Buzz events, they are handled by the ``common_features`` state.  

.. include:: i_navigation_5.rst

.. _zero_to_one-how-does-a-one-shot-work5:

**How does a one shot work?**

Any ``post_fifo`` or ``post_lifo`` call with the ``period`` argument set, spawns
another python daemonic-thread with an internal timer.  It will issue as many
events as indicated by the ``times`` argument; when it has completed its work,
the thread will stop running and python will garbage collect it.

.. note::

  If the ``times`` argument is set to zero, the ``post_fifo`` or ``post_lifo``
  will continue to post events until the program is stopped.

.. include:: i_navigation_5.rst

.. _zero_to_one-why-do-you-cancel-the-events-in-the-exit-states5:

**Why do you cancel the events in the exit states?**

The deferred one shot pushes a behavior into the future.  It's event will arrive
as if it was posted from outside of the chart, with no regard for the chart's
current state.  This can lead to some confusing behavior.

I'll illustrate this with an example.  Suppose we didn't cancel our one-shot
events upon leaving either the baking or toasting states:

.. image:: _static/ToasterOven_5_without_cancel.svg
  :target: _static/ToasterOven_5_without_cancel.pdf
  :align: center

Imagine that we toast something for 5 seconds, then quickly open and close the
door, then immediately press the bake button.

5 seconds after this moment we would hear a buzz, then 10 seconds after that,
then 20 seconds after that.

Without canceling our one shot, the diagram's fidelity is reduced, because you
can't just see the behavior, instead you have to run a full simulation in your
head.

However, if you cancel your one-shot upon exiting the state from which they were
created, you will avoid these strange behaviours.  When you look at the baking
or toasting states, you will know that if the unit remains in these states for
their respective one-shot times, the oven will behave as you expect it to.  

.. image:: _static/ToasterOven.svg
  :target: _static/ToasterOven.pdf
  :align: center

Let's re-imagine our scenario with the one-shot cancellations in the exit states
of baking and toasting.  We toast something for 5 seconds, open the door, close
the door, then immediately press the bake button.  The buzzer will sound in 20
seconds.

Typically, I cancel deferred events when exiting the states from which they were
initiated.  If you see a diagram where this isn't the case; it might be a design 
bug, or at least an indication that you have to think harder to understand what
is going on.

In the next iteration I will break this best-practice to make a different point.

.. include:: i_navigation_5.rst

.. _zero_to_one-can-you-relate-a-one-shot-to-the-story5:

**Can you relate a one shot to the story?**

One-shot triggers and their cancellations can be initiated by any human when
they talk to Spike or Tara.

The one shot is a kind of event gun (``post_fifo`` or ``post_lifo``) which
invents a small universe then tears a portal to it.  Through this portal, an
event is placed in suspension for a given amount of time relative to our
universe (a statechart has no such time dimension).  The portal closes and the
universe (holding the event) persists for the duration of time specified by the
period argument.  Once this time has elapsed, the event attaches itself into the
portal that Theo is watching and the temporary universe is destroyed.
 
When Theo receives such an event he marvels at it, believing that it came from
some other universe, which is true, but he has no idea that it was initiated by
one of the humans in his own domain.  He treats it as he would any other event.

If the one shot was initiated using a ``post_fifo`` call, the event
will be placed at the last location available in the deque.  

.. image:: _static/ToasterOven_5_Theo_1.svg
  :target: _static/ToasterOven_5_Theo_1.pdf
  :align: center

If the one shot was initiated by a ``post_lifo`` call, the event
will barge its way to the front of the deque, shifting all other items to the
right by one.  Such a call will put the event immediately in front of Theo once
its time has elapsed.

.. image:: _static/ToasterOven_5_Theo_2.svg
  :target: _static/ToasterOven_5_Theo_2.pdf
  :align: center

``cancel_events`` can be thought of as a gun that shoots bullets that destroys
bullets shot by other guns.  A call to ``cancel_events`` will tear into the
great beyond, looking for all of the one-shots that haven't timed-out yet.  If
the event name of the one shot matches that which was fed to the
``cancel_events`` call, that universe is annihilated before it's event can be
presented Theo.

.. include:: i_navigation_5.rst

.. _zero_to_one-what-is-the-remind-pattern5:

**What is the remind pattern?**

When you invent an event within a statechart, then post it back into the same
statechart, it is called the :ref:`reminder pattern <patterns-reminder>`.

.. include:: i_navigation_5.rst

.. _zero_to_one-why-did-you-turn-toasterovenmock-into-a-subclass-of-toasteroven5:

**Why did you turn ToasterOvenMock into a subclass of ToasterOven?**

A ToasterOvenMock object is intended to test a ToasterOven and its attached
statemachine.

In this iteration we introduced the ``toast_time_in_sec`` and
``bake_time_in_sec`` attributes to the ToasterOven, and they are referenced within the
statemachine.  This means that the ToasterOvenMock needs them too.

To avoid repeating myself, by defining these attributes in both classes,
ToasterOvenMock inherits from the ToasterOven so I get these attributes
automatically.

.. include:: i_navigation_5.rst

.. _zero_to_one-why-do-you-have-docstrings-in-the-test-code-and-not-elsewhere5:

**Why do you have docstrings in the test code and not elsewhere?**

I found the testing code a bit confusing so I added some documentation.  You can
see that I use some reStructuredText in my Docstring which adds some clutter.

When docstrings are written in this manner, then parsed and turned into
html, they will produce a document that looks like `this
<https://aleph2c.github.io/spaced/repetition.html#module-repetition>`_

.. include:: i_navigation_5.rst

.. _zero_to_one-what-is-jitter5:

**What is jitter?**

"Jitter is the deviation from true periodicity of a presumable periodic signal,
often in relation to a reference clock signal". -- Wikipedia

In our test code we try to produce two signals, one with a period of 100 ms and
the other 200 ms.  The signals only run once, but we still see evidence of
jitter, because they arrive late.

We account for this lateness in our test code by providing some tolerance:

.. code-block:: python

   assert(100 <= delay_in_ms <= 105)
   # ..
   assert(200 <= delay_in_ms <= 205)

.. note::

  Our jitter is asymetric, an event will never arrive early; we slip into the
  future.

.. include:: i_navigation_5.rst

.. _zero_to_one-why-is-your-tolernance-of-jitter-so-high5:

**Why is your tolernance of jitter so high?**

I am testing this documentation using Jupyter (running in a web browser) which
is talking to a CPython, Python implementation, which is running within the
Windows Subsystem for Linux (wsl).  The Jupyter web interface communicates with the
Cpython interpreter using Json over the ZeroMQ messaging protocol.

The ``miros`` library uses Python threads, which is to say a single process on
one CPU, that is shared between the threads.  To avoid concurrency problems --
deadlocks, priority-inversion etc, python uses something called the global
interpreter lock (GIL).

So there is a lot of technology between my demonstration-code and the actual CPU
and its timers.  As a python programmer using Threads I really don't get to have
access to the precise time features offered by my computer; especially if I am
running code in Jupyter.

If you need tight time tolerances consider using the `qp framework
<https://www.state-machine.com/>`_ without an OS.

.. include:: i_navigation_5.rst

.. _zero_to_one-how-can-i-reduce-the-jitter5:

**How can I reduce the jitter?**

Well, don't run your program in Jupyter for one.  Consider using the `qp
framework <https://www.state-machine.com/>`_ or its derived `farc framework
<https://github.com/dwhall/farc>`_ in python.

In our design, we don't really care about the 2-5 ms latency, because it is
0.02%-0.05% of the 10 second delay, and 0.01%-0.025% percent of the 20 second
delay.

Our customers won't notice if they have to wait an additional 5 ms to hear their
toaster oven buzz.

.. include:: i_navigation_5.rst

.. _iter6:

Iteration 6: Multi-Shot events and Payloads
-------------------------------------------
So far we have built a very basic toaster oven.

In this iteration we will add two new features:

* The oven will buzz once when it is almost done.
* When the oven has finished cooking, it will buzz twice and turn off.

.. include:: i_navigation_6.rst

.. _iter6_spec:

Iteration 6 specification
"""""""""""""""""""""""""

Iteration 6 specification:

The toaster oven spec:

* The toaster oven will have an oven light, which can be turned on and off
* The toaster oven will have a heater, which can be turned on and off
* It will have two different heating modes, baking which can bake a potato
  and toasting which can toast some bread
* The toaster oven should start in the off state
* The toaster can only heat when the door is closed
* The toaster's light should be off when the door is closed
* The toaster should turn on its light when the door is opened
* A customer should be able to open and close the door of our toaster oven
* When a customer closes the door, the toaster oven should go back to behaving
  like it did before
* :dead_spec:`The buzzer will sound 10 seconds after a Toasting event`
* :dead_spec:`The buzzer will sound 20 seconds after a Baking event`
* :new_spec:`The toasting mode will cook for 10 seconds, then turn off`
* :new_spec:`The baking mode will cook for 20 seconds, then turn off`
* :new_spec:`One buzz means get ready, there is 1 second left`
* :new_spec:`Two buzzes means something has finished cooking`
* :new_spec:`Three buzzes means the white walkers are coming`

.. _iter6_design:

Iteration 6 design
""""""""""""""""""
If you can't see the design in your browser, click on the diagram to look at the
pdf file.

.. image:: _static/ToasterOven_6.svg
    :target: _static/ToasterOven_6.pdf
    :align: center

The entry condition of the baking state creates two deferred one-shot events,
``Get_Ready`` and ``Done``.  Each of these events contain a buzz specification
as a payload.

When the ``Get_Ready`` event is received by the statechart, it creates a ``Buzz``
one-shot which fires immediately.

When the ``Done`` event is received, it creates a ``Buzz`` multishot (two
buzzes) which begins firing immediately, then the oven turns off.

The toasting state behaves exactly like the baking state, except it has a
different cook time.  To avoid having code repetition, the code that is common
between the ``baking`` and ``toasting`` states was pulled out of the
statemachine and into the ``cook_time`` method of the ToasterOven.

Here is a timing diagram describing how the statechart timing relates to the
hardware timing:

.. image:: _static/ToasterOven_6_Timing_Diagram.svg
    :target: _static/ToasterOven_6_Timing_Diagram.pdf
    :align: center

.. include:: i_navigation_6.rst


.. _iter6_code:

Iteration 6 code
""""""""""""""""

.. code-block:: python
  :emphasize-lines: 9, 11-12, 18-19, 24, 25 ,33-36, 65-88, 294-305, 319, 335, 338, 339
  :linenos:

  import re
  import time
  from miros import Event
  from miros import spy_on
  from miros import signals
  from datetime import datetime
  from miros import ActiveObject
  from miros import return_status
  from collections import namedtuple

  BuzzSpec = namedtuple(
    "BuzzSpec", ['buzz_times'])

  class ToasterOven(ActiveObject):
    
    TOAST_TIME_IN_SEC = 10
    BAKE_TIME_IN_SEC = 20
    PRE_TIME_SEC = 1
    DONE_BUZZ_PERIOD_SEC = 0.5
    
    def __init__(self, name, 
      toast_time_in_sec=None,
      bake_time_in_sec=None,
      get_ready_sec=None,
      done_buzz_period_sec=None):

      super().__init__(name)
    
      if toast_time_in_sec is None:
        toast_time_in_sec = ToasterOven.TOAST_TIME_IN_SEC
      if bake_time_in_sec is None:
        bake_time_in_sec = ToasterOven.BAKE_TIME_IN_SEC
      if get_ready_sec is None:
        get_ready_sec = ToasterOven.PRE_TIME_SEC
      if done_buzz_period_sec is None:
        done_buzz_period_sec = ToasterOven.DONE_BUZZ_PERIOD_SEC
        
      self.toast_time_in_sec = toast_time_in_sec
      self.bake_time_in_sec = bake_time_in_sec
      self.get_ready_sec = get_ready_sec
      self.done_buzz_period_sec = done_buzz_period_sec
      self.history = None

    def light_on(self):
      # call to your hardware's light_on driver
      pass

    def light_off(self):
      # call to your hardware's light_off driver
      pass
      
      
    def heater_on(self):
      # call to your hardware's heater on driver
      pass

    def heater_off(self):
      # call to your hardware's heater off driver
       pass
      
    def buzz(self):
      # call to your hardware's buzzer
      pass

    def cook_time(self, time_in_sec):
      '''Produce ``Get_Ready`` and ``Done`` one-shot events with their respect Buzz
         specifications.

      **Note**:
         This code is used in both the baking and toasting states, so it was moved
         into the ToasterOven class to avoid repeating code in the statemachine.

      **Args**:
         | ``time_in_sec`` (float): the cooking time in seconds
      '''
      get_ready_sec = time_in_sec - self.get_ready_sec

      self.post_fifo(
        Event(signal=signals.Get_Ready, payload=BuzzSpec(buzz_times=1)),
        times=1,
        period=get_ready_sec,
        deferred=True)

      self.post_fifo(
        Event(signal=signals.Done, payload=BuzzSpec(buzz_times=2)),
        times=1,
        period=time_in_sec,
        deferred=True)

    
  class ToasterOvenMock(ToasterOven):

    def __init__(self, 
      name, 
      toast_time_in_sec=None,
      bake_time_in_sec=None,
      get_ready_sec=None,
      done_buzz_period_sec=None):

      super().__init__(name,
        toast_time_in_sec,
        bake_time_in_sec,
        get_ready_sec,
        done_buzz_period_sec)
     
    @staticmethod
    def prepend_trace_timestamp(string):
      '''Prepend the trace-style timestamp in front of a string

      **Args**:
         | ``string`` (str): a string you would like timestamped

      **Returns**:
         (string): datetime stamp prepended to input string

      **Example(s)**:
        
      .. code-block:: python

        ToasterOven.prepend_trace_timestamp("example")
        # => [2019-02-04 06:37:04.542346] example

      '''
      return "[{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), string)

    @staticmethod
    def get_100ms_from_timestamp(timestamp_string):
      '''Get the 100ms part of a timestamp provided in the trace style

      **Args**:
         | ``timestamp_string`` (str): string with prepended timestamp

      **Returns**:
         | (string): The first three digits after the seconds decimal point
         | (None): If no match

      **Example(s)**:
        
      .. code-block:: python

        get_my_ms =  "[2019-02-04 06:37:04.542346] example"
        ToasterOven.prepend_trace_timestamp(get_my_ms) # => 542

      '''
      pattern = re.compile(r'\[.+\.([0-9]{3}).+\]')
      try:
        result = pattern.search(timestamp_string).group(1)
      except:
        result = None
      return result

    @staticmethod
    def time_difference(time_1_string, time_2_string, modulo_base=None):
      '''Return the time difference between to ms readings of a timestamp

      **Args**:
         | ``time_1_string`` (str|int): part of a timestamp
         | ``time_2_string`` (str|int): part of a timestamp
         | ``modulo_base`` (int):  defaults to 1000, allows for time raps

      **Returns**:
         (int): (int(time_1_string) - int(time_2_string)) % modulo_base

      **Example(s)**:
        
      .. code-block:: python
        
        # typical usage
        ToasterOvenMock.time_difference('500', '300') #=> 200
        ToasterOvenMock.time_difference('500', '300', modulo_base=1000) #=> 200

        # time wrap
        # time_1_string from 1.010
        # time_2_string from 0.790
        ToasterOvenMock.time_difference('010', '790') #=> 200

      '''
      if modulo_base is None:
        modulo_base = 1000
      time_1 = int(time_1_string)
      time_2 = int(time_2_string)
      diff = time_2 - time_1 if time_1 <= time_2 else (time_2 - time_1) % modulo_base
      return diff

    @staticmethod
    def instrumentation_line_of_match(spy_or_trace, string):
      '''Get the line from a instrumentation collection

      **Args**:
         | ``spy_or_trace`` (str|list): instrumentation output
         | ``string`` (str): thing to search for in the instrumentation output

      **Returns**:
         (str): part of the instrumentation that matches the string

      **Example(s)**:
        
      .. code-block:: python
         
        spy_of_trace = """
          [2019-02-09 10:50:07.784989] [oven] e->start_at() top->off
          [2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting"""

        ToasterOvenMock.instrumentation_line_of_match(
          spy_of_trace, "Toasting") 
        # => '[2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting'

      '''
      result = None
      i_list = spy_or_trace.split("\n") if type(spy_or_trace) is str else spy_or_trace
      pattern = re.compile(string)
      for line in i_list:
        if pattern.search(line):
          result = line
          break
      return result

    def scribble(self, string):
      '''prepend a scribble string with the trace instrumentation style timestamp

      **Args**:
         | ``string`` (str): String to add to the scribble

      **Example(s)**:
        
      .. code-block:: python

         oven = ToasterOvenMock(name='oven')

         # calls ActiveObject's scribble with something like:
         # "[2019-02-09 10:50:07.785844] buzz"
         oven.scribble("buzz") 

      '''
      super().scribble(ToasterOvenMock.prepend_trace_timestamp(string))
      
    def light_on(self):
      self.scribble("light_on")

    def light_off(self):
      self.scribble("light_off")

    def heater_on(self):
      self.scribble("heater_on")

    def heater_off(self):
      self.scribble("heater_off")
      
    def buzz(self):
      if self.live_spy == False:
        output = ToasterOvenMock.prepend_trace_timestamp("buzz")
        print(output)
      self.scribble("buzz")
      
      
  @spy_on
  def common_features(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.Buzz):
      oven.buzz()
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.Baking):
      status = oven.trans(baking)
    elif(e.signal == signals.Toasting):
      status = oven.trans(toasting)
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    elif(e.signal == signals.Door_Open):
      status = oven.trans(door_open)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heater_on()
      status = return_status.HANDLED
    elif(e.signal == signals.Get_Ready):
      oven.post_fifo(Event(signal=signals.Buzz),
        times=e.payload.buzz_times,
        period=oven.done_buzz_period_sec,
        deferred=False)
      status = return_status.HANDLED
    elif(e.signal == signals.Done):
      oven.post_fifo(Event(signal=signals.Buzz),
        times=e.payload.buzz_times,
        period=oven.done_buzz_period_sec,
        deferred=False)
      status = oven.trans(off)
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heater_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = baking
      oven.cook_time(oven.bake_time_in_sec)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.cancel_events(Event(signal=signals.Done))
      oven.cancel_events(Event(signal=signals.Get_Ready))
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = toasting
      oven.cook_time(oven.toast_time_in_sec)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.cancel_events(Event(signal=signals.Done))
      oven.cancel_events(Event(signal=signals.Get_Ready))
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def off(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.history = off
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def door_open(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.light_on()
    elif(e.signal == signals.Door_Close):
      status = oven.trans(oven.history)
    else:
      oven.temp.fun = common_features
      status = return_status.SUPER
    return status

  if __name__ == '__main__':

    # reduce our time delays so we don't have 
    # to wait while we are testing
    oven = ToasterOvenMock(
      name="oven",
      toast_time_in_sec=1.0,
      bake_time_in_sec=2.0,
      get_ready_sec=0.10,
      done_buzz_period_sec=0.05)

    oven.live_spy = True

    # start our oven in the door_closed state
    oven.start_at(door_closed)

    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    
    # Let it finish toasting
    time.sleep(2)

    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))

    # let it finish backing
    time.sleep(3)


.. include:: i_navigation_6.rst

.. _iter6_proof:

Iteration 6 proof
"""""""""""""""""

Our design hasn't changed that much, but is the part that we changed working?

.. image:: _static/ToasterOven_6.svg
    :target: _static/ToasterOven_6.pdf
    :align: center

Let's give it some time parameters, turn on the trace and look at the output.
To avoid a long feedback cycle we will test in milliseconds.

.. code-block:: python
  :emphasize-lines: 10,11
  :linenos:

  toast_time = 0.1  # 100 ms
  bake_time = 0.2  # 200 ms
  get_ready_sec = 0.05  # 50 ms
  done_buzz_period_sec = 0.01  # 10 ms

  oven = ToasterOvenMock(
    name="oven",
    toast_time_in_sec=toast_time,
    bake_time_in_sec=bake_time,
    get_ready_sec=get_ready_sec,
    done_buzz_period_sec=done_buzz_period_sec)
  oven.live_trace = True
  oven.start_at(off)
  oven.post_fifo(Event(signal=signals.Toasting))

This results in something like this:

.. code-block:: python

  [2019-02-17 11:32:54.844655] [oven] e->start_at() top->off
  [2019-02-17 11:32:54.845782] [oven] e->Toasting() off->toasting
  [2019-02-17 11:32:54.897128] buzz
  [2019-02-17 11:32:54.948089] [oven] e->Done() toasting->off
  [2019-02-17 11:32:54.948708] buzz
  [2019-02-17 11:32:54.958674] buzz

These results match the "Statchmachine Timing" characteristics of our timing
diagram:

.. image:: _static/ToasterOven_6_Timing_Diagram.svg
    :target: _static/ToasterOven_6_Timing_Diagram.pdf
    :align: center

Here is a sequence diagram of the output:

.. code-block:: text

   [Statechart: oven]
         top            off         toasting
          +--start_at()->|              |
          |     (1)      |              |
          |              +--Toasting()->|
          |              |     (2)      |
          |              |              | buzz(3)
          |              |              | 
          |              +<---Done()----| 
          |              |     (4)      | buzz(5)
          |              |              | buzz(6)
          |              |              |

1. Starting the oven
2. Sending the toasting event at 845 ms
3. Get ready buzz event at 897 ms. 897, roughly (845 + 100-50)
4. The toasting is Done at 948 ms. 948, roughly (845 + 100)
5. First off buzz event at 949 ms, telling the user the oven is done cooking. 949, roughly (845 + 100)
6. Second off buzz event at 959 ms, telling the user the oven is done cooking. 959, roughly (845 + 100 + 10)

Our preliminary check tells us things are working.

Here is a complete test:

.. code-block:: python
  :emphasize-lines: 72-147, 183-184
  :linenos:

  import re
  from miros import stripped

  def trace_through_all_states():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    time.sleep(0.01)
    return oven.trace()

  def spy_on_light_on():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door to turn on the light
    oven.post_fifo(Event(signal=signals.Door_Open))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_light_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
    
  def spy_on_buzz():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Send the buzz event
    oven.post_fifo(Event(signal=signals.Buzz))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_heater_on():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(0.02)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_heater_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    oven.clear_spy()
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def test_buzz_timing():
    # Test in the range of ms so we don't have to wait around for results
    toast_time, bake_time = 0.1, 0.2
    get_ready_sec = 0.01
    done_buzz_period_sec = 0.03

    oven = ToasterOvenMock(
      name="oven",
      toast_time_in_sec=toast_time,
      bake_time_in_sec=bake_time,
      get_ready_sec=get_ready_sec,
      done_buzz_period_sec=done_buzz_period_sec)

    # start our oven in the door_closed state
    oven.start_at(door_closed)

    # Buzz timing testing specifications and helper functions
    TS = namedtuple('TargetAndToleranceSpec', ['desc', 'offset', 'tolerance'])

    def make_test_spec(cook_time_sec, get_ready_sec, done_buzz_period_sec, tolernance_in_ms=3):
      "create as specification where define everything in ms"
      ts = [
        TS(desc="get ready buzz",
          offset=1000*(cook_time_sec-get_ready_sec),
          tolerance=tolernance_in_ms),
        TS(desc="first done buzz" , 
          offset=1000*(cook_time_sec), 
          tolerance=tolernance_in_ms),
        TS(desc="second done buzz", 
          offset=1000*(cook_time_sec+done_buzz_period_sec), 
          tolerance=tolernance_in_ms)]
      return ts

    def test_buzz_events(test_type, start_time, spec, buzz_times):
      for (desc, offset, tolerance), buzz_time in zip(spec, buzz_times):

        # only keep track of ms, allow for wrapping of time
        bottom_bound = (start_time+offset-tolerance) % 1000
        top_bound = (start_time+offset+tolerance) % 1000
        
        # allow for wrapping of time
        if bottom_bound > top_bound:
          bottom_bound -= 1000
        try:
          assert(bottom_bound <= float(buzz_time) <= top_bound)
        except:
          # if you land here try increasing your tolerance
          print("FAILED: testing {} {}".format(test_type, desc))
          print("{} <= {} <= {}".format(bottom_bound, buzz_time, top_bound))

    toasting_buzz_test_spec = make_test_spec(toast_time, get_ready_sec, done_buzz_period_sec)

    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(1)
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Toasting")
    toasting_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
    buzz_times = [int(ToasterOvenMock.get_100ms_from_timestamp(line)) for
                  line in re.findall(r'\[.+\] buzz', "\n".join(oven.spy()))]
    test_buzz_events('toasting', toasting_time_ms, toasting_buzz_test_spec, buzz_times)

    # clear the spy and trace logs for another test
    oven.clear_spy()
    oven.clear_trace()

    baking_buzz_test_spec = make_test_spec(bake_time, get_ready_sec, done_buzz_period_sec)

    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    time.sleep(1)
    oven.post_fifo(Event(signal=signals.Baking))
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Baking")
    baking_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
    buzz_times = [int(ToasterOvenMock.get_100ms_from_timestamp(line)) for
                  line in re.findall(r'\[.+\] buzz', "\n".join(oven.spy()))]
    test_buzz_events('baking', baking_time_ms, baking_buzz_test_spec, buzz_times)

  # Confirm our graph's structure
  trace_target = """
  [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
  [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
  [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
  [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
  [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
  [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
  [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
  [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
  [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
  """

  with stripped(trace_target) as stripped_target, \
       stripped(trace_through_all_states()) as stripped_trace_result:
    
    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

  # Confirm the our statemachine is triggering the methods we want when we want them
  assert re.search(r'light_off', spy_on_light_off())

  # Confirm our light turns on
  assert re.search(r'light_on', spy_on_light_on())

  # Confirm the heater turns on
  assert re.search(r'heater_on', spy_on_heater_on())

  # Confirm the heater turns off
  assert re.search(r'heater_off', spy_on_heater_off())

  # Confirm our buzzer works
  assert re.search(r'buzz', spy_on_buzz())

  # Confirm the buzzer timing features are working
  test_buzz_timing()


.. include:: i_navigation_6.rst

.. _iter6_questions:

Iteration 6 questions
"""""""""""""""""""""

* :ref:`Do you really test things like this? <zero_to_one-do-you-really-test-things-like-this6>`
* :ref:`Do you typically use timing diagrams with your design? <zero_to_one-do-you-typically-use-timing-diagrams-with-your-design6>`
* :ref:`How do you generate the ASCII sequence diagrams from the trace? <zero_to_one-how-do-you-generate-the-ascii-sequence-diagrams-from-the-trace6>`
* :ref:`What is a payload? <zero_to_one-what-is-a-payload6>`
* :ref:`Why do you use a namedtuple to make a payload? <zero_to_one-why-do-you-use-a-namedtuple-to-make-a-payload6>`
* :ref:`Why should payloads be immutable? <zero_to_one-why-should-payloads-be-immutable6>`
* :ref:`Can you explain the timing diagram? <zero_to_one-can-you-explain-the-timing-diagram6>`

.. _zero_to_one-do-you-really-test-things-like-this6:

**Do you really test things like this?**

No.  I mostly rely on the spy and trace instrumentation to determine if a design
is working or not.

The graph confirmation and mock tests seem like a good idea to me; these can be
added to a regression test without a lot of effort.  They won't slow down
development progress and they aren't tightly coupled to the specifics of the
implementation.

This can not be said for the timing tests.  They are expensive, because you need
to:

* parameterize your timing features so you can reduce the time it takes to make
  the test. (complexity is added to make the system testable)
* add tunable tolerancing to account for task jitter 
* manage time wrapping when testing in the millisecond domain
* explain how the test works to a maintenance developer in your docstrings.

The burden of carrying these tests may outweigh the benefits they offer.

It is a worthwhile investment to pay the high cost of such rigorous regression
tests, when it is difficult to decouple a system for debugging purposes.  It
also makes sense when you can't see your code with a debugger, like if
you are meta-programming with Ruby.  As far as I can tell the `test everything
ethos came from this community
<https://www.youtube.com/watch?time_continue=3&v=YX3iRjKj7C0>`_.

But if you are using the statechart architectural pattern, it is trivial to
build up an elaborate design using small and knowable parts, each part having
its own diagram and rich instrumentation.  If you need to debug something, you
can just drop into that part of the system and look at it's picture to
understand how it works, then test it in isolation to see if it's misbehaving.

.. include:: i_navigation_6.rst

.. _zero_to_one-do-you-typically-use-timing-diagrams-with-your-design6:

**Do you typically use timing diagrams with your design?**

No. I think they look good, but they quickly add to your technical debt.  So
only use them if you need them.

To explain what I mean consider what would happen if I change the number of
buzzes used to tell someone their food is done, from 2 to 3.

Now I have to remember to go back into the timing diagram and mess about with
the drawn pulses, I have to re-size the picture and make sure all of the words
fit.  I'm not adding a lot of value here and this work would slow me down.

In comparison, to change the number of pulses from 2 to 3 in the statechart
diagram I would update one character in its picture, and I would be done.

.. note::

   Timing diagrams should be generative; they should automatically be
   constructed from the instrumentation output.  I did this work for the
   construction of the sequence diagrams but I did not do it for the timing
   diagrams.

.. include:: i_navigation_6.rst

.. _zero_to_one-how-do-you-generate-the-ascii-sequence-diagrams-from-the-trace6:

**How do you generate the ASCII sequence diagrams from the trace?**

You can read about that :ref:`here <reading_diagrams-sequence-diagrams>`.

.. include:: i_navigation_6.rst

.. _zero_to_one-what-is-a-payload6:

**What is a payload?**

The payload is the thing within the event.  You can use this to pass whatever
information you want between threads.  In our case we use a payload to
describe the number of buzz pulses:  The event is passed from the statechart to
a one shot thread and then from the one shot thread back to the statechart.
When the statechart receives the ``Get_Ready`` or ``Done`` events, it can look
within those event payloads to get the number of times we want the buzzer to
pulse:

.. code-block:: python

  # e is the event
  e.payload.buzz_times

.. include:: i_navigation_6.rst

.. _zero_to_one-why-do-you-use-a-namedtuple-to-make-a-payload6:

**Why do you use a namedtuple to make a payload?**

Nametuples are immutable and they are easy to make and describe; they make great payload data structures.

You don't have to use a namedtuple; but I advice that you use something immutable.

.. include:: i_navigation_6.rst

.. _zero_to_one-why-should-payloads-be-immutable6:

**Why should payloads be immutable?**

Immutable means that it can't be changed once it's written.  This immutability
is precisely what we want because we are sharing information between two
different threads which operate at different times and have no knowledge of one
another.  If both threads try to change the information they share, as some
underlying process task-switches between them, the information will become
scrambled for both threads.

You can see how this could lead to a nasty bug.  These kinds of bugs appear to
happen randomly; so they are extremely difficult to reproduce and fix.  In fact,
this is why people advise against the use of threads.

If you do share memory between threads, you need to provide a locking mechanism.

.. note::
  
   This is what the `GIL
   <https://realpython.com/python-gil/#what-problem-did-the-gil-solve-for-python>`_
   does in Python, it's a locking mechanism that has gotten a lot of bad press.

Or, you can take a Charlie Munger approach and just pre-avoid the mistake:

Miros doesn't share memory, so it doesn't use a locking mechanism, it just
copies the data from one thing into the queue of another thing.  But, there is a
chance that Python won't actually make a copy of your data, it might use a
reference (I can't claim to understand the implementation details of Python
memory management.)

So to pre-lock all of your data in the payload, use an immutable data structure.
If you can't change the data once it is written, you can't have a bug.  This is
why namedtuples are great event payloads.

.. include:: i_navigation_6.rst

.. _zero_to_one-can-you-explain-the-timing-diagram6:

**Can you explain the timing diagram?**

The timing diagram contains two signals: the "hardware Timing" as the blue line
and the "Statemachine Timing" as the red line.  The horizontal axis is time and
the vertical axis represents voltage.

Monitoring a voltage change on the hardware makes sense but it doesn't really
make sense when we are thinking about the statemachine.  So we need to wave our
hands and pretend we have peppered hardware-bit-toggling code through out the
statemachine and we are monitoring the output of its pin's voltage with an
oscilloscope.  We aren't going to do this, but you know it is possible.  If it
where added to the code, the results would be used to construct the
"Statemachine Timing" signal.

The positive edge would map to the ``post_fifo`` call initiating the oneshot and
the negative edge would map to the moment the task managing the one shot
began to run.

.. image:: _static/ToasterOven_6_Timing_Diagram.svg
    :target: _static/ToasterOven_6_Timing_Diagram.pdf
    :align: center

The "thread start latency" is the time between when we want to initiate a one-shot or
multi-shot task, and when it actually starts.  This latency might be very small,
but it will always be there.

.. note::

   This "thread start latency" will very depending upon which version of python
   you run, your os, your hardware etc.  It will not be reliably consistent.  If you need
   tight time tolerancing switch to qp.

Here is the timing diagram with the code that initiates the timing.

.. image:: _static/ToasterOven_6_Timing_Diagram_2.svg
    :target: _static/ToasterOven_6_Timing_Diagram_2.pdf
    :align: center

The diagram displays two different kinds of deferred event patterns.  The
"Get_Ready Oneshot" and "Done Oneshot" events occur sometime after they are
initiated, they are deferred.

This is not true for the buzz one-shot and multi-shot, they trigger almost
immediately after being started.

.. include:: i_navigation_6.rst

.. raw:: html

  <a class="reference internal" href="quickstart.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="reading_diagrams.html"><span class="std std-ref">next</span></a>

