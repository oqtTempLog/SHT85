#!/bin/bash
'
In case you need to manually upload data of a specific date you can execute this script. The working principle is the same as in upload.sh.
You need to provide two command line arguments:
	1: the date of the data you want to upload, in the format year-month-day
	2: the title of the plot that is generated
'

dateUpload=$1
piID=$(whoami)
title=$2
directory="/home/$piID/SHT85/$dateUpload"
if [ ! -d "$directory" ]; then
	echo "Directory $directory does not exist."
else
	python /home/$piID/SHT85/mergeData.py $piID $dateUpload

	python /home/$piID/SHT85/plot.py $piID $title $dateUpload
	
	rclone mkdir owncloud:RaspiLogs/$piID/$dateUpload
	rclone copyto $directory/data_merged.txt owncloud:RaspiLogs/$piID/$dateUpload/data.txt
	rclone copyto $directory/plot.pdf owncloud:RaspiLogs/$piID/$dateUpload/plot.pdf
	echo "Upload done."
fi
