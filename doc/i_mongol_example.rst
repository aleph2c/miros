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
would begin the most dangerous and effective movement in their 'defeat in
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

So the retreat war cry would occur when the last horse archer pulled his
scimitar, or when an officer was lured or when enough time had passed for the
enemy to re-organize.

A retreating horse archer was extremely dangerous; since they would pretend to
be slow when they were actually fast.  The closer you got to them, the easier
you would make their shot on you.  Your advance would not be protected by a
flanking soldier; but there would be another horse archer their also retreating
with his brethren.  They were especially dangerous to officers, since an officer
would often be on horse back to increase their mobility and express their rank.
The speed of the chasing officer would pull him away from his protecting mass;
leaving him alone and flanked by his enemies.  He had no real chance of catching
his prey; all of his training and ideas about the world working against him.

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
being your need to track who in your unit was ready to go.  If you were the last
horseman, the rules would still apply:  You would advance; you would circle and
shoot; you would skirmish and lure and retreat-to-fire when followed.

.. image:: _static/backwards.jpg
    :align: center

:ref:`back to examples <examples>
