  *You know you are working with clean code when each routine you read turns out to
  be pretty much what you expected. You can call it beautiful code when the code
  also makes it look like the language was made for the problem.*

  -- Ward Cunningham

.. _towardsthefactoryexample-towards-a-factory:

Using and Unwinding a Factory
=============================

.. image:: _static/factory1.svg
    :target: _static/factory1.pdf
    :align: center

.. _towardsthefactoryexample-example-summary:

Example Summary
---------------
1. :ref:`Standard Approach to Writing State Methods<towardsthefactoryexample-standard-approach>`
2. :ref:`Registering Callbacks to Specific Events<towardsthefactoryexample-registering-callbacks-to-specific-events>`
3. :ref:`Creating a Statechart Using Templates<towardsthefactoryexample-registering-a-parent-to-a-state-method>`
4. :ref:`Creating a Statechart Using A Factory<towardsthefactoryexample-using-the-factory-class>`
5. :ref:`Unwinding a Factory State Method<towardsthefactoryexample-unwinding-a-factory-state-method>`

.. _towardsthefactoryexample-why-you-would-want-a-factory:

In this example I will walk you through how to hand-code a simple state method
then show how that same method could be written for you automatically.  Then I
will show how to re-flatten a statechart, so that you can copy this code back
into your design to make it easier to debug. (Like looking at preprocessor
results in c).

Why a Factory?
--------------
The event processor uses the organization of your state methods, who their
parents are and how they relate to each other as if they defined a complicated
data structure.  These state methods contain your application code too, but
they `are` the nodes of your graph; they define the topology of your
statechart.

When you send an event which will cause a transition across multiple states with
complicated entry/exit/init event triggering to provide the Harel Formalism,
you don't have to worry about how it is implemented, you just need to ensure
that you have framed in your state methods with enough structure that the event
processing algorithm can discover the graph and build out the expected behavior.

This provides the illusion that you are using a completely different type of
programming language, but it's still all Python.  Your state methods are just
being called over and over again with different arguments.

Miro Samek describes this as "an inversion of control".  By using his event
processing algorithm, you are packing the management complexity of the
topological search into the bottom part of your software system.  By pushing
this to the bottom, you can focus on writing concise descriptions of how your
system should behave without concerning yourself with how to implement this
behavior, the algorithm solves that problem.  You just need to build the map.

But to do this, the event processor expects all of your state methods to have a
specific shape.  Their method signatures have to look a certain way and their
if-else structures have to be framed-in just right, otherwise the event
processor will get lost while it's searching for the correct behavior.

Wouldn't it be nice if the library wrote the methods for you too?  Well it can,
you can use a factory to create state method nodes, then link in event
callbacks and assign parents at run time.  The benefit of such an approach is
that you can avoid the strangeness of a state method.  It will become harder
for a maintenance developer to accidentally break your statechart by making
something that looks like an innocuous change.  The factory hides the
topological structure of your state methods behind another layer of
indirection.

However, if you use this library to write your state methods for you, you are
placing yet another layer of abstraction between you and your design.  A bug
might be even harder to find than it was before.  The nice thing about the
state methods is that they are easy to understand, they are flat, and you can
literally see the code and break within it for debugging.  The cognitive
difficulty experienced while trouble shooting a flat state method is much less
than it would be for something that is auto-generated.  


.. _towardsthefactoryexample-standard-approach:

Standard Approach to Writing State Methods
------------------------------------------

.. image:: _static/factory1.svg
    :target: _static/factory1.pdf
    :align: center

To create the above diagram we would define three state methods, ``c``, ``c1``
and ``c2`` and an active object.

.. code-block:: python
  :emphasize-lines: 42
  
  import time
  from miros import spy_on, pp
  from miros import ActiveObject
  from miros import signals, Event, return_status


  @spy_on
  def c(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(c1)
    elif(e.signal == signals.BB):
      status = chart.trans(c)
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status


  @spy_on
  def c1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status


  @spy_on
  def c2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status


  ao = ActiveObject()
  ao.start_at(c2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01) # give your active object a moment to respond
  pp(ao.spy())

An active object has its own thread, so when you want to communicate to it by
posting an event, you have to give it the briefest opportunity to react.
This delay is highlighted in the above code.  

When the above code is run, it would output this to your terminal:

  .. code-block:: python
    :emphasize-lines: 7,14

    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:c2',
     'SEARCH_FOR_SUPER_SIGNAL:c',
     'ENTRY_SIGNAL:c',
     'ENTRY_SIGNAL:c2',
     'INIT_SIGNAL:c2',
     '<- Queued:(0) Deferred:(0)',
     'A:c2',
     'SEARCH_FOR_SUPER_SIGNAL:c1',
     'SEARCH_FOR_SUPER_SIGNAL:c2',
     'EXIT_SIGNAL:c2',
     'ENTRY_SIGNAL:c1',
     'INIT_SIGNAL:c1',
     '<- Queued:(0) Deferred:(0)']

We see from the spy log that we had two run to completion events with no
surprises.  Notice that the event processor tried to call the state functions
with the ``ENTRY_SIGNAL``, ``INIT_SIGNAL`` and ``EXIT_SIGNAL`` as it should
have, even though our state methods did not handle these events.  The handlers
for these events were left out of the state method examples to keep the code
compact.  This demonstrates that the event processor assumes that a missing
handler for ``entry``, ``init`` and ``exit`` signals are handled by a state
method.

.. _towardsthefactoryexample-registering-callbacks-to-specific-events:

Registering Callbacks to Specific Events
----------------------------------------
To build our state method code generation we need to create something that is 
common to all state methods.  The state method does two different things, it
responds to events and it returns parent information.  

To break this down even more, we can say that it does four things.  It asks two
questions and answers two questions.  It asks "How should I respond to the
events that I care about?" and "Who is my parent?".

Then it answers these questions with information specific to that state method.
To make something common across all state methods we can ask the questions but
we can't answer them.  The answers will have to be injected into the state
methods after they have been created.

To be more specific a general state method could look something like this:

.. code-block:: python
  :emphasize-lines: 4-6, 8-11

  @spy_on
  def general_state_method(chart, e):

    # How should I respond to the events that I care about?
    with chart.signal_callback(e, general_state_method) as fn:
      status = fn(chart, e)

    # Who is my parent?
    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

We see that the chart argument provides different context managers,
``signal_callback`` and ``parent_callback``.  It is within these context
managers that the answers are made.

To inject the information into the chart
object so that these context managers have something to answer with we can use the
``register_signal_callback`` and the ``register_parent`` of the active object.

Things should become a bit clearer with an example, reconsider our previous design:

.. image:: _static/factory3.svg
    :target: _static/factory3.pdf
    :align: center


.. code-block:: python
  :emphasize-lines: 4, 16, 28
  
  @spy_on
  def tc(chart, e):

    with chart.signal_callback(e, tc) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc1(chart, e):

    with chart.signal_callback(e, tc1) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc2(chart, e):

    with chart.signal_callback(e, tc2) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

To distinguish these state methods from the previous ones we pre-pend their names
with `t` which stands for template.

These state methods almost look identical, the highlighted lines spell out how
they are different;  the ``signal_callback`` context manager is using the state
method's name to get its information.  Other than that it hardly seems worth
writing out the code three times.

Now we have to give it the information required to perform the actions we want,
first we define some callback methods, then we describe how we want our state
methods to call them.

.. code-block:: python
  :emphasize-lines: 1-11, 13, 15-31

  def trans_to_tc(chart, e):
    return chart.trans(tc)

  def trans_to_tc1(chart, e):
    return chart.trans(tc1)

  def trans_to_tc2(chart, e):
    return chart.trans(tc2)

  def do_nothing(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(tc, signals.BB, trans_to_tc)
  ao.register_signal_callback(tc, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc, signals.INIT_SIGNAL,  trans_to_tc1)
  ao.register_parent(tc, ao.top)

  ao.register_signal_callback(tc1, signals.A, trans_to_tc2)
  ao.register_signal_callback(tc1, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc1, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc1, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc1, tc)

  ao.register_signal_callback(tc2, signals.A, trans_to_tc1)
  ao.register_signal_callback(tc2, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc2, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc2, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc2, tc)

In the first highlighted block we create four different callback methods.  They
have the same method signature as a state method and they work exactly as they
would if they were defined within a state method.

The second block is just an instantiation of an active object, it has the event
processor and it also provides a means to register callback methods for events
and to register a parent state.

The next block shows how are three state methods are given their information.
For instance, the event ``BB`` will cause state ``tc`` to transition to itself.

If we run this code like we did in our previous example we would expect to it
behave the same:

.. code-block:: python

  ao.start_at(tc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)  # give your active object a moment to respond
  pp(ao.spy())

If we ran this code, we would see:

  .. code-block:: python
    :emphasize-lines: 7,14

    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:tc2',
     'SEARCH_FOR_SUPER_SIGNAL:tc',
     'ENTRY_SIGNAL:tc',
     'ENTRY_SIGNAL:tc2',
     'INIT_SIGNAL:tc2',
     '<- Queued:(0) Deferred:(0)',
     'A:tc2',
     'SEARCH_FOR_SUPER_SIGNAL:tc1',
     'SEARCH_FOR_SUPER_SIGNAL:tc2',
     'EXIT_SIGNAL:tc2',
     'ENTRY_SIGNAL:tc1',
     'INIT_SIGNAL:tc1',
     '<- Queued:(0) Deferred:(0)']

.. _towardsthefactoryexample-registering-a-parent-to-a-state-method:

Creating a Statechart Using Templates
-------------------------------------
We pretty much wrote the same method three times in a row in our :ref:`last
example<towardsthefactoryexample-registering-callbacks-to-specific-events>`.
Wouldn't it be nice if something could write the thing for us?  

This is exactly what the ``miros.hsm.state_method_template`` does.

It writes the template code within another function, then copies it so that
this function result is unique in memory, then it renames it and then decorates
it with some instrumentation.

.. code-block:: python

  from miros import spy_on

  def state_method_template(name):

    def base_state_method(chart, e):

      with chart.signal_callback(e, name) as fn:
        status = fn(chart, e)

      if(status == return_status.UNHANDLED):
        with chart.parent_callback(name) as parent:
          status, chart.temp.fun = return_status.SUPER, parent

      return status

    resulting_function = copy(base_state_method)
    resulting_function.__name__ = name
    resulting_function = spy_on(resulting_function)
    return resulting_function

With this method we can automatically write our state methods then register
event callbacks and parent states.

Let's re-create our example, this time using this ``state_method_template``
method:

.. image:: _static/factory4.svg
    :target: _static/factory4.pdf
    :align: center

.. code-block:: python
 
  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # create the states
  fc  = state_method_template('fc')
  fc1 = state_method_template('fc1')
  fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  ao.register_parent(fc, ao.top)

  # write the design information into the fc1 state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  ao.register_parent(fc1, fc)

  # write the design information into the fc2 state
  ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  ao.register_parent(fc2, fc)

  # start up the active object and watch what is does
  ao.start_at(fc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())

This is a much more compact version of our map.  I removed the registration of
signals that weren't being used by the design, but more importantly I used the
``state_method_template`` to create the state methods that could have
information added to them with the active object registration methods.

The output from this program is:

.. code-block:: python
  :emphasize-lines: 7,14

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'ENTRY_SIGNAL:fc2',
   'INIT_SIGNAL:fc2',
   '<- Queued:(0) Deferred:(0)',
   'A:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'EXIT_SIGNAL:fc2',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)']

Which is the expected behavior.

.. _towardsthefactoryexample-using-the-factory-class:

Using the Factory Class
-----------------------
The ``active_object`` module's Factory class provides a syntax which is similar to
the previous miros version.  It has the ``create``, ``catch`` and ``nest``
methods, but it also extends the other API with ``to_method`` and ``to_code``.

The Factory class wraps the ``register_signal_callback`` and
``register_parent`` described in the :ref:`previous
section<towardsthefactoryexample-registering-a-parent-to-a-state-method>`
making syntax that is a bit more concise.

.. image:: _static/factory5.svg
    :target: _static/factory5.pdf
    :align: center

Here is how you could implement this statechart with the ``Factory`` class:

.. code-block:: python
  :emphasize-lines: 15
  :linenos:

  from miros import ActiveObject
  from miros import signals, Event, return_status
  from miros import Factory

  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  chart = Factory('factory_class_example')

  fc = chart.create(state='fc').                             \
    catch(signal=signals.B, handler=trans_to_fc).            \
    catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
    to_method()

  fc1 = chart.create(state='fc1'). \
    catch(signal=signals.A, handler=trans_to_fc2). \
    to_method()

  fc2 = chart.create(state='fc2'). \
    catch(signal=signals.A, handler=trans_to_fc1). \
    to_method()

  chart.nest(fc,  parent=None). \
        nest(fc1, parent=fc). \
        nest(fc2, parent=fc)

  chart.start_at(fc)
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(chart.spy())

If we ran the above code we would see the expected behavior:

.. code-block:: python

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'INIT_SIGNAL:fc',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)',
   'A:fc1',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'EXIT_SIGNAL:fc1',
   'ENTRY_SIGNAL:fc2',
   'INIT_SIGNAL:fc2',
   '<- Queued:(0) Deferred:(0)']


.. _towardsthefactoryexample-unwinding-a-factory-state-method:

Unwinding a Factory State Method
--------------------------------
State methods made from factories are hard to debug because you can't actually
see their code.  If you find that you have an issue with such a state method, you
can unwind it into flat code using the ``to_code`` method.  This method outputs a
string that you can use as a hand written state method.

In the following example, I'll show how we can 'unwind' a design.

.. image:: _static/factory4.svg
    :target: _static/factory4.pdf
    :align: center

First we repeat the work of the last section:

.. code-block:: python
 
  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # create the states
  fc  = state_method_template('fc')
  fc1 = state_method_template('fc1')
  fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  ao.register_parent(fc, ao.top)

  # write the design information into the fc1 state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  ao.register_parent(fc1, fc)

  # write the design information into the fc2 state
  ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  ao.register_parent(fc2, fc)

The ``fc``, ``fc1`` and ``fc2`` objects contain state methods that were
generated by the framework and their code is hidden within the ``ao`` object.

Now suppose something were to go wrong with this design?  An application
developer would have to know that there are at least four different places to
look within the miros framework to understand their state method: the
registration functions, the context managers and in the actual template
generation function.  That would be a lot to keep in their head while they were
also trying to wrestle with their own design problem.

Instead, they could use the ``to_code`` method, copy the result and write it
back into the design as flat state methods.  In this way they could focus their
entire attention on their own issue.  Here is how they could do it:

.. code-block:: python

  print(ao.to_code(fc))
  print(ao.to_code(fc1))
  print(ao.to_code(fc2))

This would output the following:

.. code-block:: python

  @spy_on                                                                                   
  def fc(chart, e):                                                                         
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = trans_to_fc1(chart, e)                                                       
    elif(e.signal == signals.BB):                                                           
      status = trans_to_fc(chart, e)                                                        
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, chart.top                               
    return status                                                                           
                                                                                            
                                                                                            
  @spy_on                                                                                   
  def fc1(chart, e):                                                                        
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.A):                                                            
      status = trans_to_fc2(chart, e)                                                       
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, fc                                      
    return status                                                                           
                                                                                            
                                                                                            
  @spy_on                                                                                   
  def fc2(chart, e):                                                                        
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.A):                                                            
      status = trans_to_fc1(chart, e)                                                       
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, fc                                      
    return status                                                                           
                                                                                          

They could copy these methods and re-write their original code as this, making
sure that the comment out all of the factory code:

.. code-block:: python
  :emphasize-lines: 11-24,27-40,43-56, 58-61, 66-69,71-74,76-78

  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  @spy_on                                                                                   
  def fc(chart, e):                                                                         
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = trans_to_fc1(chart, e)                                                       
    elif(e.signal == signals.BB):                                                           
      status = trans_to_fc(chart, e)                                                        
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, chart.top                               
    return status                                                                           
                                                                                            
                                                                                            
  @spy_on                                                                                   
  def fc1(chart, e):                                                                        
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.A):                                                            
      status = trans_to_fc2(chart, e)                                                       
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, fc                                      
    return status                                                                           
                                                                                            
                                                                                            
  @spy_on                                                                                   
  def fc2(chart, e):                                                                        
    status = return_status.UNHANDLED                                                        
    if(e.signal == signals.ENTRY_SIGNAL):                                                   
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.INIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    elif(e.signal == signals.A):                                                            
      status = trans_to_fc1(chart, e)                                                       
    elif(e.signal == signals.EXIT_SIGNAL):                                                  
      status = return_status.HANDLED                                                        
    else:                                                                                   
      status, chart.temp.fun = return_status.SUPER, fc                                      
    return status                                                                           
                                                                                          
  # create the states
  # fc  = state_method_template('fc')
  # fc1 = state_method_template('fc1')
  # fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  # ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  # ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  # ao.register_parent(fc, ao.top)

  # write the design information into the fc1 state
  # ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  # ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  # ao.register_parent(fc1, fc)

  # write the design information into the fc2 state
  # ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  # ao.register_parent(fc2, fc)

  # start up the active object and watch what it does
  ao.start_at(fc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())

The highlighted sections identify all of the changes to the design.  New
flattened state methods were added and the old factory code was commented out.
If we run this code, we see that it behaves properly:

.. code-block:: python

  ['START',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc',
   'ENTRY_SIGNAL:fc',
   'ENTRY_SIGNAL:fc2',
   'INIT_SIGNAL:fc2',
   '<- Queued:(0) Deferred:(0)',
   'A:fc2',
   'SEARCH_FOR_SUPER_SIGNAL:fc1',
   'SEARCH_FOR_SUPER_SIGNAL:fc2',
   'EXIT_SIGNAL:fc2',
   'ENTRY_SIGNAL:fc1',
   'INIT_SIGNAL:fc1',
   '<- Queued:(0) Deferred:(0)']

Metaprogramming is easy on the person who first writes the code and very hard
on those that have to maintain or extend the design.  Like anything else,
whether it should be done or not is dependent upon the engineering trade offs.

:ref:`back to examples <examples>`
