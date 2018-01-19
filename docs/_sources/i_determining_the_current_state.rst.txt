To see what state your chart is in:

.. code-block:: python
  :emphasize-lines: 1,2

    # state name as a string
    chart.state_name

    # state as a function
    chart.state_fn

.. note::
  This will only work if you have wrapped your statemethod with a ``@spy_on``
  decorator or if you have constructed your statechart with the Factory class.
