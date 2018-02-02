.. _i_mongol_example-mongol-horsemen:

  *The most difficult subjects can be explained to the most slow-witted man if
  he has not formed any idea of them already; but the simplest thing cannot be
  made clear to the most intelligent man if he is firmly persuaded that he knows
  already, without a shadow of a doubt, what is laid before him.* 

   -- Leo Tolstoy

Mongol Horse Archer
===================
In this example I will demonstrate how to write a type of tactical botnet.  I
will base it on something from history, the Mongol Horsemen.

.. image:: _static/archer.jpg
    :align: center

The example will demonstrate how to design `emergent order
<https://en.wikipedia.org/wiki/Self-organization>`_ using multiple nodes across
a network, which have limited information about one another.  Each node will
have the ability to link up with another node and act in unison and then unlink
and act under their own initiative.  The overall unit tactic will continue to
work even if only one node remains.

**Example Background:**

* :ref:`Historical Context<i_mongol_example-historical-context>`
* :ref:`Deceit in Detail<i_mongol_example-distributed-officers>`
* :ref:`Modelling the Mongol Mind<i_mongol_example-modelling-the-mongol-mind>`

**Example Software:**

* :ref:`Technical Overview<i_mongol_example-technical-oveview>`
* :ref:`Designing the Mongol in its Tactic<i_mongol_example-designing-the-mongol-in-its-tactic>`
* :ref:`Encrypted Commnications<i_mongol_example-encrypted-communications>`
* :ref:`Instrumenting to Debug a Horse Archer<i_mongol_example-instrumenting-to-debug-the-botnet>`
* :ref:`Implementing the Mogol in miros<i_mongol_example-implementing-the-mongol-in-miros>`



.. _i_mongol_example-historical-context:

Some Historical Context For the Example
---------------------------------------
Military officers are faced with the paradox of leadership.

As a leader they collect information about their army and as much intelligence
about their enemy as they can access.  From this information they render a plan
of how to harm their enemy as much as possible while limiting losses to their
own force.

An officer must exert their plan onto an army of men who would rather be at
home working their fields and feeding their families.  When an officer exerts
their power over a soldier they reduce that soldier's ability to think for
themselves.  But each battling soldier consumes tremendous amounts of
information; far too much to send up the chain of command.  If they could act
upon it independently, it could be to the great advantage of their army.  This
is the paradox of leadership, when a leader exerts too much control over their
subordinates they limit the effective intelligence of the group to their *own
mental ability* and the *limited information* they are receiving.

The chain of command is like an extremely slow nervous system.  Limited and
bottle-necked by the cognitive load and biases of each officer as they transmit
orders to their soldiers and the results of those orders back up to their own
ranking officer.  

But without officers providing decisions in battle, the group would breakdown
into a set of unorganized individuals who at best, would default to their
training and at the worst would run from the enemy exposing themselves to
slaughter.  Group cohesion is the key.

In war their are hard points and weak points to armies.  Ideally, you would
attack your opponents weak point with your hard point.  An example of this is a
flanking maneuver.  If you can hit your enemy at the side (flank), rather than
at their front, you would minimize your losses while maximizing theirs.

But the chain of command itself, is a weak point in an army.  If you could kill
the officer's of your opposing force, you would turn the army into a group of
scared men all acting alone.  A micromanaging general who is exerting absolute
control can be attacked directly with confusion and mental over-taxation.  Such
a general becomes a weak point because of the paradox of leadership.  As their
mental abilities are diminished by confusion their army acts dumber, making ever
worse collective decisions.

In the 13th Century, western armies typically organized their officers in
hierarchical structures, using command and control architectures.  The officers
would be on the front line, mounted on horse back, wearing heavy armor, easy to
identify.

The Mongol forces were organized differently, each horse archer could act as a
local officer to control the over all efforts of their local unit.  Each unit
was made up of no more than ten horse archers.  The cognitive load required to
control the whole system was limited, because each unit could act independently
from their whole.

There was still a hierarchy of leadership in the Mongol army with different
ranking officers controlling the actions of the groups of units under their
command; but orders where issued as intentions, rather than a specific set of
individual instructions.  Today we call this, "commander's intent".  If such
orders are used, the military force under their command becomes smarter than the
officer issuing them.  Each officer at each level can innovate and react to
their local battles as they unfold.  Officer-ship itself is pushed down into the
individual soldiers.

The Mongol tactics and strategy were intended to harm the state of mind of the
opposing military commander.  They would not stay put, they would not act in a
way that could be fathomed by theory or previous experience.  They would put
their opponents into constant conundrums, if their enemy closed ranks the
Mongols would fire arrows on the mass of men, if they spread out, the Mongol
could attack and pick off the individuals.

Any opposing micro-manager would quickly become overwhelmed, leaving their
forces lobotomized; breaking down cohesion.

So confusion was the great weapon of the Mongols and it was blasted directly at the
minds of the military commanders controlling the opposing force.  When a Mongol
army came upon a larger army controlled using traditional-command-and-control
cognition, it was a simple matter to destroy them at their leisure -- since the
opposing army lacked to mobility to catch or surround the mongols.

The Mongols would engage, feign a retreat, then move into more favorable
terrain.  The opposing force would be lead away from their strong point,
exposing a supply line and become small enough that the Mongols could attack
them en masse with numerical superiority.

This tactic is called "Defeat in Detail".

.. _i_mongol_example-distributed-officers:

Deceit in Detail
----------------
Now let's talk about a specific "Defeat in Detail" set of tactics used by an
individual unit of Mongol horse archers.

Their commander's intent was for them to lure the enemy away from its protecting
mass and kill as many officer's as possible.

Each horse archer started a fight with 60 arrow's and a scimitar.  They wanted
to damage the enemy with the arrows from a distance so that they could avoid
risk.  They would only pull their scimitar while close to their prey.  But the
point of the scimitar wasn't to kill or maim their enemy, but to protect
themselves while they got close enough to present a lie.

In close quarters the Mongol would pretend that they were scared.  They would
act as if their unit's will was broken when it wasn't.  This behavior would have
been especially alluring to any opposing military officer's who wanted to prove
their valor.  They would have been more willing to see this fake weakness as a
truth; enraged and frustrated with their own inability to take action, they
would be inclined to take the bait.

The Mongol units had to attack as a unit and retreat as a unit.  To do otherwise
would have had them executed by their own senior officers for lack of cohesion.

But the retreat requirement of this cohesion-directive was often broken by the
fog of war. They couldn't always know if another horse archer had been killed
and to wait around and get killed themselves would have been stupid; so a
compromise was reached.  When a horse archer saw that their enemy was
re-organized enough to put up real resistance, or better yet,  they had
successfully lured an officer, they could issue a retreat war cry and all other
horse archers within earshot would follow them to a predetermined marshal point.

While retreating, the horse archers would turn and use their last arrows on the
enemies chasing them; placing the highest priority on officers.

It is possible that modern Western military theory has still not caught up to
medieval Mongol thinking.  The tactic name, "defeat in detail" might have been
called "deceit in detail" had it been written down by a 13th century Mongol,
instead of a despotic Frenchman.

.. _i_mongol_example-modelling-the-mongol-mind:

Modelling the Mongol Mind
-------------------------
A group of Mongol horse archers needed to protect their mental flanks while
doing the most to harm their opponents.  The key to this is to make the group
tactic simple from the inside and bafflingly complex from the outside.

Each soldier needed independent thought and action but in a moment to be able to
snap back into a collective dance with the rest of their unit.  The calls
between the members of a unit needed to be encrypted, simple and loud.  

The amount of memory needed to track their brethren also needed to be limited.
Unlike the general trying to remember and track everything all at once, our
distributed officer only needed to remember a few crucial things.

To make things mentally easier, the Mongol soldier relied on the idea of
sameness.  The ergodic mirror metaphor is useful here.  If you were surrounded
by an ergodic mirror, anywhere you turn you would be looking into your own eyes.
So the Mongol horse archers where ergodic; they were surrounded by themselves.
Every member of their unit would act as they would, so there was no concern or
doubt about what to do.

The tactics used by a unit of horse archers needed to work even if some of its
members were killed.  The hologram provides another useful metaphor.  A
holographic sheet is a two dimensional thing, yet as its parts work together it
produces something in the third dimension.  If you scratch the holographic
sheet, the three dimensional image remains, only slightly fuzzier than it was
before.  To be effective the Mongol tactics needed to have this same property.
As a unit they express complexity beyond the sum of their parts and this
complexity would not break down with losses, but only lose its fidelity.

Let's weave these metaphors into the specifics of battle.  To begin with a
Mongol unit would meet, fill their quivers with arrows and decide where they
would meet again after their first encounter.  This next place, call it a
marshal point, would be on ground which would give them some sort of advantage
and access to more ammunition.

They would wait for an advance-war-cry.  Any member of their unit could issue
this call and all members would immediately advance.

At a certain distance from the enemy the horse archers would have their horses
follow each other to form a circle.  The closest horse archer to the enemy front
lines would shoot an arrow, then reload as their horse took them around the
circle again.  This would create a kind of sustained machine gun effect on their
opponent's mass; causing them to loosen their ranks as to avoid the constant
barrage of arrows.

The next stage of battle would have the horse archers get close enough to their
enemy to skirmish.  While skirmishing a horse archer would aim their arrows
directly at individual opponents.  To begin a skirmish any of the horse archers
could issue a skirmish war cry and all other units would follow, breaking away
from their circle to move close into the now disordered front of their enemy.
At some point one of the horse archers would become low on ammunition; then they
would begin the most dangerous and effective movement in their 'deceit in
detail' tactic, they would pull their scimitar; saving the last of their arrows
for their luring retreat.

While swinging their scimitar they would do exactly the opposite of what you
would expect a terrible horse archer to do.  They would appear scared and
confused; disoriented and craven.  It is not easy to charge into the heart of
your enemy only to put on a play for them; but this deceit was necessary to lure
their enemy into *real* danger.

So as a horse archer was fighting, they would have to remember enough about their
unit to know if they were the last to pull their scimitar.  If they were, it
meant that as a unit they were low on ammunition and they were ready for a their
next collective action.

This would mean that a horse archer would have to call out when they were
pulling their scimitar; and each other horse archer would have to track this
information.  But if a horse archer was killed; they wouldn't be able to call
out; so there had to be another way for the unit to communicate to itself that
it was time to go.  So any horse archer could issue a retreat war cry.  They
could do this when they had successfully lured an officer are when enough time
had passed that the enemy was becoming sufficiently reorganized to actually put
up real opposition.

The retreat war cry would occur when the last horse archer pulled his
scimitar, or when an officer was lured or when enough time had passed for the
enemy to re-organize.

A retreating horse archer was extremely dangerous; since they would pretend to
be slow when they were actually fast.  The closer you got to them, the easier
you would make their shot on you.  Your advance would not be protected by a
flanking soldier; but there would be another horse archer their also retreating
with his brethren.  They were especially dangerous to officers, since an officer
would often be on horse back to increase their mobility and express their rank.
The speed of the chasing officer would pull him away from his protecting mass;
leaving him alone and flanked by his enemies, his helmet blinding his peripheral
vision.  He had no real chance of catching his prey; all of his training and
ideas about the world working against him.

From the outside the mongols would appear like a angry swarm of wasps;
incomprehensible, always out of reach.  Any engagement with them reducing the
leadership and cohesion within your own force.

But if you were an individual horseman, you would only have to follow a few
simple rules.  Advance if you heard an Advance war cry.  Create a circle when
close enough to the enemy.  Skirmish when you heard a Skirmish war cry.  Track
your unit's Retreat Ready War cries; so you can know if it is up to you to issue
the Retreat.  When you heard a Retreat War cry retreat and attack any lured
enemy's flank.

As an individual horseman, you could issue your own commands to your group.  You
could give an Advance War Cry, to start the circle.  When you were low enough on
arrows you could make the Skirmish war cry and your brethren would close the
distance to the enemy with you.  If your ammunition was running low, you would
issue the Ammunition Low war cry and the other members of your unit would know
you are ready to go.  If you had successfully lured an officer, you could issue
the Retreat war cry and leave knowing that your brethren would follow and flank
the officer chasing you.

Most of your concentration would be used to make your shots, or to put on the
deceitful-play while close enough to the enemy.  The only exception to this
being your need to track who in your unit was ready to go.

If you were the last horseman, the rules would still apply:  You would advance;
you would circle and shoot; you would skirmish and lure and retreat-to-fire when
followed.

.. image:: _static/backwards.jpg
    :align: center

Now that we have an understanding of what we are trying to model, let's build it
in software using miros.

.. _i_mongol_example-technical-oveview:

Technical Overview
------------------
To build the horse archer botnet we need at least two different computers.  I'll
be using a windows machine and a raspberry pi.

First, we'll design a set of statecharts that will model an individual horse
archer and it's understanding of it's brethren.

Any communication between our horse archer bots will be encrypted, since we
don't want our enemy to learn about what we are doing.

We will adjust how our instrumentation works; we will make it so that it can
stream its output to any computer of our choosing.  We will do this so we can
debug our entire botnet from one location.

Finally We'll write the software; run it on two or more computers and demonstrate
that it is working.

Here are the steps:

* :ref:`Designing the Mongol in its Tactic<i_mongol_example-designing-the-mongol-in-its-tactic>`
* :ref:`Encrypted Commnications<i_mongol_example-encrypted-communications>`
* :ref:`Instrumenting to Debug the Mongol Botnet<i_mongol_example-instrumenting-to-debug-the-botnet>`
* :ref:`Implementing the Mogol in miros<i_mongol_example-implementing-the-mongol-in-miros>`

.. _i_mongol_example-designing-the-mongol-in-its-tactic:

Designing the Mongol in its Tactic
----------------------------------
We already understand the tactic, so I'll draw and describe how I think it might
work in an HSM several times over; adding complexity and technical improvements
with each iteration.  When we have a design that can sufficiently sketch out our
bot net I'll move to the next technical step.

While working through the example we will introduce different events that cause
changes in the horse archer's behavior.  When an event is a war cry, who exactly
is yelling it out?  Any war cry can come from one of two places.  It can come
from the horse archer himself, or a senior officer.  We do this so that the
unit tactic can be autonomous yet flexible enough to receive outside direction.

Let's think about a single horse archer and the actions he would take.  He would
meet up with his brethren (marshal), then they would determine where they would like
to meet after their first maneuver, then they would fill their quivers with
arrows.

So, I have to first figure out what to call the outer state.  For now I'll call it,
Deceit_in_Detail_Tactic (marshaled), because I want to express that the horse
archers are meeting and that this is one tactic of many that they could choose from.

.. image:: _static/ergotic_mongol_11.svg
    :align: center

`ergotic_mongol_11`_

Immediately after filling their arrows, they attack.  This may not be
historically true, but let's have our botnet just attack right away.

Once the horse archers advance close enough to the mass of their enemy, they
would circle and fire.  How do we express this in software?  If we were building
a botnet to fight the North Koreans or a malevolent AI or something, we could
have each node in our botnet read a transducer or take a reading.  For now we
will fake out this information with a
:ref:`one-shot<recipes-create-a-one-shot-state>` so that we can frame in our
design.  Three seconds after advancing they will issue the
Close_Enough_For_Circle event.

So our horse archers circle and fire; creating an intangible rain of arrows down
upon the enemy's front line.  To save themselves, the enemy loosens their ranks
allowing enough space and safety for our horse archers to charge in for their
next play.

Notice that the Circle and Fire state is within the Advance state.  Why do this?
I did this in case an individual horse archer decided that the enemies front was
sufficiently disorganized enough not to waste arrows on an imprecise
bombardment; To skip the circle and fire step and just advance into a skirmish.
To do this, they would issue a Skirmish_War_Cry and charge into the enemy's
disorganized front and to make individual attacks.

.. image:: _static/ergotic_mongol_12.svg
    :align: center

`ergotic_mongol_12`_

Upon making the Skirmish_War_Cry are horse archer charges into close enough
range to make individual attacks with their arrows.  This type of fighting is
called a skirmish to show that we do not want them to stick around.

Our war bot would have some client code connected to the entry condition of the
skirmish state.  It might be the initialization of a specific targeting and
attack control system, whatever it is it would have to issue the Ammunition_Low
event when it was done firing upon specific targets.  This Ammunition_Low event
would be caught by the skirmish state as a :ref:`hook<patterns-ultimate-hook>`.
This hook would in turn, trigger a Retreat_Ready_War_Cry event.

I could have just used a single Ammunition_Low event to cause the transition
from the Skirmish state into the "Waiting To Lure" state.  But, I often use two
distinct events like this to make the debugging and reflection processes easier
on myself, so that I can debug a statechart faster than I could with only one
event that expresses two different semantic meanings.  (This will also give our
design more flexibility, which we will see later in this example).

After a horse archer issues the Retreat_Ready_War_Cry they enter the "Waiting to
Lure" state.  He would expertly attach his bow to his mount and pull his
scimitar, then he would do something really brave.  He draw the attention of an
enemy officer and somehow convince him that he was scared and incompetent, that
his unit's will was broken.  While in the waiting to lure state, he would act
like a father who is being chased by his children.  He would pretend that they
could actually catch him if they only just tried a little bit harder.

The western Knight would be spoiling for a fight, feeling enraged, yet
incompetent, he would want to do something other than watch his footmen die.  He
might look down at his massive warhorse and compare it to the strange little
ponies these horse archers are riding.

What he doesn't know is that he is the quarry.  They are on a hunting trip; not
every arrow carries the same value; the whole point of their attack was to find
him.  They have something to give him.

The Knight see's his chance and attacks!

Once again we find ourselves needing real input from the world.   This is where
our bot would need another transducer or reading to determine if the officer had
been lured.  For now we will fake out the reading with another one-shot, so that
we can frame in the design.  To make things interesting we will pick a random
integer between 3 and 12 and then count down in seconds before we trigger our
fake Officer_Lured event.

The horse archer has been paying careful attention to the Knight even though he
has been pretending not to see him.  When he sees him begin his attack, he
issues the Officer_Lured event.

The Officer_Lured event is caught by a hook, which triggers the Retreat_War_Cry.
The Retreat_Ready_War_Cry causes an exit transition from the "Waiting to Lure"
state.  This will have the horse archer put away his scimitar and arm his bow
with an arrow.

.. image:: _static/ergotic_mongol_13.svg
    :align: center

`ergotic_mongol_13`_

The Retreat_War_Cry causes the horse to enter the "Feigned Retreat" state.  In
this state, a different control system would come into play.  The horse archer
would let the Knight close the distance to him, so that he can comfortably make
his shot.

He might even veer and dodge to place bodies and soldiers between him and the
charging Knight, or lure him closer toward other horse archers who could flank
the knight; taking advantage of how his helmet has cut off his peripheral
vision.  It doesn't really matter; once the knight attacks, stupidly charging
into a group of organized horse archers with unprotected flanks, he is doomed.

What to do next?  The unit goal has been achieved, yet they still have arrows.
So they leave them in any other pursuing soldiers, then ride full gallop back to
the marshal point.

.. image:: _static/ergotic_mongol_14.svg
    :align: center

The final stage of our tactic would have the horse archers meet at their marshal
point.  Their they would decide upon where to meet again after their next
attack.  Load their horses with arrows, field wrap their wounds.  Drink and
water their horses and mentally prepare themselves for the next advance.

The requirement for group cohesion still applies.  Any horse archer would be
limited on the battle field if he had to advance with an empty quiver; so every
horse archer would want to wait for the last horse archer to finish reloading
before advancing.

Therefore like the "Waiting to Lure" state, there must be a "Waiting to Advance"
state.  In this first pass at a design, we setup a one shot that will trigger
the READY event after three seconds.

In the "Waiting to Advance" state we place a randomized one-shot that will
trigger the Advance_War_Cry at some time between 3 and 12 seconds.

But this overall tactic, as it is currently designed is completely fragile.
What happens if a horse archer is issued an Advance_War_Cry while in the
"Marshal" state?  Well, he would just sit there.  What would happen if a
Skirmish_War_Cry was issued while the horse archer was in the "Feigned Retreat"
state?  They would ignore the command.  This is not flexible.

There will be situations where a senior officer issues an Advance_War_Cry when
the horse archer is not ready; no matter, it is time to attack, even without
arrows.  Group cohesion is of paramount importance to the Mongols.

So, as a map it is easy to see what is going on, but it tells a very specific
and inflexible story.  With a few light adjustments we could make the horse
archer much more seasoned and responsive in the face of unexpected events.

For instance we could make the Advance_War_Cry cause an advance on the enemy
while the horse archer is in any of it's maneuvers.  Suppose a horse archer is
in the "Feigned Retreat" stage and a senior officer sees some sort of global
opportunity and bangs on a war drum, issuing a global Advance_War_Cry.  Our
horse archer would turn around and advance.

In this way the control at a higher leadership level of the mongol army could
reach into this unit, tweak its behavior, then let it run autonomously again.

Let's improve the design:

.. image:: _static/ergotic_mongol_2.svg
    :align: center

As a statechart designer, you might look at the Advance_War_Cry event connecting
the outer state to the advance state and become confused.  Where does this
Advance_War_Cry come from?  Oh, there it is, in the "Waiting to Advance" state.  

I have seen junior developers destroy designs by adjusting arrows to make the
"story easier to read" off of the map.  It is tempting to put the arrow source
back to the "Waiting to Advance" state so that the map makes immediate sense
upon looking at it. But think about what this has done to our design.  When an
arrow is connected from the outer state, to the "Advance" state, it is shorthand
for connecting *all of the states* to the "Advance" state with an
Advance_War_Cry arrow.  When the junior developer mistakenly adjusts the tactic
to make the map "make more sense", they would break 7 different behavioral
pathways in this design; causing our horse archer unit to lose cohesion and thereby
guarantee its execution by a senior officer.  Statecharts are
extremely powerful at packing tactical complexity onto a map; so you really have
to be careful moving the arrows around.

Remember, at this stage of our design process any war cry can be issued by the
horse archer themselves, or by a senior officer.

Now let's adjust the Skirmish_War_Cry and the Retreat_Ready_War_Cry from the
outer state to their respective states.  We just added 14 different behavioral
paths.

Suppose that in the future, a new developer decides to adjust the deceit-in-detail
tactic by adding another state within it.  If they do not change how our
war-cry event arrows are attached, they will automatically get the behavior of
the old tactic without knowing that they did.  Statecharts are robust against
state additions made by future programmers.  So statecharts can quickly act like
a culture, they become smarter than the individual programming them.

Notice that the Out_Of_Arrows event was not globalized.  We do not want our
horse archer to just leave when he's out of arrows.  Furthermore, because of our
adjustments to globalize the Advance_War_Cry, Skirmish_War_Cry and the
Retreat_War_Cry we have to ensure we don't accidentally leave our horse archer
stranded in a state when he is out of arrows.

So what happens if an empty horse archer is asked to advance?  Well, he
uselessly circles and then will issue a Skirmish_War_Cry.  Good, he can escape
the "Advance" state.

Notice that some code was added to the entry state of the "Skirmish" state.  Now
if a horse archer has less than 10 arrows, or no arrows, he will end up in the
"Waiting to Lure" state.  This is good, he is no longer just uselessly riding
around because he can start to bait knights and he can escape the "Skirmish"
state event if he doesn't have arrows.

Likewise, entry code was added to the "Feigned Retreat" state.  When he enters
this state with no arrows, he will just ride back to the marshal point.

Now that we have a decent adumbration of a horse archer acting alone, let's add
control so the horse archers can react to the behavior of other horse archers.

A horse archer is a distributed officer.  This means that any horse archer can
issue commands to, or obey commands from, any other horse archer in his unit.
For this unit tactic, there are two types of commands.  There is a "Let's do
this thing right now!" and a "Track that I am ready in your head!" kind of
command.

To see what I mean consider the Advance_War_Cry.  That is a "Let's do this thing
right now" command.  All horse archers will immediately advance and circle if
they issued the command themselves or if they hear it come from another horse
archer or a senior officer.  In the deceit in detail there are three different
war cries that have this type of characteristic: Advance_War_Cry,
Skirmish_War_Cry and Retreat_War_Cry.

.. note::

  The "Let's do this thing right now!" variety of signaling between different
  statechart can be generalized into the "multi-chart race pattern", since each of
  the statecharts can be thought of racing to give the command to another chart.
  If given all of the statecharts will race to state indicated.

.. image:: _static/ergotic_mongol_31.svg
    :align: center

Let's turn each of these commands into three distinct events so that we can tell
if it was issued by a senior officer, the horse archer themselves or another
horse archer.  By doing this our statechart will be easier to debug, it's
instrumentation will be clear and the sequence tool will tell a better story.

We construct three new events, Senior_Advance_War_Cry, Senior_Skirmish_War_Cry
and Senior_Retreat_War_Cry.  Imagine that these commands can be issued at a high
vantage point by war drums near the back of the Mongol horde.

When a horse archer hears a command from a senior officer, they will give the
cry themselves and then perform the action.  We implement this using the
reminder pattern.  A hook is placed at the outer state for these commands; and
it re-issues a new event as a response.  When a horse archer calls out, it can
be heard by other horse archers through mechanism we haven't programmed yet, but
that doesn't mean we can't name them: Other_Advance_War_Cry,
Other_Skirmish_War_Cry and Retreat_War_Cry.

There will be situations where a horse archer wants to ignore a command coming
from a senior officer or from his brethren.  This is when he is already engaged
in a complicated maneuver that would be initiated by that command.  For instance
while the horse archer is baiting a night in the "Waiting to Lure" state, they
would ignore the Senior_Skirmish_War_Cry and the Other_Skirmish_War_Cry since
they are already engaged in that activity.

Likewise, a horse archer would ignore any order to advance, coming from someone
else, if they are already advancing or engaged in the circle and fire maneuver.

.. image:: _static/ergotic_mongol_32.svg
    :align: center

Battle is a noisy affair.  There is a good chance that one horse archer might
not hear a war cry issued by another one far away from him (network issues); so
anytime a horse archer hears a war cry coming from another horse archer, they
yell out the command again so as to re-transmit it to the brethren within
earshot.  In our diagram we do this with the reminder pattern.

.. _i_mongol_example-encrypted-communications:

Encrypted Communications
------------------------

.. _i_mongol_example-instrumenting-to-debug-the-botnet:

Instrumenting to Debug the Mongol Botnet
----------------------------------------

.. _i_mongol_example-implementing-the-mongol-in-miros:

Implementing the Mongol in miros
--------------------------------

.. _ergotic_mongol_11: https://github.com/aleph2c/miros/blob/master/doc/_static/ergotic_mongol_11.pgn
.. _ergotic_mongol_12: https://github.com/aleph2c/miros/blob/master/doc/_static/ergotic_mongol_12.pgn
.. _ergotic_mongol_13: https://github.com/aleph2c/miros/blob/master/doc/_static/ergotic_mongol_13.pgn

:ref:`back to examples <examples>`
