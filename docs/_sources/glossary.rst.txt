.. _glossary-glossary:

If you are a mathematician you will be disappointed by the lack of formality in
these definitions.

Glossary
========

.. glossary::
   :sorted:

   State
      Defines the current operating condition of a program.  A program will have
      more than one state and collectively these states are called a state machine.

   FSM
      Finite State Machine: a :term:`state machine<State Machine>` without hierarchy.

   State Machine
      A program which uses :term:`states<State>` and :term:`events<Event>` to
      determine how it should react to information coming to it in an
      asynchronous manner.

   State Method
      The code used to describe a :term:`state<State>`.  They can be hand coded,
      built using a template or described within a Factory.

   Pseudostate
      Awkward language describing icons that aren't transitions or states in a
      statechart diagram.

   HSM
     Hierarchical State Machine: a state machine where states can exit within
     other states.  An outer state is called a parent state and an inner state
     is called a child state.  In an HSM all child states share the behavior of
     the parents states unless this behavior is over-written by the designer.

   Event
      Any action in the world that your program cares about.  It can be triggered
      by a user, an instrument or internally by your own design.  Your program
      will notice, then react to this event by running a subset of your design to
      manifest the behavior described in the specification.  An event is often
      named something.  This name is called a signal.  An event can also carry a
      payload, which can be any data object describable by Python.

   Signal
      A name of an event.  Signals can be shared between many different events
      and they are used by state methods to determine how they should react to a
      given event when it is called by the Event Processor.

   Payload
      A data object that has been injected into an Event.  It is intended to be
      used by the consumer of the event.

   Mealy State Machine
      A state machine which provides program output on the transition between
      states.  Because of this, the path taken by the state machine become's
      its own unmanaged state.  To program using the Mealy style you would
      write functions onto your state transitions.

   Moore State Machine
      A state machine which provides program output within the state.  This is
      different from the Mealy approach, in that the transitions do not output
      information from the program.  The program outputs happen within the
      states themselves.

   Active Object
      Contains an event processor, a queue and a thread which wakes up when an
      event is placed in its queue.  Upon waking, it calls the event processor with
      the event and the state methods which are connected to the method are run
      in accordance to the Harel Formalism.  An active object also has a
      relationship with the Active Fabric, which is a singleton class shared by all
      active objects.  If the Active Fabric has not been created before it is
      created by the active object.  The active fabric is the software which
      allows all active objects to communicate with all other active objects.

   Active Fabric
      A singleton class shared by all active objects.  Through it active
      objects can publish and subscribe to events created by other active
      objects.  It contains two seperate threads (fifo/lifo) each tied to their own
      priority queue.  When an active object publishes to the active fabric, it
      places the event in both priority queues at the priorty set as an
      argument given to the publish call.  If another active object has
      subscribed to that event with the fifo subscription, the active fabric
      will post the event into it's deque using the post_fifo method.  If it
      subscribed using a lifo subscription it will post into it's deque using
      the post_lifo method.

   Factory
      The Factory class inherits from the active object class and thereby gains
      all of it's abilities and relationship with the Active Fabric.  In
      addition to this is can be used to manufacture state methods and nest
      them within one another.  It also has a reflection feature, ``to_code``
      which can be used to show what it's manufactured state methods would look
      like if they were hand crafted.

      


