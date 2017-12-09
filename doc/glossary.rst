.. _glossary-glossary:

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

   Event
      Any action in the world that your program cares about.  It can be
      triggered by a user, an instrument or internally by your own design.
      Your program will notice, then react to this event by running a subset of
      your design to manifest the behavior described by the chart's structure.  An
      event is often named something.  This name is called a signal.  An event
      can also carry a payload, which can be any data object describable by
      Python.

      An event can be source from a ``post_fifo`` or ``post_lifo`` or
      ``publish`` call.  An event can have an optional payload but it must be
      created with a signal.  An event is always the second argument of your
      state methods.

   Signal
      A signal is a common set of enumerations that apply to all sets of events
      within the system.  They are used to catagorize events into pools of
      commmon meaning that can be used by your state methods to take action
      upon.  There are external signals (which you define as a user) and
      internal signals like INIT_SIGNAL, ENTRY_SIGNAL, EXIT_SIGNAL .. which are
      used internally by the event processor algorithm.

   Publish
      An active object can publish an event anytime by using the ``publish``
      method.  This will pass the event to the active fabric which will search
      and determine if any other active objects have subscribed to the event.
      If they have it will post this event into their internal queue so that it
      will be consumed during a future run-to-completion process.

   Subscribe
      A subscription is a multi-statchart concept.  When an active object would
      like to receive and respond to a message provided by another active
      object it can subscribe to the signal that that event will contain.

   Run To Completion (RTC)
      A run to completion process begins when a statechart receives an event.
      It searches it's local graph and makes a determination if it needs to
      respond, if so it will transition from the local state to the target
      state while adhering to the Harel Formalism, then it will run the
      INIT_SIGNAL within that target state.  If that state initiations itself
      by transitioning to another state, the event processor will run that
      transition with the Harel Formalism.  This will continue until the
      statechart has nothing left to do at which point it is finished it's
      run-to-completion processing.  The active objects can not be pre-empted
      with new events while they are in the throes of running through a RTC
      process.  If an event is received it is placed in the queue and it will
      not be considered by the event processor until it's RTC step is
      completed.
      

   Harel Formalism
      The Harel Formalism is a set of rules for describing how events should be
      processed by active objects.  They describe when internal events should
      be send to state methods.  For instance an ENTRY_SIGNAL event should be
      sent to a state method when it's boundary is breached from the outside to
      the inside of the state.  An INIT_SIGNAL will be sent to a state method
      anytime a state has been settled upon.  An EXIT_SIGNAL event should be
      sent to a state method when it's boundary is being breached from an
      inside-to-the-outside.  If a state doesn't know how to manage an event it
      is passed out to it's outer state.  If no states know how to manage a
      signal it is ignored by the state chart.

   Fifo
      First in first out.  Things line up as you image they should.

   Lifo
      Last in first out.  An item gets to barge to the front of a line.

   Spy
      The spy is one of the two instrumentation techniques used by the miros
      library.  It shows every detail that the event processor is doing while
      it is searching and running an RTC event.  You can add information into
      the spy log by using the ``scribble`` method.  You can view this
      log live as it is running by using the live spy.  Or you can look to see
      what the log contains by running the ``spy`` method.  The spy log has a
      ring buffer containing 500 spots.

   Trace
      The trace is one of the two instrumentation techniques used by the miros
      library.  It provides a high level view of what has happened, in that it
      show the initial stimuleous, the starting state and the ending state per
      line.  Unlike the spy it does not show the details related to how the
      transitions occured or any of the internal workings of the event processor.

      It can be used with the sequence tool to generate ASCII sequence
      diagrams.

      You can view the live trace log by using the live trace.  Or you can look
      to what what the log contains using the ``trace`` method.  The trace log
      has a ring buffer which contains 250 spots.

   Sequence
      Sequence is a tool that consumes trace log strings and produces ASCII
      sequence diagrams.  If the spy log contains the output of many different
      active objects, the sequence tool will create as many sequence diagrams
      as there are active objects in the trace.

   Statechart
      A statechart is a Hierarchical State Machine with it's own queue for the
      events it hasn't reacted against yet and a thread in which it can run.
      The word was invented by David Harel and it is often used as a synonym
      for active object or factory in this documentation. 

   Pattern
      A statechart pattern is an example of how to structure a map with some of
      the features provided by this library to solve a class of problems.

      The idea of a pattern was originally invented by the architect
      Christopher Alexander.

   Event Processor
      The event processor is the code the creates the Harel Formalism.  It was
      ported from the work of Miro Samek.  The library is named miros in honour
      of his contribution.

   Parent State
      A parent state is a relative term.  For a state to have a parent state it
      must be incircled by that parent state in a Hierarchical State Machine.

   Child State
      A child state is a relative term. For a state to be a child state of
      another state it must be within that other state's boundary.

   Top State
      A top state is a state that is the parent state to all states within a
      Hierarchical state machine.  It actually exists as a state method within
      the event processor.

   Catch and Release
      Describes a pattern where an event is caught by a state method, used as
      stimulation to run client code and then re-released as if that state
      didn't know how to process the event.

   Defer
      The ``defer`` method is a way to place an event into a secondary queue
      that is ignored by the active object until the momenent the ``recall``
      method is called.  At this point the event is placed into the active
      object's queue as if an outside caller used it's ``post_fifo`` method.

      The number of elements contained with the deferred queue can be seen
      using the spy instrumentation.

   Recall
      The ``recall`` method is to pop the oldest item from the deferred queue
      and place those items into the working queue of the current active
      object.

   Template
      A template is a state method that has a structure which contains the
      ``signal_callback`` and ``parent_callback`` context managers.  You can
      use a template using the ``state_method_template`` and it will return a
      state method who's name is as an input.  It will be instrumented and will
      has access to the signal callbacks and parent state which you provide
      it's active object with once it is formed.

      A state method built up this way can be turned back into a flat method by
      using the ``to_code`` method.

   One Shot
      A one shot is a delay event.  It can be created using the ``post_fifo``
      or ``post_lifo`` call by setting the ``times`` argument to 1 and the
      ``deferred`` argument to True.  The ``period`` argument is in units of
      seconds and it's value will determine the time delay prior to the event
      being presented to the active object's queue.

   Multi Shot
      A multi shot is sent from a ``post_lifo`` call by setting the ``times``
      argument to how every many events you would like to post (0 for
      infinite).  If you would like to delay the event, set the ``deferred``
      argument to True.  The ``period`` argument is in units of seconds and
      it's value will determine the time delay prior to the event being
      presented to the active object's queue if you have deferred the event.
      It also represents the period of your multishot.







        


