.. _glossary-glossary:

Glossary
========

.. glossary::
   :sorted:

   State
    Defines the current operating condition of a program.  In the Harel
    Formalism, a state would map to a particular rounded rectangle in your
    state diagram.

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







