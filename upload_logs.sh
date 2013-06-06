#!/bin/sh
TIMESTAMP=`date +%Y%m%d.%H%M`

cd /home/biin/museotouch/tools/upload_logs/

LOG="logs/send_logs-$TIMESTAMP.log"

python send_logs.py > ${LOG}

