#!/bin/sh

at -f myscript.sh now +1 min < my.daily

poweroff

# echo "/usr/bin/poweroff" | at 16:34

# at now <<_EOF_
# "firefox"
# _EOF_

