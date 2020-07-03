.. included from recipes
.. included from reflection

To add messaging to your spy log so that you can see how an activity is
situated within the statechart's behavior, use the ``scribble`` api within your
state method:

.. code-block:: python
  :emphasize-lines: 4,7

  @spy_on
  def s2_state(chart, e):
    def c(chart):
      chart.scribble("running c()")

    def d(chart):
      chart.scribble("running d()")

    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      c(chart)
      status = return_status.HANDLED
    if(e.signal == signals.INIT_SIGNAL):
      d(chart)
      status = chart.trans(s21_state)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status
