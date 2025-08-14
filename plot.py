'''
	This script is called by upload.sh after the measurement data of the previous day has been collected in a combined file. The measurement data is read in and a plot of temperature and humidity is created.
	The script expects two command line arguments:
	    - the username
	    - the title of the plot 
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import sys
import logging

def plot(times, dat_plt, title, directory):
	mask_invalid_measurements = (dat_plt[:,1] < 0) & (dat_plt[:,0] < 0)
	fig = plt.figure(figsize=(8,5))
	ax = fig.add_subplot()
	fig.suptitle(title)
	ax.plot(times[~mask_invalid_measurements], dat_plt[:,1][~mask_invalid_measurements], color="cornflowerblue")
	ax_twin = ax.twinx()
	ax_twin.plot(times[~mask_invalid_measurements], dat_plt[:,0][~mask_invalid_measurements], color="firebrick")

	ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	ax.set_xlabel("Time")
	ax.grid()
	ax.xaxis.set_tick_params(rotation=45)
	ax.set_ylabel("Humidity [%]", color="cornflowerblue")
	ax.yaxis.set_tick_params(colors="cornflowerblue")
	ax_twin.set_ylabel("Temperature [°C]", color="firebrick")
	ax_twin.yaxis.set_tick_params(colors="firebrick")
	fig.tight_layout()
	plt.savefig(f"{directory}/plot.pdf")
	
if __name__=="__main__":
	logging.basicConfig(format="%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s :  %(message)s", datefmt="%Y-%m-%d %H:%M", level=logging.INFO)
	if len(sys.argv) != 4:
		#Expected command line arguments: username title date_yesterday
		logging.error(f"Expected number of arguments is 3, not {len(sys.argv) - 1}")
	else:
		username = sys.argv[1]
		title = sys.argv[2] #title of the plot
		yesterday = sys.argv[3] #(datetime.now() - timedelta(days=1)).date()
		directory = f"/home/{username}/SHT85/{yesterday}"
		try:
			data = np.loadtxt(fname=f"{directory}/data_merged.txt", comments="#")
		except OSError as e:
			logging.error(f"Unable to open {directory}/data_merged.txt. Plot can't be created.")
			sys.exit(1)
		times = np.array([datetime.fromtimestamp(t_) for t_ in data[:,0]])
		plot(times, data[:,1:], f"{title}, date: {yesterday}", directory)
