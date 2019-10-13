# soc_ocv.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

data_ocv_soc = np.genfromtxt(
  'soc_ocv.csv',
  delimiter=',',
  skip_header=1,
  names=['state_of_charge', 'open_circuit_voltage'],
  dtype="float, float",
)

# build the function which will approximate the data set
fn_soc_to_ocv = interp1d(
  data_ocv_soc['state_of_charge'], 
  data_ocv_soc['open_circuit_voltage'] 
)

colors = {
  'csv_color': 'tab:red',
  'function_color': 'tab:blue',
}

# plot the data and the approximation function
fig, (ax1, ax2) = plt.subplots(2, sharey=True)
ax1.plot(
  data_ocv_soc['state_of_charge'], 
  data_ocv_soc['open_circuit_voltage'],
  color=colors['csv_color']
)
ax1.set(title="Battery: Open Circuit Voltage Profile", ylabel="open_circuit_voltage csv")
x_new = np.linspace(
  data_ocv_soc['state_of_charge'][0], 
  data_ocv_soc['state_of_charge'],
  50
)
y_new = fn_soc_to_ocv(x_new)
ax2.plot(x_new, y_new, color=colors['function_color'])
ax2.set(xlabel="state_of_charge", ylabel="fn_soc_to_ocv")

plt.savefig('battery_profile.svg')
plt.savefig('battery_profile.pdf')
plt.show()
sys.exit(0)
