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
      Awkward UML language describing icons or glyphs that aren't transitions
      or states.

   HSM
     Hierarchical State Machine: a state machine where states can exit within
     other states.  An outer state is called a parent state and an inner state
     is called a child state.  In an HSM all child states share the behavior of
     the parents states unless this behavior is over-written by the designer.

   Hierarchical State Machine
     HSM: a state machine where states can exist within other states.  An outer
     state is called a parent state and an inner state is called a child state.
     In an HSM all child states share the behavior of the parents states unless
     this behavior is over-written by the designer.  Software written using HSM
     follow the :term:`harel formalism<Harel Formalism>`

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
      Contains an :term:`event processor<Event Processor>`, a queue and a
      thread which wakes up when an event is placed in its queue.  Upon waking,
      it calls the :term:`event processor<Event Processor>` with the
      :term:`event<Event>` and the :term:`state methods<State Method>` which
      are connected to the method are run in accordance to the :term:`Harel
      Formalism<Harel Formalism>`.  An active object also has a relationship
      with the :term:`active fabric<Active Fabric>`, which is a singleton class
      shared by all active objects.  If the Active Fabric has not been created
      before it is created by the active object.  The active fabric is the
      software which allows all active objects to communicate with all other
      active objects.

   Active Fabric
      A singleton class shared by all :term:`active objects<Active Object>`.
      Through it active objects can :term:`publish<Publish>` and
      :term:`subscribe<Subscribe>` to events created by other active objects.
      It contains two seperate threads (fifo/lifo) each tied to their own
      priority queue.  When an active object publishes to the active fabric, it
      places the event in both priority queues at the priorty set as an
      argument given to the publish call.  If another active object has
      subscribed to that event with the fifo subscription, the active fabric
      will post the event into it's deque using the post_fifo method.  If it
      subscribed using a lifo subscription it will post into it's deque using
      the post_lifo method.

   Factory
      The Factory class inherits from the :term:`active object<Active Object>`
      class and thereby gains all of it's abilities and relationship with the
      Active Fabric.  In addition to this it can be used to manufacture state
      methods and nest them within one another.  It also has a reflection
      feature, ``to_code`` which can be used to show what it's manufactured
      state methods would look like if they were hand crafted.

      To learn about what a Factor is and how to use it, read the :ref:`using
      and unwinding a factory
      example<towardsthefactoryexample-towards-a-factory>`.

   Event
      Any action in the world that your program cares about.  It can be
      triggered by a user, an instrument or internally by an :term:`artificial
      event<Artificial Event>`.  Your program will notice, then react to this
      event by running a subset of your design to manifest the behavior
      described by the chart's structure.  An event is often named something.
      This name is called a :term:`signal<Signal>`.  An event can also carry a
      payload, which can be any data object describable by Python.

      An event can be source from a ``post_fifo`` or ``post_lifo`` or
      ``publish`` or ``dispatch`` call.  An event can have an optional payload
      but it must be created with a :term:`signal<Signal>`.  An event is always the second
      argument of your :term:`state method<State Method>`.

   Signal
      A signal is a common set of enumerations that apply to all sets of
      :term:`events<Event>` within the system.  They are used to catagorize
      events into pools of commmon meaning that can be used by your state
      methods to take action upon.  There are external signals (which you
      define as a user) and internal signals like INIT_SIGNAL, ENTRY_SIGNAL,
      EXIT_SIGNAL .. which are used internally by the event processor
      algorithm.

   Publish
      An active object can publish an event anytime by using the ``publish``
      method.  This will pass the event to the active fabric which will search
      and determine if any other active objects have
      :term:`subscribed<Subscribe>` to the :term:`event<Event>`.  If they have
      it will post this event into their internal queue so that it will be
      consumed during a future :term:`run to completion<Run To Completion>`
      process.

   Subscribe
      A subscription is a multi-statchart concept.  When an active object would
      like to receive and respond to a message provided by another active
      object it can subscribe to the :term:`signal<Signal>` that that event
      will contain.

   Run To Completion
      A run to completion process begins when a statechart receives an event.
      It searches it's local graph and makes a determination if it needs to
      respond, if so it will transition from the local state to the target
      state while adhering to the :term:`Harel Formalism<Harel Formalism>`,
      then it will run the INIT_SIGNAL within that target state.  If that state
      initiations itself by transitioning to another state, the event processor
      will run that transition with the :term:`Harel Formalism<Harel
      Formalism>`.  This will continue until the :term:`statechart<Statechart>`
      has nothing left to do at which point it is finished it's
      run-to-completion processing.  The active objects can not be pre-empted
      with new events while they are in the throes of running through a RTC
      process.  If an event is received it is placed in the queue and it will
      not be considered by the event processor until it's RTC step is
      completed.

   RTC
      :term:`Run To Completion<Run To Completion>`

   Harel Formalism
      The Harel Formalism is a set of rules for describing how events should be
      processed by active objects.  They describe when :term:`internal
      events<Internal Event>` should be send to state methods.  For instance an
      ENTRY_SIGNAL event should be sent to a state method when it's boundary is
      breached from the outside to the inside of the state.  An INIT_SIGNAL
      will be sent to a state method anytime a state has been settled upon.  An
      EXIT_SIGNAL event should be sent to a state method when it's boundary is
      being breached from an inside-to-the-outside.  If a state doesn't know
      how to manage an event it is passed outward to it's parent state.  If
      none of the states within a state machine know how to manage an event,
      it is ignored.

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

      It can be used with the :term:`sequence<Sequence>` tool to generate ASCII sequence
      diagrams.

      You can view the live trace log by using the live trace.  Or you can look
      to what what the log contains using the ``trace`` method.  The trace log
      has a ring buffer which contains 250 spots.

   Sequence
      `Sequence`_ is a tool that consumes trace log strings and
      produces ASCII sequence diagrams.  If the spy log contains the output of
      many different active objects, the sequence tool will create as many
      sequence diagrams as there are active objects in the trace.

   Statechart
      A statechart is a :term:`hierarchical state machine<Hierarchical State
      Machine>` with it's own queue for the events it hasn't reacted against
      yet and a thread in which it can run.  The word was invented by David
      Harel and it is often used as a synonym for :term:`active object<Active
      Object>` or :term:`factory<Factory>` in this documentation. 

   Pattern
      A statechart pattern is an example of how to structure a map with some of
      the features provided by this library to solve a class of problems.

      The idea of a pattern was originally invented by the architect
      Christopher Alexander.

   Event Processor
      The event processor is the code the creates the :term:`Harel
      Formalism<Harel Formalism>`.  It was ported from the work of Miro Samek.
      The library is named miros in honour of his contribution.

   Parent State
      A parent state is a relative term.  For a state to have a parent state it
      must be incircled by that parent state in a Hierarchical State Machine.

   Superstate
      A parent state.

   Substate
      A child state.

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

      A one shot is often used as a kind of delayed :term:`init<Initialization Event>`
      event.  If your statechart needs to settle for a while before it
      continues to the next state consider using a one shot.

   Multi Shot
      A multi shot is sent from a ``post_lifo`` call by setting the ``times``
      argument to how every many events you would like to post (0 for
      infinite).  If you would like to delay the event, set the ``deferred``
      argument to True.  The ``period`` argument is in units of seconds and
      it's value will determine the time delay prior to the event being
      presented to the active object's queue if you have deferred the event.
      It also represents the period of your multishot.

   Client Code
      Any code that you anchor onto your statechart.  It's the code that
      actually solves your business problem.  It is different the the
      statechart code in that it does not describe the structure of the
      hierarchical state machine.

   Orthogonal Region
      A concept taken from the original Harel paper.  To understand what is meant
      by an orthogonal region imagine two statecharts sitting beside one
      another with a bunch of arrows between them. Loosely speaking if your to
      draw a circle around these two statecharts and their arrows, you would be
      describing two orthogonal regions. The word 'orthogonal' comes from
      geometry where it describes a right angle. In the context of physics
      'orthogonal' builds on this right angle idea and it adds the meaning that
      two things do not effect each other that much.

      The problem with orthogonal regions is one of search expense. If you are
      sitting deep within one region and your statechart receives and event which
      should take it deep within the other region, it must first search the chart
      structure to find where it needs to go. The underlying framework within the
      library does this work before it actually starts the exit and entry processing.

      Given that you might be in the inner state of one of your orthogonal regions,
      and you will need to search all the way out of this statechart and reach into
      another; you are wasting cycles and adding a lot of computational complexity to
      your design. This search is handled by the miros package, but your code will
      run a lot slower than it needs to.

      If you find yourself doing this, consider refacting your code using the
      :ref:`reminder pattern<patterns-reminder-here>`.

   Artificial Event
      An artificial event is an event which is made within your active object
      and posted to itself.  An example of an artificial event would be a
      :term:`one shot<One Shot>`.  It is called `artificial` because it is not
      an event that came from outside of the active object in an asynchronous
      way.

      The :ref:`reminder pattern<patterns-reminder-here>` also uses artificial
      events.

   Initialization Event
      The initialization (init) event, is an :term:`internal event<Internal
      Event>` with signal called INIT_SIGNAL.  It is injected into your state
      method when the event processor has settled upon this state after either
      starting within it or finishing a state transition from a called to
      ``trans``.  In UML the init event looks like a big black dot and an arrow
      and it can point to another state, or have some code written directly on
      it.

   Internal Event
      An internal event is an event that is created by the event processor and
      sent to your active object to manifest the :term:`Harel Formalism<Harel
      Formalism>`.  It is different from other events in that you don't have to
      explicitly invent it when you are creating your design.

   HsmTopologyException
      An exception which is raised by the event processor when an INIT_SIGNAL
      event tries to leave the current state.  This exception is often raise
      when the chart is designed incorrectly or when the nest method of the
      factory hasn't ordered the states properly.

   Final State
      A :term:`pseudostate<Pseudostate>` which indicates that an arrow should
      stop processing.

      .. image:: _static/reminder3.svg
          :align: center

   UML
      Universal Modeling Language.  Any drawing referenced in this library is
      intended to be used as a sketch of a design, not as a blue print or as
      the language itself.

   Illegal Transition
      A transition that can not be serviced by the Miro Samek :term:`event
      processor<Event Processor>`.  An example of an illegal transition would
      occur then an INIT_SIGNAL event tries to leave it's current state rather
      than by drilling further into the statechart.  An illegal transition will
      issue a :term:`HsmTopologyException<HsmTopologyException>`

    Ultimate Hook Pattern
      This pattern uses a hook on the outer state of a statechart to provide a
      behavior accessible to all child states.  To learn more about it read
      :ref:`this<patterns-reminder>`.

   Reminder Pattern
      A pattern used to remidy designs which have :term:`orthogonal
      regions<Orthogonal Regions>`.  An :term:`ultimate hook<Ultimate Hook
      Pattern>` is used to inject an :term:`artificial event<Artificial Event>`
      into the statechart.  To learn more about it read
      :ref:`this<patterns-reminder>`.  To see an example click
      :ref:`here<patterns-reminder-here>`.

   Extended State Variables
      This is a variable that can be used by a :term:`state machine<State
      Machine>`.  They are often used in guard conditions.  In the miros
      library the object containing the :term:`event processor<Event
      Processor>`, which are passed into the :term:`state methods<State
      Method>` contain the extended state variables.

      `Extended state`_ variables are used to increase the complexity of a state
      machine without having to add explicit states
      
   Transducer
      A measuring device which converts a physical property (temperature,
      location, acceleration .. etc) into an electrical signal or binary
      number.

   Flat State Method
      A set of :ref:`state methods<recipes-boiler-plate-state-method-code>`
      which use if-elif-else structures to define how they react to various
      events based on the :term:`event<Event>` :term:`signal<Signal>` name.
      The else clause of a flat state method must return the parent state
      otherwise the event processor will not be able to discover the structure
      of your statechart while it is searching your statechart and implmenting
      the :term:`Harel Formalism<Harel Formalism>`.

      A flat state method can be though of in contrast from one made from a
      factory.  The :ref:`to_code<recipes-flatting-a-state-method>` method can
      be used on a factory state method to turn it back into a flat state
      method.

.. _Extended state: https://en.wikipedia.org/wiki/UML_state_machine#Extended_states
.. _Sequence: https://github.com/aleph2c/sequence
