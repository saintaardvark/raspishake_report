#!/bin/bash

cd /backup/batch_jobs/raspishake_report/
source .venv/bin/activate

./src/usgs.py pretty_table

# Turning this off while Raspishake servers are being rebuilt
# echo
# echo

# TD=$(mktemp -d)
# TEMPSCRIPT=${TD}/cron.sh
# echo "#!/bin/bash -x" > $TEMPSCRIPT
# ./src/usgs.py script_report >> $TEMPSCRIPT

# chmod 755 $TEMPSCRIPT
# $TEMPSCRIPT
