#!/bin/bash

cd /backup/batch_jobs/raspishake_report/
source .venv/bin/activate

echo "Worldwide quakes > 4.5:"
echo
./src/usgs.py pretty_table

echo
echo "Nearby quakes > 1.0:"
echo
./src/usgs.py pretty_table --feed LAST_DAY_OVER_1_POINT_0 --radius 1000

# Turning this off while Raspishake servers are being rebuilt
# echo
# echo

# TD=$(mktemp -d)
# TEMPSCRIPT=${TD}/cron.sh
# echo "#!/bin/bash -x" > $TEMPSCRIPT
# ./src/usgs.py script_report >> $TEMPSCRIPT

# chmod 755 $TEMPSCRIPT
# $TEMPSCRIPT
