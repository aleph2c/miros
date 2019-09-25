.. _batterychargingexample-battery-charging-example:

Distributed Battery Charging Example
====================================
Lead acid batteries are very heavy.  But they are cheaper than lithium ion
batteries and this is why they are used in a lot of off-grid electrical systems.

.. image:: https://krisdedecker.typepad.com/.a/6a00e0099229e8883301bb0820445e970d-pi
    :target: https://www.lowtechmagazine.com/2015/05/sustainability-off-grid-solar-power.html
    :align: center

A large lead-acid battery is made up of a set of smaller lead-acid batteries
connected together in series.  These smaller batteries are called cells.

.. image:: _static/cells_in_series.PNG
    :target: https://chargetek.com/images/pdfs/equal.pdf
    :align: center

Each cell contains two terminals, and each terminal is connected to a plate that
reaches down into a bath of sulphuric acid (H2SO4) and water (H2O).  There is a
positive and a negative terminal.  The positive terminal of a cell is made up of
lead dioxide (PbO2) and the negative terminal is made out of lead (Pb).

A battery is a chemical reaction that wants to happen, but can't until there is
a path for electrons to flow from one material to another.  As a result, there
is a voltage potential expressed across the positive and negative terminals of
the battery.  If an electrical device is connected across these terminals an
electron path is made, the battery can begin its chemical reaction.  As a side
effect the electrical device is powered on.  The flow of current leaves the
positive terminal and enters the negative terminal.  When this happens the
battery is said to discharge.

.. image:: https://circuitglobe.com/wp-content/uploads/2017/01/lead-acid-cell-112.jpg
    :target: https://circuitglobe.com/lead-acid-battery.html
    :align: center

Charging of a battery occurs when current is forced to flow in the opposite
direction: current leaves the negative terminal and enters the positive
terminal. This causes the chemical reaction to reverse, sequestering the
electrons back into the various materials of the battery.  You can charge a
battery with a battery charger.

.. image:: https://circuitglobe.com/wp-content/uploads/2017/01/recharging-of-lead-acid-battery.jpg
    :target: https://circuitglobe.com/lead-acid-battery.html
    :align: center

.. note::
  
   If you aren't familiar with the terminology of electricity, imagine a water
   tower.  The water is trying to get to the ground, due to gravity,
   but it is held in place by the walls of the tower.  This means that there is a
   potential for the water to flow, the height of the tower determines how much
   energy is stored within it.  The higher the tower, the higher the potential
   energy.  Voltage is analogous to height of the held water in the tower.

   .. image:: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtYw4fJS9o3meW9yv5ZGJ5enzVpyJ0sfw5L45UifmATQERiArD
       :target: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTtYw4fJS9o3meW9yv5ZGJ5enzVpyJ0sfw5L45UifmATQERiArD
       :align: center

   Now imagine connecting a pipe from the tower to the ground, and letting the
   water flow through it.  This flow is like current in an electrical system, and
   the pipe width would limit that flow, so that would be like an electrical load.

   Our battery is like a water tower; if no pipe is connected, current can't flow.
   If a pipe is connected, it can, and the energy of the battery reduces just like
   the potential energy of our water tower would reduce as it's water leaves it
   through a pipe.  If you were to push the current back into the pipe, by
   connecting a higher water tower, or by just driving the current back up the
   tube with a pump, you would cause the potential of the water tower to increase.
   We would be charging the tower.

   As mentioned before, a battery is made up of stacking cells in series.  Think of
   that as a very tall water tower made up of stacked shorter water towers.  You
   can increase their potential energy by stacking them this way.

As a lead acid battery is discharged, a crust of lead sulphate (PbSO4) forms on the
plates.  This crust reduces the surface area of the lead plates exposed to the
acid, reducing its ability to react and drive current.  

.. image:: https://stevedmarineconsulting.com/wp-content/uploads/2019/06/082504179.jpg
    :target: https://stevedmarineconsulting.com/sulfation-too-many-batteries-die-an-unnecessarily-early-death-from-this-phenomenon/
    :align: center

There are electrical charging techniques which can remove this lead sulphate
(PbSO4), by reversing the chemical reaction, and even sometimes bubbling the
acid.  These bubbles physically massage away the lead sulphate crystals,
dislodging them from the plate, dropping them into the acid bath where they can
break down, crystallizing their lead atoms back onto the plates.

An electrical charger can control one of two things, it can act to control
current flow or it can control the voltage across the terminals of the
battery.  If it holds the current constant, electrons are pushed back into the
battery, which will cause the voltage of the battery to slowly rise over time.

If the charger holds the voltage at a higher potential than the battery voltage,
current will flow into the battery.  At first it will flow quickly, but over
time the battery's ability to accept electrons will be limited by the amount of
material within it, causing the current flow to subside.

.. note::
   
   Thinking back to the water tower.  If we re-filled our water tower using a
   pump to push a constant amount of water, this would be like controlling the
   current being pushed into the battery.  If we connected a higher water tower,
   and let it passively drain some of its water into the lower tower, this would
   be like controlling the voltage of our charger.  Together the two towers
   would have the potential energy of the taller tower, so it's voltage would be
   set to this.

When you hear people talk about the stages of charging of a battery, they are
talking about either a constant current or a constant voltage charging
technique.  In two stage charging, a constant current technique starts the
charging process, then once the battery voltage rises to a high enough level, a
constant voltage technique takes over.  In three stage charging, the third stage
is a constant voltage technique, but held at a lower value than the second
stage.  A forth stage of charging can be applied very infrequently, it's called
equalization.  It is a constant voltage technique that applies such a high
voltage across the battery terminals, that the acid boils, and explosive
hydrogen is expelled from the batteries (this is why battery rooms need to be
well vented).

There are arbitrary naming conventions that have been applied to these stages of
charging:

+---------------------+----------+----------+----------------------------------+
| Name of Stage       | Constant | Constant | Notes                            |
|                     | Current? | Voltage? |                                  |
+=====================+==========+==========+==================================+
| *bulk stage*        |  yes     | no       | 80 percent of charge put back    |
+---------------------+----------+----------+----------------------------------+
| *absorption stage*  |  no      | yes      |                                  |
+---------------------+----------+----------+----------------------------------+
| *float stage*       |  no      | yes      | voltage is lower than absorption |
+---------------------+----------+----------+----------------------------------+
| *equalization*      |  no      | yes      | voltage is very high             |
+---------------------+----------+----------+----------------------------------+

A charger is typically called one of these:

+-----------------------+--------------------------------------------------------+
| Name of Charger       |  Meaning                                               |
+=======================+========================================================+
| *trickle charger*     |  float stage only                                      |
+-----------------------+--------------------------------------------------------+
| *two stage charger*   |  bulk followed by the float stage                      |
+-----------------------+--------------------------------------------------------+
| *three stage charger* |  bulk followed by absorption, followed by float        |
+-----------------------+--------------------------------------------------------+

The *equalization* stage is so dangerous that it doesn't happen automatically,
it has to be manually set by the user.

It has been found that when you charge batteries with three stage chargers, the
process of plate sulphation is slower than it would be with a two stage charger.
If such a charger is also equipped with the equalization feature, a knowledgeable
user can keep their battery's healthy for a long time.

Let's look at the three stage charging electrical profile:

.. image:: _static/three_stage_charging_all.svg
    :target: _static/three_stage_charging_all.pdf
    :align: center

That diagram is not going to win any graphic design awards, but it shows you
everything you need to know about building a charger.  We need two control
systems, one that can hold current to a constant level and one that can hold the
voltage to a constant level.  We need to track time, so that we can exit a stage
if the charger has been in it too long.  And we need to be able to set some
parameters based on the kind of battery we are attached too.

The bulk stage is where the battery is charged quickly.  Charging the battery is
what our customer's care about the most, but battery maintenance is very
important too.  Management might try to downgrade the need for battery
maintenance because this isn't driving our customer's purchasing decision. If
this happens remind them that if we damage batteries over the long term, we
should plan for a class action lawsuit. Then start working on your resume.

The charger will have a rated current, the more money we put into its hardware,
the higher this current can be.  The problem is if we over-build this, our
charger will be too big for a lot of systems and these customers will buy
someone else's product because it is cheaper than ours.

A way to solve this problem is to build a charger that can be ganged together
with more versions of itself.  That way we can keep the costs low, and if a
customer needs a lot of current, they can buy as many of our products as they
need and gang them together in parallel. 

The added benefit of this approach is that if one of their chargers fail, there
batteries can still be charged by the others in their system.  It offers them
some resilience.  If they felt so inclined, they could actually over-build their
charging system to increase their system's reliability.  Batteries are
expensive, heavy and dangerous, and chargers are relatively cheap and easy to
work with and install.

Another problem our customers have is with the parameters.  We can't expect them
to figure out what all of the values and timeouts mean.  They really don't care,
we need to eat this complexity on their behalf, especially if we are expecting
them to buy a bunch of our products for a single installation.

:ref:`back to examples <examples>`
