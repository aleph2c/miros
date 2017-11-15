.. _towardsthefactoryexample-towards-a-factory:

Using and Unwinding a Factory
=============================

.. image:: _static/factory1.svg
    :align: center

.. _towardsthefactoryexample-example-summary:

Example Summary
---------------
1. :ref:`Write a standard flat version of a statechart<towardsthefactoryexample-standard-approach>`
2. :ref:`Re-write the state methods so that you can register callbacks with specific
   events.<towardsthefactoryexample-registering-callbacks-to-specific-events>`
3. :ref:`Re-write the state methods so that you can register a parent with
   them<towardsthefactoryexample-registering-a-parent-to-a-state-method>`
4. :ref:`Remove the need to explicitly write a number of state methods, instead, we
   can get them from a template
   function<towardsthefactoryexample-building-a-method-to-build-state-methods>`
5. :ref:`Use the miros factory
   methods<towardsthefactoryexample-using-the-miros-factory-method>`
6. :ref:`Use miros to convert it's factory method into a flat version of a state
   function for
   debugging.<towardsthefactoryexample-unwinding-a-factory-state-method>`

.. _towardsthefactoryexample-why-you-would-want-a-factory:

Why a Factory?
--------------

The event processor used to create the dynamics of your statechart expects all
of your state methods to have a specific shape.  Their method signatures have
to look a certain way and their if-else structures have to be framed-in just
right, otherwise the event processor might get lost while it's searching for
the correct behavior.

The event processor provides the illusion that you are using a completely
different type of programming language, but it's still all Python.  Your state
methods are just being called over and over again with different arguments.

Miro Samek describes this as "an inversion of control".  By using his event
processor algorithm, you are packing the management of the topological search
complexity into the bottom of your software system.

The beautiful thing about the framework is that a state method only has to
describe which other state method is it's parent.  Then when the event
processor is called, it will look at the current state and
recurse over your state methods determining how and when each of your state
methods should be called in accordance to the Harel Formalism.  You don't
have to worry about how this is done, you just have to remember how the maps
behave, then translate your map into state methods.

The cost of this is that you have to express your application code within
*specifically* structured state methods.  Wouldn't it be nice if the library
wrote the methods for you too?  Well, it can do that using the factory pattern,
but let's consider the downside of structuring your application like this.

If you use this library to write your state methods for you, you are placing
yet another layer of abstraction between you and your application code.  A bug
might be even harder to find than it was before.  The nice thing about the
state methods is that they are easy to understand, they are flat,
and you can literally see the code and break within it for debugging.  The
cognitive load experienced while trouble shooting a flat state method is much
less than it would be for something that is auto-generated.

In this example I will walk you through how we can move from a simple state
method towards one that is written for you automatically.  I will also describe
fusion state methods which use both techniques and thereby allow you to
register event callbacks while your code is executing and why you might want
to do this.

I will also describe how to create a state method using a factory, then how to
ask the framework to print out what that code would look like if it were
hard-coded into your project.  I will then demonstrate a technique of unwinding
a complicated design, into such flat methods, so that you can 'see' what is
going on.

.. _towardsthefactoryexample-standard-approach:

Standard Approach
-----------------

.. _towardsthefactoryexample-registering-callbacks-to-specific-events:

Registering Callbacks to Specific Events
----------------------------------------

.. _towardsthefactoryexample-registering-a-parent-to-a-state-method:

Registering a Parent to a State Method
--------------------------------------

.. _towardsthefactoryexample-building-a-method-to-build-state-methods:

Building a Method to Build State Methods
----------------------------------------

.. _towardsthefactoryexample-using-the-miros-factory-method:

Using the Miros Factory Method
------------------------------

.. _towardsthefactoryexample-unwinding-a-factory-state-method:

Unwinding a Factory State Method
--------------------------------




