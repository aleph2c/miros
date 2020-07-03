.. included from networking_instrumentation
.. added because the table breaks the sphinx code highlighting

+---------------------+-------------------------+-----------------------------------+
|File                 | Where I Ran the Code    |  Purpose                          |
+---------------------+-------------------------+-----------------------------------+
| `c_trace_producer`_ | Run on Raspberry Pi     | To produce spy and trace          |
|                     |                         | information from a statemachine   |
|                     |                         | running on a different computer   |
|                     |                         | than the one monitoring it.       |
+---------------------+-------------------------+-----------------------------------+
| `c_trace_consumer`_ | Run on Window           | To consume, then aggregate all of |
|                     |                         | the spy and trace information     |
|                     |                         | being produced by a foreign       |
|                     |                         | statechart, running on a          |
|                     |                         | different machine.                |
+---------------------+-------------------------+-----------------------------------+
