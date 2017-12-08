To create effective, yet inexpensive documentation, you can :ref:`first obtain
a trace of your system<reflection-a-high-level-description-of-the-behavior>`,
then use it to generate a sequence diagram, with `sequence`_.

Without a lot of effort, you can configure your text editor to write these
pictures for you.  When I select this in my editor:

.. code-block:: python
        
  [2017-11-06 08:34:28.268873] [75c8c] e->start_at() top->arming
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() arming->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() armed->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() armed->armed
  
Then press <ctrl-T>, it becomes this:

.. code-block:: python

  [ Chart: 75c8c ] (?)
       top        arming        armed    
        +-tart_at()->|            |
        |    (?)     |            |
        |            +---BC()---->|
        |            |    (?)     |
        |            |            +            
        |            |             \ (?)       
        |            |             BC()        
        |            |             /           
        |            |            <            


Then I would manually replace the question marks with numbers, so that
I could explained each event by referencing its number.  Since my diagram is in
ASCII, I could place it in my code comments.

`sequence`_ also works with interleaving trace outputs that would come from two
different interacting active objects:

Suppose you got this from your terminal while testing two different
statecharts:

.. code-block:: python
  
  [2017-11-06 08:34:28.268873] [75c8c] e->start_at() top->arming
  [2017-11-06 08:34:28.268873] [95a8c] e->start_at() top->arming
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() arming->armed
  [2017-11-06 08:34:26.312241] [95a8c] e->OTHER() arming->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() armed->armed
  [2017-11-06 08:34:26.312241] [75c8c] e->BC() armed->armed
  [2017-11-06 08:34:26.312241] [95a8c] e->BC() armed->armed
  [2017-11-06 08:34:26.312241] [95a8c] e->BC() armed->armed

By running it through `sequence`_ we would see:

.. code-block:: python
  :emphasize-lines: 17

  [ Chart: 75c8c ] (?)
       top        arming        armed    
        +-tart_at()->|            |
        |    (?)     |            |
        |            +---BC()---->|
        |            |    (?)     |
        |            |            +            
        |            |             \ (?)       
        |            |             BC()        
        |            |             /           
        |            |            <            
  
  [ Chart: 95a8c ] (?)
       top        arming        armed    
        +-tart_at()->|            |
        |    (?)     |            |
        |            +--OTHER()-->|
        |            |    (?)     |
        |            |            +            
        |            |             \ (?)       
        |            |             BC()        
        |            |             /           
        |            |            <            
  
Now I'll write some fake documentation to make a point, notice how I update the
numbers in the diagram:

.. code-block:: python
  :emphasize-lines: 17

  [ Chart: Unit 1 ]
       top        arming        armed    
        +start_at()->|            |
        |    (1)     |            |
        |            +---BC()---->|
        |            |    (3)     |
        |            |            +            
        |            |             \ (5)       
        |            |             BC()        
        |            |             /           
        |            |            <            
  
  [ Chart: Unit 2 ]
       top        arming        armed    
        +start_at()->|            |
        |    (2)     |            |
        |            +--OTHER()-->|
        |            |    (4)     |
        |            |            +            
        |            |             \ (6)       
        |            |             BC()        
        |            |             /           
        |            |            <            


You can gang two tazors together to act as one tazor.  The first arming event
in your tazor network will also arm all of the other tazors, consider the
diagram above to see this interaction.

1.  Tazor labeled 'Unit 1' turns on in the `arming` state.

2.  Tazor labeled 'Unit 2' turns on in the `arming` state.

3.  Unit 1 begins a battery charge (BC) which will send a broadcast message to
    all other tazors in the network.

4.  Unit 2 detects another tazor is beginning a battery charge, so it too begins
    it's battery charge (OTHER)

.... and so on

If I changed the above design, it would be simple to adjust these diagrams and
their description.  Sequence diagrams are great for explaining small things,
but they do break the `DRY`_ principle.  You are effectively replicating your
data by having these descriptions in your documentation.  The source `image` is
your state chart diagram.  Give it a lot of attention, since it is actually
your specification.  The sequence diagrams are little throw away things, that
can be used to assist in telling a very specific story about how your system
behaves.

I'm probably not following the UML standard and I don't care.  The utility of
the sequence diagram picture is in its simplicity.

I know that you can represent loops and object destructor's using these
diagrams, but why bother?  It is easier to write a loop in the code than it is
in a picture, so why not copy and paste the code onto the sequence diagram if
you need to explain a loop?

If you would like to create sequence diagrams that are UML compliant, the
`umlet`_ program supports these features.

.. _sequence: https://github.com/aleph2c/sequence
.. _DRY: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
.. _umlet: http://www.umlet.com/
