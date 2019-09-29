# single_unit_three_stage_charge_1.py
import re
import time
import logging
from functools import partial
from collections import deque
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status
from miros import ThreadSafeAttributes

class ControlSystem:
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None):
    '''Control System

    **Note**:

       (If this was a real system we would SWIG in the c-code used to make the
       control systems work, for now we just pretend this is going to happen so
       that we can continue with our example).

       This class is intended to be subclassed.  At some point we will use it to
       change the reference and control parameters of another control system
       written in c, but SWIG'd into this code base. (we will do this once we
       get the hardware)

       The controller's parameters are wrapped within properties, it is our
       intention to connect these property accesses (getting/setting) to c-code
       which is running on the DSP at 20 Khz.  This Python code will govern the
       parameters and the reference, but the c-code will actually run the
       control systems, setting the output for a given input (which it will
       read).

    **Args**:
       | ``reference=None`` (float): What the controller will force the system towards
       | ``input=None`` (float): The current value of our system
       | ``kp=None`` (float): proportional gain parameter
       | ``ki=None`` (float): integral gain parameter
       | ``kd=None`` (float): differential gain parameter

    **Example(s)**:
      
    .. code-block:: python
       
       class CurrentControlSystem(ControlSystem)
          # ...

    '''
    self._reference = reference
    self._kp = kp
    self._kd = kd
    self._ki = ki
    self._input = input
    self._output = None

  @property
  def reference(self):
    '''framed in so we can call SWIG'd code later'''
    return self._reference

  @reference.setter
  def reference(self, value):
    '''framed in so we can call SWIG'd code later'''
    self._reference = value

  @property
  def kp(self):
    '''framed in so we can call SWIG'd code later'''
    return self._kp

  @kp.setter
  def reference(self, value):
    '''framed in so we can call SWIG'd code later'''
    self._kp = value

  @property
  def ki(self):
    '''framed in so we can call SWIG'd code later'''
    return self._ki

  @ki.setter
  def reference(self, value):
    '''framed in so we can call SWIG'd code later'''
    self._ki = value

  @property
  def kd(self):
    '''framed in so we can call SWIG'd code later'''
    return self._kd

  @kd.setter
  def reference(self, value):
    '''framed in so we can call SWIG'd code later'''
    self._kd = value

  @property
  def output(self):
    '''framed in so we can call SWIG'd code later'''
    return self._output


class CurrentControlSystem(ControlSystem):
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None):
    '''The Current Control System

    **Note**:
      This PID control system will pass on it's reference and parameters to the
      c-written control system, SWIG'd into our system.  This class will not
      directly control the current, but it will provide the targets and control
      parameters to the c-written control system which will be responsible for
      control the charger's current.

    **Args**:
       | ``reference=None`` (float): What the controller will force the system towards
       | ``input=None`` (float): The current value of our system
       | ``kp=None`` (float): proportional gain parameter
       | ``ki=None`` (float): integral gain parameter
       | ``kd=None`` (float): differential gain parameter

    **Example(s)**:
      
    .. code-block:: python
       
      ccs = CurrentControlSystem(
        reference=50.0,
        kp=0.5,
        ki=0.03,
        kd=0.04)

    '''
    super().__init__(
      reference=reference, 
      input=input,
      kp=kp,
      ki=ki,
      kd=kd
    )

class VoltageControlSystem(ControlSystem):
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None):
    '''The Voltage Control System

    **Note**:
      This PID control system will pass on it's reference and parameters to the
      c-written control system, SWIG'd into our system.  This class will not
      directly control the current, but it will provide the targets and control
      parameters to the c-written control system which will be responsible for
      control the charger's current.

    **Args**:
       | ``reference=None`` (float): What the controller will force the system towards
       | ``input=None`` (float): The current value of our system
       | ``kp=None`` (float): proportional gain parameter
       | ``ki=None`` (float): integral gain parameter
       | ``kd=None`` (float): differential gain parameter

    **Example(s)**:
      
    .. code-block:: python
       
      ccs = VoltageControlSystem(
        reference=48.0,
        kp=0.5,
        ki=0.02,
        kd=0.005)
    '''
    super().__init__(
      reference=reference, 
      input=input,
      kp=kp,
      ki=ki,
      kd=kd
    )

class BatterySpecificationSettings:
  def __init__(self,
      bulk_timeout_sec=None,
      abs_timeout_sec=None,
      equ_timeout_sec=None,
      bulk_entry_volts=None,
      bulk_exit_volts=None,
      abs_exit_amps=None,
      bulk_ref_amps=None,
      float_ref_volts=None,
      abs_ref_volts=None,
      equ_ref_volts=None):
    '''The battery specification setting for the three stage charger.

    **Args**:
       | ``bulk_timeout_sec=None`` (float): Maximum time in the bulk stage
       | ``abs_timeout_sec=None`` (float):  Maximum time in the absorption stage
       | ``equ_timeout_sec=None`` (float):  Maximum time in the equalization
       |                                    stage
       | ``bulk_entry_volts=None`` (float): Voltage under-which we force a
       |                                    transition into the bulk charging
       |                                    stage
       | ``bulk_exit_volts=None`` (float):  Voltage over-which we transition to
       |                                    absorption stage
       | ``abs_exit_amps=None`` (float):    Current over-which we transition to float
       | ``bulk_ref_amps=None`` (float):    Constant current value driven into
       |                                    battery during the bulk stage
       | ``float_ref_volts=None`` (float):   Constant voltage value expressed
       |                                    across battery terminal during float
       |                                    stage
       | ``abs_ref_volts=None`` (float):    Constant voltage value expressed
       |                                    across battery terminal during
       |                                    absorption stage
       | ``equ_ref_volts=None`` (float):    Constant voltage value expressed
       |                                    across battery terminal during
       |                                    equalization stage


    **Returns**:
       (BatterySpecificationSettings):  this obj

    **Example(s)**:
      
    .. code-block:: python

      batt_spec = BatterySpecificationSettings(
        bulk_timeout_sec=700,
        abs_timeout_sec=900,
        equ_timeout_sec=86400,
        bulk_entry_volts=18.0,
        bulk_exit_volts=28.0,
        abs_exit_amps=12,
        bulk_ref_amps=240,
        float_ref_volts=24.0,
        abs_ref_volts=28.0,
        equ_ref_volts=30.0)

    '''

class ChargerParameters(ThreadSafeAttributes):

  _attributes = ['c_control', 'v_control', 'battery_spec']

  def __init__(self, c_control=None, v_control=None, battery_spec=None, **kwargs):
    '''Battery Charger Parameters

    **Args**:
       | ``c_control`` (CurrentControlSystem): The current PID parameters
       | ``v_control`` (VoltageControlSystem): The voltage PID parameters
       | ``battery_spec`` (BatterySpecificationSettings):  The battery specific settings 

    **Returns**:
       (ChargerParameters): 

    **Example(s)**:
      
    .. code-block:: python
       
      ccs = CurrentControlSystem(
        reference=50.0,
        kp=0.5,
        ki=0.03,
        kd=0.04)

      vcs = VoltageControlSystem(
        reference=48.0,
        kp=0.5,
        ki=0.02,
        kd=0.005)

      battery_spec = BatterySpecificationSettings(
        bulk_timeout_sec=700,
        abs_timeout_sec=900,
        equ_timeout_sec=86400,
        bulk_entry_volts=18.0,
        bulk_exit_volts=28.0,
        abs_exit_amps=12,
        bulk_ref_amps=240,
        float_ref_volts=24.0,
        abs_ref_volts=28.0,
        equ_ref_volts=30.0):

      charge_params = ChargerParameters(
        c_control=ccs,
        v_control=vcs,
        battery_spec=battery_spec)

    '''
    self.c_control = c_control
    self.v_control = v_control
    self.battery_spec = battery_spec

class CustomFactory(Factory, ThreadSafeAttributes):
  # we will add our custom logging for the live_trace and live_spy here
  def __init__(self, name=None, live_trace=None, live_spy=None, **kwargs):
    super().__init__(name)

class Charger(ChargerParameters, CustomFactory):

  # The charger will be multithreaded, provide simple locks around data accesses
  # to these attributes
  _attributes = [
    'amps',
    'volts',
    'sec',
    'control',
  ]

  def __init__(self, name=None, charger_params=None, live_trace=None,
      live_spy=None, pulse_sec=None):
    '''Three stage battery charger feature management

    This class will manage the data and the behavior of our three stage battery
    charger.  The control systems used by the charge will be written in c, but
    the reference and turning parameters of these controllers will be accessible
    to this python code via SWIG.

    To understand this class reference
    
      1) the three stage charging electrical profile drawing:

      2) the three stage charging data architecture drawing:

      3) the three stage charging state chart drawing:

    **Args**:
       | ``name`` (str): name of the charging state chart
       | ``charger_params=None`` (ChargerParameters):  parameters/controller
       |                                               needed by charger
       | ``live_trace=None(bool)``: enable live_trace feature?
       | ``live_spy=None(bool)``: enable live_spy feature?
       | ``pulse_sec=None``(float): how often to same current/voltage and make
       |                            decisions about state changes

    **Example(s)**:
      
    .. code-block:: python
     
      ccs = CurrentControlSystem(# ...)
      vcs = VoltageControlSystem(# ...)
      battery_spec = BatterySpecificationSettings(# ...)
      charge_params = ChargerParameters(
        c_control=ccs,
        v_control=vcs,
        battery_spec=battery_spec)

      three_stage_charger = Charger(
        'charger',
        charger_params=charger_params,
        live_trace=True)

    '''
    self.pulse_sec = 0.5 if pulse_sec is None else pulse_sec

    # build a default charger
    if charger_params is None:
      c_control = CurrentControlSystem(
        reference=50.0,
        kp=0.5,
        ki=0.03,
        kd=0.04
      )

      v_control = VoltageControlSystem(
        reference=12.0,
        kp=0.5,
        ki=0.02,
        kd=0.005
      )

      battery_spec = BatterySpecificationSettings(
        bulk_timeout_sec=700,
        abs_timeout_sec=900,
        equ_timeout_sec=86400,
        bulk_entry_volts=18.0,
        bulk_exit_volts=28.0,
        abs_exit_amps=12,
        bulk_ref_amps=240,
        float_ref_volts=24.0,
        abs_ref_volts=28.0,
        equ_ref_volts=30.0
      )
    else:
      c_control = charger_params.c_control
      v_control = charger_params.v_control
      battery_spec = charger_params.battery_spec

    super().__init__(name=name, 
        c_control=c_control, 
        v_control=v_control,
        battery_spec=battery_spec,
        live_trace=live_trace,
        live_spy=live_spy
    )

  def sample_current(self):
    pass

  def sample_voltage(self):
    pass

if __name__ == '__main__':
 
  # current control system
  ccs = CurrentControlSystem(
    reference=50.0,  # 50 amps
    kp=0.5,
    ki=0.03,
    kd=0.04
  )

  # voltage control system
  vcs = VoltageControlSystem(
    reference=12.0, # 12 volts
    kp=0.4,
    ki=0.02,
    kd=0.005
  )

  # battery specification
  battery_spec = BatterySpecificationSettings(
    bulk_timeout_sec=700,
    abs_timeout_sec=900,
    equ_timeout_sec=86400,
    bulk_entry_volts=18.0,
    bulk_exit_volts=28.0,
    abs_exit_amps=12,
    bulk_ref_amps=240,
    float_ref_volts=24.0,
    abs_ref_volts=28.0,
    equ_ref_volts=30.0
  )

  # aggregated charger paramters
  charger_params = ChargerParameters(
    c_control=ccs,
    v_control=vcs,
    battery_spec=battery_spec
  )

  # the charger data and behavior
  three_stage_charger = Charger(
    name='charger',
    charger_params=charger_params,
    live_trace=True
  )
