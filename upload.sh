#!/bin/bash

#This script runs at the end of every day and is responsible for managing the upload process of yesterdays data, i.e.
#    - Merging data into a single file and create an overview plot of yesterdays temperature and humidity
#    - Uploading plot and data to cloud
#    - Remove data from more than seven days ago


dateYesterday=$(date -d "yesterday" +"%Y-%m-%d")
piID=$(whoami)
title="office"
directory="/home/$piID/SHT85/$dateYesterday"
if [ ! -d "$directory" ]; then
	echo "Directory $directory does not exist."
else
	# Merging files of the previous day to a single file
	python /home/$piID/SHT85/mergeData.py $piID $dateYesterday
	
	# Creating plot
	python /home/$piID/SHT85/plot.py $piID $title $dateYesterday
	
	#Uploading the data/plot to the ownCloud
	curl -d loginProfile=6 -d accessType=termsOnly https://hotspot.vodafone.de/api/v4/login
	rclone mkdir owncloud:RaspiLogs/$piID/$dateYesterday
	rclone copyto $directory/data_merged.txt owncloud:RaspiLogs/$piID/$dateYesterday/data.txt
	rclone copyto $directory/plot.pdf owncloud:RaspiLogs/$piID/$dateYesterday/plot.pdf
	echo "Upload done."
fi

# Delete outdated data files. Only the last seven days are stored on the Raspberry Pi.
dateRemove=$(date --date="7 day ago" +"%Y-%m-%d")
cd /home/$piID/SHT85
for f in *; do #loop through all files
    if [ -d "$f" ]; then #check if f is a directory
    	if [[ "$f" == [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] ]]; then #check if f is of the from yyyy-mm-dd
     		if [[ "$dateRemove" > "$f" ]]; then
				rm -r $f
			fi
    	fi        
    fi
done
