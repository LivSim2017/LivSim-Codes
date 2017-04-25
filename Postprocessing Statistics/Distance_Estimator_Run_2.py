import numpy as nump
import time
import csv
import scipy as scip
import datetime
import operator
import sys
import queue
from copy import deepcopy
import pandas as pd
from matplotlib.dates import strpdate2num

def estimate_transport(transplants):
	"""
	This function computes transport statistics for organs traveling between DSAs
	@Input:
		@transplants: data frame containing number of organs being transported 
		from DSA i to DSA j across 5 years 5 replications
	@Output:
		@distances: average distance traveled by an organ
		@times: average time traveled by an organ
		@drives: percentage of organ transported by ground vehicle
		@helicopters: percentage of organ transported by helicopters
		@airplanes: percentage of organ transported by airplanes
	"""

	#Settings
	nreps = 5
	nump.random.seed(7777)
	ndsa = 58

	#load distance-time-mode data
	data = nump.loadtxt("C:/Users/kbui1993/Documents/LivSim Codes/Postprocessing Statistics/distancetimes.txt")

	#Setup data
	dis_data = [[[] for i in range(0,ndsa)] for j in range(0,ndsa)]
	time_data = [[[] for i in range(0,ndsa)] for j in range(0,ndsa)]
	mode_data = [[[] for i in range(0,ndsa)] for j in range(0,ndsa)]

	for i in range(0,nump.shape(data)[0]):
		opo = int(data[i,0])
		txdsa =  int(data[i,1])
		dis_data[opo][txdsa].append(data[i,2])
		time_data[opo][txdsa].append(data[i,3])
		mode_data[opo][txdsa].append(data[i,4])

	#Prepare Output
	distances = []
	times = []
	drives =[]
	helicopters = []
	airplanes = []

	#preinitialize list to store number of transplant at the end of 5 years per replication
	transplant_data_list = []
	transplant_subset0 = transplants.iloc[232:289+1,:]
	transplant_data_list.append(transplant_subset0)


	#get total number of transplants at the end of 5 years per replication
	for n in range(1,nreps):
		transplant_subset1 = transplants.iloc[(232+(58*5)*n):(289+(58*5)*n)+1,:]
		total_transplant_subset = nump.subtract(transplant_subset1, transplant_subset0)
		transplant_data_list.append(total_transplant_subset)
		transplant_subset0 = transplant_subset1

	for n in range(0,nreps):

		#get tx data of replication n
		tx_subset = transplant_data_list[n]

		#get total number of transplants across 5 years in one replication
		tx_total = nump.sum(tx_subset.sum())

		#pre-initialize variables to store relevant values
		moment1_distance = 0
		moment1_time = 0

		count_drive = 0
		count_helicopter = 0
		count_airplane = 0

		#iterate through each entry of DSA i to DSA j to estimate distance traveled and hours traveled for
		#an organ
		for i in range(0,ndsa):
			for j in range(0,ndsa):
				#skip if there is negative number of transplants (which isn't supposed to happen)
				if int(tx_subset.iloc[i,j]) <= 0:
					pass
				else:
					for k in range(0,int(tx_subset.iloc[i,j])):
						#Select random donor_hospital and tx_ctr combination
						if len(dis_data[i][j]) > 0:
							randindex = nump.random.choice(list(range(0,len(dis_data[i][j]))))

							#Update Stats
							moment1_distance = moment1_distance + dis_data[i][j][randindex]
							moment1_time = moment1_time + time_data[i][j][randindex]

							count_drive  =count_drive + int(mode_data[i][j][randindex]==0)
							count_helicopter  =count_helicopter + int(mode_data[i][j][randindex]==1)
							count_airplane  =count_airplane + int(mode_data[i][j][randindex]==2)

		#store average statistics
		distances.append(moment1_distance/tx_total)
		times.append(moment1_time/tx_total)
		drives.append(count_drive/tx_total)
		helicopters.append(count_helicopter/tx_total)
		airplanes.append(count_airplane/tx_total)

	#convert to data frames
	distances = pd.DataFrame(distances)
	distances.columns = ['Average Distance Traveled']
	times = pd.DataFrame(times)
	times.columns = ['Average Time Traveled']
	drives = pd.DataFrame(drives)
	drives.columns = ['Percentage of Organ Traveled by Car']
	helicopters = pd.DataFrame(helicopters)
	helicopters.columns = ['Percentage of Organ Traveled by Helicopter']
	airplanes = pd.DataFrame(airplanes)
	airplanes.columns = ['Percentage of Organ Traveled by Airplane']

	#return results
	return distances, times, drives, helicopters, airplanes


def output_distance_data(directory):
	"""
	This function estimates the transport statistics based on RawOutput_DSAs2.csv. 
	It writes the results into the directory
	@Input:
		@directory: location of RawOutput_DSAs2.csv. Also location where
		output files will be written to.
	"""

	#read in transplants data
	transplants = pd.read_csv(directory + "RawOutput_DSAs2.csv")
	transplants = transplants.iloc[58:, 1:]

	#compute travel statistics
	travel_stat = estimate_transport(transplants)

	#write results to directory
	travel_stat[0].to_csv(directory+ "AvgDistance.csv", sep = ',', encoding = 'utf-8', index = False)
	travel_stat[1].to_csv(directory+ "AvgTime.csv", sep = ',', encoding = 'utf-8', index = False)
	travel_stat[2].to_csv(directory+ "CarPercentage.csv", sep = ',', encoding = 'utf-8', index = False)
	travel_stat[3].to_csv(directory+"HelicopterPercentage.csv", sep = ',', encoding = 'utf-8', index = False)
	travel_stat[4].to_csv(directory+"AirplanePercentage.csv", sep = ',', encoding = 'utf-8', index = False)











