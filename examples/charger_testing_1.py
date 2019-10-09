# https://stackoverflow.com/questions/43397162/show-matplotlib-plots-in-ubuntu-windows-subsystem-for-linux
import sys
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve
from scipy.interpolate import interp1d
from functools import partial
blocks_per_volt = 10.0   # ten charge blocks make a volt
volts_per_block = 1.0/blocks_per_volt
cc_blocks       = 10.0   # bulk charging amps
volt_max        = 20.0   # volts
equ_abs         = 18.0   # equalization volts
cv_abs          = 16.0   # absorption volts
cv_float        = 12.0   # float volts
abs_exit_blocks = 2.1  # abs_exit_blocks

data_ocv_soc = np.genfromtxt(
  'ocv_soc.csv',
  delimiter=',',
  skip_header=1,
  names=['state_of_charge', 'open_circuit_voltage'],
  dtype="float, float",
)
x = data_ocv_soc['state_of_charge']
y = data_ocv_soc['open_circuit_voltage']
fn_soc_to_ocv = interp1d(x, y)


################################################################################
#                              Setup Graph Style                               #
################################################################################
colors = {
  'voltage_color' : 'tab:blue',
  'current_color' : 'tab:red',
  'state_color' : 'tab:orange',
}
fig, (ax1, ax2) = plt.subplots(2, sharey=True)
ax1.plot(data_ocv_soc['state_of_charge'], data_ocv_soc['open_circuit_voltage'], color=colors['current_color'])
ax1.set(title="Battery Profile", ylabel="open_circuit_voltage csv")
x_new = np.linspace(x[0], x[-1], 50)
y_new = fn_soc_to_ocv(x_new)
ax2.plot(x_new, y_new, color=colors['voltage_color'])
ax2.set(xlabel="state_of_charge", ylabel="fn_soc_to_ocv")

plt.savefig('./../doc/_static/battery_profile.svg')
plt.savefig('./../doc/_static/battery_profile.pdf')
plt.show()
sys.exit(0)
################################################################################
#                                 Get the Data                                 #
################################################################################
data = np.genfromtxt(
  'charger_testing.csv',
  delimiter=',',
  skip_header=1,
  names=['time', 'current', 'voltage', 'state'],
  dtype="float, float, float, |S10",  # this took 20 minutes to figure out
)
################################################################################
#                                 Current Plot                                 #
################################################################################
color = colors['current_color']
ax1.set_xlabel('time [Sec]')

max_current_height = max(data['current'])*1.10

ax1.set_ylim([0, max_current_height])
ax1.set_ylabel('current [Amps]')
ax1.plot(data['time'], data['current'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

# This will be used by both the state change and the voltage plots
max_voltage_height = max(data['voltage'])*1.05

################################################################################
#                              State Change Plot                               #
################################################################################
# Instatiate a second axes that shares the same x-axis
ax2 = ax1.twinx()
color = colors['state_color']
ax2.set_ylim([0, max_voltage_height])
# If the next state name is different than our current state name, this time is
# a state transition time
state_transition_times = [
  d[0] for i, d in enumerate(data) if \
   i+1 < len(data) and data[i][3] != data[i+1][3]
]
for transition_time in state_transition_times:
  ax2.plot([transition_time, transition_time], [0, max_voltage_height], color=color)
ax2.tick_params(axis='y', labelcolor=color)

################################################################################
#                                 Voltage Plot                                 #
################################################################################
# Instatiate a third axes that shares the same x-axis
ax3 = ax1.twinx()
color = colors['voltage_color']
ax3.set_ylabel('voltage [Volts]')
ax3.set_ylim([0, max_voltage_height])
ax3.plot(data['time'], data['voltage'], color=color)
ax3.tick_params(axis='y', labelcolor=color)

# Need to do this or the right y-label is slighly clipped
fig.tight_layout()
plt.show()
