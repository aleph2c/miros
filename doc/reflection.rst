.. _reflection

Reflection
=======================
How to instrument your state charts to you can see what is going on

.. code-block:: python
  :emphasize-lines: 1
  :linenos:
        
    [05:43:06.135566] [75c8c] e->None() top->arming
    [05:43:06.254068] [75c8c] e->BATTERY_CHARGE() arming->armed
    [05:43:06.354835] [75c8c] e->BATTERY_CHARGE() armed->armed
    [05:43:06.456146] [75c8c] e->BATTERY_CHARGE() armed->armed
    [05:43:06.553918] [75c8c] e->CAPACITOR_CHARGE() armed->tazor_operating
    [05:43:06.554796] [75c8c] e->CAPACITOR_CHARGE() tazor_operating->tazor_operating
    [05:43:06.555828] [75c8c] e->CAPACITOR_CHARGE() tazor_operating->tazor_operating

    [ Chart: 75c8c ] (?)
             top                arming                armed           tazor_operating   
              +------None()------->|                    |                    |
              |        (?)         |                    |                    |
              |                    +-BATTERY_CHARGE()-->|                    |
              |                    |        (?)         |                    |
              |                    |                    +                    |
              |                    |                     \ (?)               |
              |                    |                     BATTERY_CHARGE()    |
              |                    |                     /                   |
              |                    |                    <                    |
              |                    |                    +                    |
              |                    |                     \ (?)               |
              |                    |                     BATTERY_CHARGE()    |
              |                    |                     /                   |
              |                    |                    <                    |
              |                    |                    +-APACITOR_CHARGE()->|
              |                    |                    |        (?)         |
              |                    |                    |                    +                    
              |                    |                    |                     \ (?)               
              |                    |                    |                     CAPACITOR_CHARGE()  
              |                    |                    |                     /                   
              |                    |                    |                    <                    
              |                    |                    |                    +                    
              |                    |                    |                     \ (?)               
              |                    |                    |                     CAPACITOR_CHARGE()  
              |                    |                    |                     /                   
              |                    |                    |                    <                    
    
    


.. toctree::
   :maxdepth: 2
   :caption: Contents:
