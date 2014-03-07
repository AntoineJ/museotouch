#!/bin/sh
# Close the museotouch daemon 
ps aux | grep -ie app.sh | awk '{print $2}' | xargs kill -9