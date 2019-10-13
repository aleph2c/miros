import numpy as np
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly

data_ocv_internal_resistance = np.genfromtxt(
  'ocv_internal_resistance.csv',
  delimiter=',',
  skip_header=1,
  names=['open_circuit_volts', 'resistance_ohms'],
  dtype="float, float",
)

coefs = poly.polyfit(
  data_ocv_internal_resistance['open_circuit_volts'],
  data_ocv_internal_resistance['resistance_ohms'],
  5,
)

fn_ocv_to_batt_r = poly.Polynomial(coefs)
colors = {
  'csv_color': 'tab:red',
  'function_color': 'tab:blue',
}

fig, (ax1, ax2) = plt.subplots(2, sharey=True)
ax1.plot(
  data_ocv_internal_resistance['open_circuit_volts'],
  data_ocv_internal_resistance['resistance_ohms'],
  color=colors['csv_color'],
)

ax1.set(
  title="Battery: Internal Resistance Profile",
  ylabel="battery_resistance_ohms"
)

x_new = np.linspace(
  data_ocv_internal_resistance['open_circuit_volts'][0],
  data_ocv_internal_resistance['open_circuit_volts'][-1],
  50
)
y_new = fn_ocv_to_batt_r(x_new)
ax2.plot(x_new, y_new, color=colors['function_color'])
ax2.set(xlabel="state_of_charge", ylabel="fn_ocv_to_batt_r")

for i, x in enumerate(x_new):
  print("i osv:{}, ohms:{}".format(x_new[i], y_new[i]))

plt.savefig('../doc/_static/battery_resistance_profile.svg')
plt.savefig('../doc/_static/battery_resistance_profile.pdf')
plt.show()

