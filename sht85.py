'''
	This script is executed at regular intervals (e.g. every 3 minutes). 
	It measures the humidity and temperature for a certain period of time (adjustable via command line argument) with a certain frequency (also adjustable via command line argument). 
	The communication is based on the I2C bus system (see Wikipedia and the SHT85 manual for details). 
	At the end of the measurement, the measurement data is saved (name of file=time of measurement)
	
	The script expects three command line argument:
	    - the username
	    - mps=measurements per second (either  '0.5mps', '1mps', '2mps', '4mps', or '10mps')
	    - duration of the measurement (in seconds)
'''
import smbus
import time
from datetime import datetime
import sys
import numpy as np
import os
import logging

DEVICE_BUS = 1
DEVICE_ADDR = 0x44 # address of SHT85 sensor (can be found in the manual)

REG_PERIODIC = {
	'0.5mps': 0x20, 
	'1mps': 0x21, 
	'2mps': 0x22, 
	'4mps': 0x23, 
	'10mps': 0x27
	}
PERIODIC_LSB = {
	'0.5mps': {'high': 0x32, 'medium': 0x24, 'low': 0x2f}, 
	'1mps': {'high': 0x30, 'medium': 0x26, 'low': 0x2d}, 
	'2mps': {'high': 0x36, 'medium': 0x20, 'low': 0x2b}, 
	'4mps': {'high': 0x34, 'medium': 0x22, 'low': 0x29}, 
	'10mps': {'high': 0x37, 'medium': 0x21, 'low': 0x2a}
	}
	
REG_BREAK_PERIODIC = 0x30
BREAK_PERIODIC_LSB = 0x93

REG_FETCH_DATA = 0xe0
FETCH_DATA_LSB = 0x00

REG_READ = 0x00

CRC_POLYNOMIAL = 0x131 #x^8 + x^5 + x^4 + 1 = 100110001

def saveData(temp_list, hum_list, username, mps_setting):
	if len(temp_list)!=len(hum_list):
		logging.error("There should be the same number of temperature and humidity data points.")
		return
	dat = np.zeros(shape=(len(temp_list),2))
	dat[:, 0] = temp_list
	dat[:, 1] = hum_list
	header = f'TIME={datetime.now()}\nMPS={mps_setting}\ntemperature [°C], humidity [%]'
	directory = f'/home/{username}/SHT85/'
	date = f'{datetime.now().date()}'
	dir_date = os.path.join(directory, date)
	if not os.path.exists(dir_date):
		os.makedirs(dir_date)
	np.savetxt(f'{dir_date}/{datetime.now()}.txt', X=dat, header=header)
	logging.info(f'saved: {dir_date}/{datetime.now()}.txt')
	
def checkCRC(data, nbrOfBytes, crc_provided):
	crc = 0xFF #calculated checksum
	# calculates 8-Bit checksum with given polynomial (see the SHT85 manual for details)
	for byteCtr in range(0, nbrOfBytes, 1):
		crc ^= (data[byteCtr])
		for bit in range(8, 0, -1):
			if(crc & 0x80):
				crc = (crc << 1) ^ CRC_POLYNOMIAL
			else:
				crc = (crc << 1)
	if crc != crc_provided:
		return False
	return True
	
def conv_RH(S_RH):
	# convert relative humidty to unit % (see the SHT85 manual for details)
	return 100*S_RH/(2**16-1)

def conv_T(S_T):
	# convert temperature to °C (see the SHT85 manual for details)
	return -45 + 175*S_T/(2**16-1)
	
def periodicMeasurement(bus, duration_sec, mps='1mps', repeatibility='high'):
	
	temp_list = list()
	hum_list = list()
	
	bus.write_i2c_block_data(DEVICE_ADDR, REG_PERIODIC[mps], [PERIODIC_LSB[mps][repeatibility]]) #start peridiodic measurement with specific mps and repeatibility settings
	time.sleep(0.01)
	t_start = time.time()
	t_stop = time.time()
	while(t_stop - t_start < duration_sec):
		bus.write_i2c_block_data(DEVICE_ADDR, REG_FETCH_DATA, [FETCH_DATA_LSB]) #fetch data from sensor 
		time.sleep(0.01)
		
		#Read data from SHT85. The SHT85 sends 6 bytes (see SHT85 manual for details):
		# - The first two encode the temperature
		# - the third is a checksum for the tmeperature bytes
		# - the fourth and fifth encode the humitidy 
		# - the sixth is a checksum for the humidity bytes 
		ret = bus.read_i2c_block_data(DEVICE_ADDR, REG_READ, 6)
		S_T = (ret[0] << 8) | ret[1]
		check1 = checkCRC(ret[0:2], 2, ret[2])
		S_RH = (ret[3] << 8) | ret[4]
		check2 = checkCRC(ret[3:5], 2, ret[5])
		
		#convert temperature and humidity to usefull units
		hum = conv_RH(S_RH) #in %
		temp = conv_T(S_T) #in C
		
		# Disregard Measurements in case the checksums do not match
		if not (check1 and check2):
			logging.error("Checksums do not match! Disregard measurement.")
		else:
			temp_list.append(temp)
			hum_list.append(hum)
			
		#wait for 1/mps seconds
		if mps!='0.5mps':
			time.sleep(1/float(mps[0]))
		else:
			time.sleep(2)
		t_stop = time.time()
		
	bus.write_i2c_block_data(DEVICE_ADDR, REG_BREAK_PERIODIC, [BREAK_PERIODIC_LSB]) #stop periodic measurement
	return hum_list, temp_list
			
if __name__ == '__main__':
	logging.basicConfig(format="%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s :  %(message)s", datefmt="%Y-%m-%d %H:%M", level=logging.INFO)
	if len(sys.argv) != 4:
		logging.error(f"Expected number of arguments is 3, not {len(sys.argv) - 1}") 
	else:
		username = sys.argv[1]
		mps_setting = sys.argv[2]
		meas_time_sec = int(sys.argv[3])
		bus = smbus.SMBus(DEVICE_BUS)
		hum_list, temp_list = periodicMeasurement(bus, duration_sec=meas_time_sec, mps=mps_setting)
		saveData(temp_list, hum_list, username, mps_setting)
	
