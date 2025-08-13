'''
	This script is called by upload.sh. The measurement data of the previous day is read in (multiple files) and combined into a single file. Structure of the output file is:
	    #merged data from {date}
	    #time, temperature [°C], humidity [%] 
	    ...,...,...
	    
	The script expects one command line argument:
	    - the username
'''
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging

def load_data(directory):
	files = os.listdir(directory)
	times = list()
	data = list()
	mps = list()
	for f in files:
		d_ = np.loadtxt(fname=f"{directory}/{f}", comments="#")
		with open(f"{directory}/{f}") as input_file:
			t_str = next(input_file).replace("\n","")
			mps_str = next(input_file).replace("\n","")
			t_ = datetime.strptime(t_str.split("=")[-1], "%Y-%m-%d %H:%M:%S.%f")
			mps_ = mps_str.split("=")[-1]
		data.append(d_)
		times.append(t_)	
		mps.append(mps_)
		
	# Sorting data by time
	t_d_zip = zip(times, data, mps)
	t_d_zip = sorted(t_d_zip, key= lambda x: x[0])
	times = [t_d[0] for t_d in t_d_zip]
	data = [t_d[1] for t_d in t_d_zip]
	mps = [t_d[2] for t_d in t_d_zip]
	
	return times, data, mps

def merge_data(times, data, mps):
	time_delta = {
		'0.5mps': timedelta(seconds=2.0), 
		'1mps': timedelta(seconds=1.0), 
		'2mps': timedelta(seconds=0.5), 
		'4mps': timedelta(seconds=0.25), 
		'10mps': timedelta(seconds=0.1)
	}
	len_dat = 0
	for d in data: 
		len_dat += len(d)
	dat_merged = np.zeros(shape=(len_dat,3))#time, temperature, humidity
	ind = 0
	for i in range(len(times)):
		t_ = times[i]
		dat_ = data[i]
		mps_ = mps[i]
		time_delta_ = time_delta[mps_]
		for j in range(len(dat_)):
			dat_merged[ind, 0] = (t_ + j*time_delta_).timestamp()
			dat_merged[ind, 1] = dat_[j, 0]
			dat_merged[ind, 2] = dat_[j, 1]
			ind += 1
	return dat_merged
	
def save_data(directory, date_yesterday, data_merged):
	header = f"merged data from {date_yesterday}\ntime, temperature [°C], humidity [%]"
	np.savetxt(f'{directory}/data_merged.txt', X=data_merged, header=header)
	
if __name__=="__main__":
	logging.basicConfig(format="%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s :  (message)s", datefmt="%Y-%m-%d %H:%m")
	if len(sys.argv) != 3:
		#Expected command line argument: username date_yesterday
		logging.error(f"Expected number of arguments is 2, not {len(sys.argv) - 1}")
	else:
		username = sys.argv[1]
		yesterday = sys.argv[2]#(datetime.now() - timedelta(days=1)).date()
		directory = f"/home/{username}/SHT85/{yesterday}"
		times, data, mps = load_data(directory) #mps = measurements per second
		merged = merge_data(times, data, mps)
		save_data(directory, yesterday, merged)
		
