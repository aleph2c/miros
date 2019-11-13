# single_unit_three_stage_charge_2.py
import re
import time
import logging
from functools import partial
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status
from miros import ThreadSafeAttributes

class ControlSystem:
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None,
      current_clamp_amps=None, voltage_clamp_volts=None):
    '''Control System

    **Note**:

       (If this was a real system we would SWIG in the c-code used to make
       the control systems work, for now we just pretend this is going to
       happen so that we can continue with our example).

       This class is intended to be subclassed.  At some point we will use
       it to change the reference and control parameters of another control
       system written in c, but SWIG'd into this code base. (we will do
       this once we get the hardware)

       The controller's parameters are wrapped within properties, it is our
       intention to connect these property accesses (getting/setting) to
       c-code which is running on the DSP at 20 Khz.  This Python code will
       govern the parameters and the reference, but the c-code will
       actually run the control systems, setting the output for a given
       input (which it will read).

    **Args**:
       | ``reference=None`` (float): 
       |     What the controller will force the system towards
       | ``input=None`` (float): 
       |     The current value of our system
       | ``kp=None`` (float): 
       |     Proportional gain parameter
       | ``ki=None`` (float): 
       |     Integral gain parameter
       | ``kd=None`` (float): 
       |     Differential gain parameter
       | ``current_clamp_amps=None`` (float): 
       |     Maximum current we want while unit under control
       | ``voltage_clamp_volts=None`` (float): 
       |     Maximum voltage we want while unit under control

    '''
    self._reference = reference
    self._kp = kp
    self._kd = kd
    self._ki = ki
    self._input = input
    self._output = None
    self._current_clamp_amps = current_clamp_amps
    self._voltage_clamp_volts = voltage_clamp_volts

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

  @property
  def current_clamp_amps(self):
    return self._current_clamp_amps

  @current_clamp_amps.setter
  def current_clamp_amps(self, value):
    self._current_clamp_amps = value

  @property
  def voltage_clamp_volts(self):
    return self._voltage_clamp_volts

  @voltage_clamp_volts.setter
  def voltage_clamp_volts(self, value):
    self._voltage_clamp_volts = value

class CurrentControlSystem(ControlSystem):
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None,
      current_clamp_amps=None, voltage_clamp_volts=None):
    '''The Current Control System

    **Note**:
      This PID control system will pass on it's reference and parameters to
      the c-written control system, SWIG'd into our system.  This class
      will not directly control the current, but it will provide the
      targets and control parameters to the c-written control system which
      will be responsible for control the charger's current.

    **Args**:
       | ``reference=None`` (float): 
       |     What the controller will force the system towards
       | ``input=None`` (float): 
       |     The current value of our system
       | ``kp=None`` (float): 
       |     Proportional gain parameter
       | ``ki=None`` (float): 
       |     Integral gain parameter
       | ``kd=None`` (float): 
       |     Differential gain parameter
       | ``current_clamp_amps=None`` (float): 
       |     Maximum current we want while unit under control
       | ``voltage_clamp_volts=None`` (float): 
       |     Maximum voltage we want while unit under control

    **Example(s)**:
      
    .. code-block:: python
       
      ccs = CurrentControlSystem(
        reference=50.0,
        kp=0.5,
        ki=0.03,
        kd=0.04,
        voltage_clamp_volts=18.0,
        current_clamp_amps=100.0
        )

    '''
    super().__init__(
      reference=reference, 
      input=input,
      kp=kp,
      ki=ki,
      kd=kd, 
      current_clamp_amps=current_clamp_amps,
      voltage_clamp_volts=voltage_clamp_volts,
    )

class VoltageControlSystem(ControlSystem):
  def __init__(self, reference=None, input=None, kp=None, ki=None, kd=None, 
      current_clamp_amps=None, voltage_clamp_volts=None):
    '''The Voltage Control System

    **Note**:
      This PID control system will pass on it's reference and parameters to
      the c-written control system, SWIG'd into our system.  This class
      will not directly control the current, but it will provide the
      targets and control parameters to the c-written control system which
      will be responsible for control the charger's current.

    **Args**:
       | ``reference=None`` (float): 
       |     What the controller will force the system towards
       | ``input=None`` (float): 
       |     The current value of our system
       | ``kp=None`` (float): 
       |     Proportional gain parameter
       | ``ki=None`` (float): 
       |     Integral gain parameter
       | ``kd=None`` (float): 
       |     Differential gain parameter
       | ``current_clamp_amps=None`` (float): 
       |     Maximum current we want while unit under control
       | ``voltage_clamp_volts=None`` (float): 
       |     Maximum voltage we want while unit under control

    **Example(s)**:
      
    .. code-block:: python
       
      ccs = VoltageControlSystem(
        reference=48.0,
        kp=0.5,
        ki=0.02,
        kd=0.005,
        current_clamp_amps=100.0,
        voltage_clamp_volts=18.0,
        )
    '''
    super().__init__(
      reference=reference, 
      input=input,
      kp=kp,
      ki=ki,
      kd=kd,
      current_clamp_amps=current_clamp_amps,
      voltage_clamp_volts=voltage_clamp_volts,
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
       | ``bulk_timeout_sec=None`` (float): 
       |     Max time in the bulk stage
       | ``abs_timeout_sec=None`` (float): 
       |     Max time in the absorption stage
       | ``equ_timeout_sec=None`` (float):  
       |     Max time in the equalization stage
       | ``bulk_entry_volts=None`` (float): 
       |     Voltage under-which we force a transition into 
       |     the bulk charging stage
       | ``bulk_exit_volts=None`` (float):  
       |     Voltage over-which we transition to absorption stage
       | ``abs_exit_amps=None`` (float):
       |     Current over-which we transition to float
       | ``bulk_ref_amps=None`` (float):
       |     Constant current value driven into battery during the bulk
       |     stage
       | ``float_ref_volts=None`` (float): 
       |     Constant voltage value expressed across battery terminal
       |     during float stage
       | ``abs_ref_volts=None`` (float): 
       |     Constant voltage value expressed across battery terminal
       |     during absorption stage
       | ``equ_ref_volts=None`` (float): 
       |     Constant voltage value expressed across battery terminal
       |     during equalization stage

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
    self.bulk_timeout_sec = bulk_timeout_sec
    self.abs_timeout_sec = abs_timeout_sec
    self.equ_timeout_sec = equ_timeout_sec
    self.bulk_entry_volts = bulk_entry_volts
    self.bulk_exit_volts = bulk_exit_volts
    self.abs_exit_amps = abs_exit_amps
    self.bulk_ref_amps = bulk_ref_amps
    self.float_ref_volts = float_ref_volts
    self.abs_ref_volts = abs_ref_volts
    self.equ_ref_volts = equ_ref_volts

class ChargerParameters(ThreadSafeAttributes):

  _attributes = ['c_control', 'v_control', 'battery_spec']

  def __init__(self, 
    *args, 
    c_control=None, 
    v_control=None,
    battery_spec=None,
    **kwargs):
    '''Battery Charger Parameters

    **Args**:
       | ``c_control`` (CurrentControlSystem): The current PID parameters
       | ``v_control`` (VoltageControlSystem): The voltage PID parameters
       | ``battery_spec`` (BatterySpecificationSettings):  The battery
       |                                                   specific
       |                                                   settings 

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
    super().__init__(*args, **kwargs)
    self.c_control = c_control
    self.v_control = v_control
    self.battery_spec = battery_spec

class LoggedBehavior(Factory):
  def __init__(self, 
      name, 
      log_file=None, 
      live_trace=None, 
      live_spy=None, 
      **kwargs):

    super().__init__(name, *kwargs)

    self.live_trace = False \
      if live_trace == None else live_trace

    self.live_spy = False \
      if live_spy == None else live_spy

    self.log_file = 'single_unit_three_stage_charger.log' \
      if log_file == None else log_file

    ## clear our old log file
    #with open(self.log_file, "w") as fp:
    #  fp.write("")

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=self.log_file,
      level=logging.DEBUG)

    self.register_live_spy_callback(
      partial(self.spy_callback)
    )
    self.register_live_trace_callback(
      partial(self.trace_callback)
    )

  def trace_callback(self, trace):
    '''trace without datetimestamp'''
    trace_without_datetime = \
      re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pending'''
    logging.debug("S: [{}] {}".format(self.name, spy))

SecInCharge = namedtuple('SecInCharge', ['sec'])
DriveCurrent = namedtuple('DriveCurrent', ['amps', 'control', 'sec', 'cause'])
DriveVoltage = namedtuple('DriveVoltage', ['volts', 'control', 'sec', 'cause'])
Sampler = namedtuple('Sampler', ['fn'])

class Charger(ChargerParameters, LoggedBehavior, ThreadSafeAttributes):

  # The charger will be multithreaded, provide simple locks around data
  # accesses to these attributes
  _attributes = [
    'amps',
    'volts',
    'sec',
    'control',
  ]

  def __init__(self, name=None, charger_params=None, live_trace=None,
      live_spy=None, pulse_sec=None):
    '''Three stage battery charger feature management

    This class will manage the data and the behavior of our three stage
    battery charger.  The control systems used by the charge will be
    written in c, but the reference and turning parameters of these
    controllers will be accessible to this python code via SWIG.

    To understand this class reference:
    
      1) the three stage charging electrical profile drawing:
        `link <https://aleph2c.github.io/miros/_static/three_stage_charging_chart_4_graph.pdf>`_

      2) the three stage charging data architecture drawing:
        `link <https://aleph2c.github.io/miros/_static/three_stage_charging_chart_5_data.pdf>`_

      3) the three stage charging state chart drawing:
        `link <https://aleph2c.github.io/miros/_static/three_stage_charging_chart_5_chart.pdf>`_

    **Args**:
       | ``name`` (str): name of the charging state chart
       | ``charger_params=None`` (ChargerParameters):  
       |                           parameters/controller
       |                           needed by charger
       | ``live_trace=None(bool)``: enable live_trace feature?
       | ``live_spy=None(bool)``: enable live_spy feature?
       | ``pulse_sec=None``(float): 
       |                        how often to same current/voltage and make
       |                        decisions about state changes

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
    self.pulse_sec = 1.0 if pulse_sec is None else pulse_sec
    self.cause = None

    c_control = charger_params.c_control
    v_control = charger_params.v_control
    battery_spec = charger_params.battery_spec

    self._fn_sample_current = None
    self._fn_sample_voltage = None

    super().__init__(
      name=name, 
      live_trace=live_trace,
      live_spy=live_spy,
      c_control=c_control, 
      v_control=v_control,
      battery_spec=battery_spec,
    )

    self.wait_for_electrical_interface = self.create(state="wait_for_electrical_interface"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.wait_for_electrical_interface_entry_signal). \
      catch(signal=signals.SET_CURRENT_SAMPLER,
        handler=self.wait_for_electrical_interface_current_sampler). \
      catch(signal=signals.SET_VOLTAGE_SAMPLER,
        handler=self.wait_for_electrical_interface_voltage_sampler). \
      catch(signal=signals.turn_on_charger,
        handler=self.wait_for_electrical_interface_turn_on_charger). \
      to_method()

    self.charging = self.create(state="charging"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.charging_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.charging_init_signal). \
      catch(signal=signals.SET_CURRENT_SAMPLER,
        handler=self.charging_set_current_sampler). \
      catch(signal=signals.SET_VOLTAGE_SAMPLER,
        handler=self.charging_set_voltage_sampler). \
      catch(signal=signals.Pulse,
        handler=self.charging_pulse). \
      catch(signal=signals.To_Bulk,
        handler=self.charging_to_bulk). \
      catch(signal=signals.Force_Bulk,
        handler=self.charging_force_bulk). \
      catch(signal=signals.To_Abs,
        handler=self.charging_to_abs). \
      catch(signal=signals.Force_Abs,
        handler=self.charging_force_abs). \
      catch(signal=signals.To_Float,
        handler=self.charging_to_float). \
      catch(signal=signals.Force_Float,
        handler=self.charging_force_float). \
      catch(signal=signals.Force_Equ,
        handler=self.charging_force_equ). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.charging_exit_signal). \
      to_method()

    self.constant_current_control = \
      self.create(state="constant_current_control"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.constant_current_control_entry_signal). \
        catch(signal=signals.electrical_change,
          handler=self.constant_current_control_electrical_change). \
      to_method()

    self.constant_voltage_control = \
      self.create(state="constant_voltage_control"). \
        catch(signal=signals.ENTRY,
          handler=self.constant_voltage_control_entry). \
        catch(signal=signals.electrical_change,
          handler=self.constant_voltage_control_electrical_change). \
      to_method()

    self.bulk = self.create(state="bulk"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.bulk_entry_signal). \
      catch(signal=signals.To_Bulk,
        handler=self.bulk_to_bulk). \
      catch(signal=signals.Tick,
        handler=self.bulk_tick). \
      to_method()

    self.absorption = self.create(state="absorption"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.absorption_entry_signal). \
      catch(signal=signals.Tick,
        handler=self.absorption_tick). \
      to_method()

    self.float = self.create(state="float"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.float_entry). \
      catch(signal=signals.Tick,
        handler=self.float_tick). \
      to_method()

    self.equalize = self.create(state="equalize"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.equalize_entry_signal). \
      catch(signal=signals.Tick,
        handler=self.equalize_tick). \
      to_method()

    self.nest(self.wait_for_electrical_interface, parent=None). \
      nest(self.charging, parent=self.wait_for_electrical_interface). \
      nest(self.constant_current_control, parent=self.charging). \
      nest(self.constant_voltage_control, parent=self.charging). \
      nest(self.bulk, parent=self.constant_current_control). \
      nest(self.absorption, parent=self.constant_voltage_control). \
      nest(self.float, parent=self.constant_voltage_control). \
      nest(self.equalize, parent=self.constant_voltage_control)

  def start(self):
    self.start_at(self.wait_for_electrical_interface)
    return self

  def wait_for_electrical_interface_entry_signal(self, e):
    status = return_status.HANDLED
    self._fn_sample_current = None
    self._fn_sample_voltage = None
    self.subscribe(Event(signal=signals.SET_CURRENT_SAMPLER))
    self.subscribe(Event(signal=signals.SET_VOLTAGE_SAMPLER))
    self.publish(Event(signal=signals.REQUEST_FOR_SAMPLERS))
    return status

  def wait_for_electrical_interface_current_sampler(self, e):
    status = return_status.HANDLED
    self._fn_sample_current = e.payload.fn
    if self._fn_sample_voltage != None:
      self.post_fifo(Event(signal=signals.turn_on_charger))
    return status

  def wait_for_electrical_interface_voltage_sampler(self, e):
    status = return_status.HANDLED
    self._fn_sample_voltage = e.payload.fn
    if self._fn_sample_current != None:
      self.post_fifo(Event(signal=signals.turn_on_charger))
    return status

  def wait_for_electrical_interface_turn_on_charger(self, e):
    status = self.trans(self.charging)
    return status

  def charging_entry_signal(self, e):
    status = return_status.HANDLED
    self.sec = 0
    self.post_fifo(Event(signal=signals.Pulse),
      deferred=True,
      period=self.pulse_sec,
      times=0)
    return status

  def charging_init_signal(self, e):
    status = self.trans(self.constant_current_control)
    return status

  def charging_set_current_sampler(self, e):
    status = return_status.HANDLED
    self._fn_sample_current = e.payload.fn
    return status

  def charging_set_voltage_sampler(self, e):
    status = return_status.HANDLED
    self._fn_sample_voltage = e.payload.fn
    return status

  def charging_pulse(self, e):
    status = return_status.HANDLED
    self.amps = self._fn_sample_current()
    self.volts = self._fn_sample_voltage()
    if(self.volts < self.battery_spec.bulk_entry_volts):
      self.post_fifo(Event(signal=signals.To_Bulk))
    self.sec += self.pulse_sec
    self.post_fifo(Event(signal=signals.Tick,
      payload=SecInCharge(sec=self.sec)))
    return status

  def charging_to_bulk(self, e):
    status = self.trans(self.bulk)
    return status

  def charging_force_bulk(self, e):
    status = self.trans(self.bulk)
    return status

  def charging_to_abs(self, e):
    status = self.trans(self.absorption)
    return status

  def charging_force_abs(self, e):
    status = self.trans(self.absorption)
    return status

  def charging_to_float(self, e):
    status = self.trans(self.float)
    return status

  def charging_force_float(self, e):
    status = self.trans(self.float)
    return status

  def charging_force_equ(self, e):
    status = self.trans(self.equalize)
    return status

  def charging_exit_signal(self, e):
    status = return_status.HANDLED
    self.cancel_events(Event(signal=signals.Pulse))
    return status

  def constant_current_control_entry_signal(self, e):
    status = return_status.HANDLED
    self.control = self.c_control
    return status

  def constant_current_control_electrical_change(self, e):
    status = return_status.HANDLED
    self.publish(
      Event(
        signal=signals.DRIVE_CURRENT,
        payload=DriveCurrent(
          amps=self.control.reference,
          control=self.control,
          sec=self.sec,
          cause=self.cause,
        )
      )
    )
    return status

  def constant_voltage_control_entry(self, e):
    status = return_status.HANDLED
    self.control = self.c_voltage
    return status

  def constant_voltage_control_electrical_change(self, e):
    status = return_status.HANDLED
    self.publish(
      Event(
        signal=signals.DRIVE_VOLTAGE,
        payload=DriveVoltage(
          volts=self.control.reference,
          control=self.control,
          sec=self.sec,
          cause=self.cause,
        )
      )
    )
    return status

  def bulk_entry_signal(self, e):
    status = return_status.HANDLED
    self.control.reference = self.battery_spec.bulk_ref_amps
    self.start_sec = self.sec
    self.post_fifo(Event(signal=signals.electrical_change))
    self.cause = self.state_name
    return status

  def bulk_to_bulk(self, e):
    status = return_status.HANDLED
    return status

  def bulk_tick(self, e):
    status = return_status.HANDLED
    if (e.payload.sec - self.start_sec >
       self.battery_spec.bulk_timeout_sec) or \
       ( self.volts > self.battery_spec.bulk_exit_volts):
      self.post_fifo(Event(signal=signals.To_Abs))
    return status

  def absorption_entry_signal(self, e):
    status = return_status.HANDLED
    self.control.reference = \
      self.battery_spec.abs_ref_volts
    self.start_sec = self.sec
    self.cause = self.state_name
    self.post_fifo(Event(signal=signals.electrical_change))
    return status

  def absorption_tick(self, e):
    status = return_status.HANDLED
    if(e.payload.sec - self.start_sec > self.battery_spec.abs_timeout_sec) or \
      (self.amps <= self.battery_spec.abs_exit_amps):
      self.post_fifo(Event(signal=signals.To_Float))
    return status

  def float_entry(self, e):
    status = return_status.HANDLED
    self.control.reference = self.battery_spec.float_ref_volts
    self.cause = self.state_name
    self.post_fifo(Event(signal=signals.electrical_change))
    return status

  def float_tick(self, e):
    status = return_status.HANDLED
    return status

  def equalize_entry_signal(self, e):
    status = return_status.HANDLED
    self.control.reference = \
      self.battery_spec.equ_ref_volts
    self.start_sec = self.sec
    self.cause = self.state_name

    self.post_fifo(Event(signal=signals.electrical_change))

    return status

  def equalize_tick(self, e):
    status = return_status.HANDLED
    if(e.payload.sec - self.start_sec > 
      self.battery_spec.equ_timeout_sec):
      self.post_fifo(Event(signal=signals.To_Float))
    return status

class ElectricalInterface(LoggedBehavior):
  def __init__(self, name=None, live_trace=None, live_spy=None):

    super().__init__(
      name=name, 
      live_trace=live_trace,
      live_spy=live_spy,
    )

    self._driving_terminal_amps = None
    self._driving_terminal_volts = None
    self._control = None

    self.respond_to_control_changes = self.create(
      state="respond_to_control_changes"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.respond_to_control_changes_entry_signal). \
      catch(signal=signals.DRIVE_CURRENT,
        handler=self.respond_to_control_changes_drive_current). \
      catch(signal=signals.DRIVE_VOLTAGE,
       handler=self.respond_to_control_changes_drive_voltage). \
      catch(signal=signals.REQUEST_FOR_SAMPLERS,
        handler=self.respond_to_control_changes_request_for_samplers). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.respond_to_control_changes_exit_signal). \
      to_method()

    self.drive_current_state = self.create(
      state="drive_current_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.drive_current_state_entry_signal). \
      to_method()

    self.drive_voltage_state = self.create(
      state="drive_voltage_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.drive_voltage_state_entry_signal). \
      to_method()

    self.nest(self.respond_to_control_changes, parent=None). \
      nest(self.drive_current_state, parent=self.respond_to_control_changes). \
      nest(self.drive_voltage_state, parent=self.respond_to_control_changes)

  def start(self):
    self.start_at(self.respond_to_control_changes)
    return self

  def respond_to_control_changes_entry_signal(self, e):
    status = return_status.HANDLED

    # wrap our sample current method and send it out to anyone that needs it
    self.publish(Event(signal=signals.SET_CURRENT_SAMPLER,
      payload=Sampler(fn=partial(self.sample_current))))

    # wrap our sample voltage method and send it out to anyone that needs it
    self.publish(Event(signal=signals.SET_VOLTAGE_SAMPLER,
      payload=Sampler(fn=partial(self.sample_voltage))))

    self.subscribe(Event(signal=signals.DRIVE_CURRENT))
    self.subscribe(Event(signal=signals.DRIVE_VOLTAGE))
    return status

  def respond_to_control_changes_exit_signal(self, e):
    status = return_status.HANDLED
    self.cancel_events(Event(signal=signals.Pulse))
    return status

  def respond_to_control_changes_drive_current(self, e):
    status = return_status.HANDLED
    return status

  def respond_to_control_changes_drive_voltage(self, e):
    status = return_status.HANDLED
    return status

  def respond_to_control_changes_request_for_samplers(self, e):
    status = self.trans(self.respond_to_control_changes)
    return status

  def drive_current_state_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def drive_voltage_state_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def sample_current(self):
    return 10.0

  def sample_voltage(self):
    return 12.0

  def drive_current(self, amps, control):
    pass

  def drive_voltage(self, volts, control):
    pass


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

# current control system
ccs = CurrentControlSystem(
  reference=50.0,  # 50 amps
  kp=0.5,
  ki=0.03,
  kd=0.04,
  current_clamp_amps=battery_spec.bulk_ref_amps,
  voltage_clamp_volts=battery_spec.equ_ref_volts,
)

# voltage control system
vcs = VoltageControlSystem(
  reference=12.0, # 12 volts
  kp=0.4,
  ki=0.02,
  kd=0.005,
  current_clamp_amps=battery_spec.bulk_ref_amps,
  voltage_clamp_volts=battery_spec.equ_ref_volts,
)

# aggregated charger paramters
charger_params = ChargerParameters(
  c_control=ccs,
  v_control=vcs,
  battery_spec=battery_spec
)

if __name__ == '__main__':

  # the charger data and behavior
  three_stage_charger = Charger(
    name='charger',
    charger_params=charger_params,
    live_spy=True,
  ).start()

  electrics = ElectricalInterface(
    name="electrical_interface",
    live_trace=True
  ).start()

  time.sleep(10)
