#!/bin/sh

if eval "ping -c 1 www.google.com"; then
	echo "We've got internet : sending logs to backoffice"
	cd /home/biin/museotouch/
	./upload_logs.sh
else
	echo "No internet available"
fi

# here I am setting a time stamp variable which I like to use for logging
#TIMESTAMP=`date +%Y%m%d.%H%M`
 
# here I am setting up the backup directory as a variable
DEST_DIR="/backup/my-backup"
 
# here I am setting up the directory in which I want to backup, again another variable
SRC_DIR="/home/<user-name-here>/Documents"
 
# let's create a variable for the backup file name file
FNAME="log"
 
# let's create a variable for the log file, let's also name the log file with the filename and timestamp it
#LOG="/home/biin/museotouch/logs/$TIMESTAMP.log"

cd /home/biin/museotouch/

while true
do
	# here I am setting a time stamp variable which I like to use for logging
	TIMESTAMP=`date +%Y%m%d.%H%M`

	# let's create a variable for the log file, let's also name the log file with the filename and timestamp it
	LOG="/home/biin/museotouch/logs/$TIMESTAMP.log"

	python app/main.py > ${LOG}
	#sleep 5
done
# if [ "$(pidof shutdown)" ] 
# then
#   echo "shutdown already running"
# else
#   sudo shutdown -h 16:32
# fi

