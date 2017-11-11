.. included from reflection.rst
.. included from recipes.rst
A signal is the name that can be given to an event.  To get access to your
signals:

.. code-block:: python

  from miros.event import signals

The signals object is provided by a singleton of the SignalSource class, which
is just an OrderedDictionary with a ``__getattr__`` method to make the syntax
easier to use.  

`This basically means that you can think of the signals object as being a dict
that is shared across your whole program.`

To see your signals, you just reflect upon it like you would with any other
Python dictionary:

.. code-block:: python

  # To see your signal names:
  signal_names = signals.keys()

  # To see your signal numbers:
  signal_numbers = signal.values()

  # To output your names and number:
  for signal_name, signal_number in signals.items():
    print(signal_name, signal_number)

  # same output with some formatting
  max_name_len   = len(max(signals, key=len))
  max_number_len = len(str(max(signals.values(), key=int)))
  for signal_name, signal_number in signals.items():
    print("{1: <{0}} {2:{3}}".format(max_name_len, 
                                     signal_name,
                                     signal_number,
                                     max_number_len))  # output below ->
    # ENTRY_SIGNAL            1
    # EXIT_SIGNAL             2
    # INIT_SIGNAL             3
    # REFLECTION_SIGNAL       4
    # SEARCH_FOR_SUPER_SIGNAL 5
    # ..

To compare a received event against a signal, compare the signal numbers:

.. code-block:: python
  :emphasize-lines: 3

  def some_example_state(chart, e):
    status = return_status.UNHANLDED
    if(e.signal == signals.ENTRY_SIGNAL):
      # do something

On lines **1-2** we see standard state method boiler plate code.  On line **3**
we see how to compare the signal numbers against one another to see if they
match.

It you wanted read the signals name as a string, you would call the
``signal_name`` method of the Event class:

.. code-block:: python
  :emphasize-lines: 3

  def some_example_state(chart, e):
    status = return_status.UNHANLDED
    print(e.signal_name) # "ENTRY_SIGNAL"

