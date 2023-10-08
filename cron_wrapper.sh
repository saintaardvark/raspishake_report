#!/bin/bash

cd /backup/batch_jobs/raspishake_report/
source .venv/bin/activate

./src/usgs.py pretty_table
echo
echo

make build_db

TD=$(mktemp -d)
TEMPSCRIPT=${TD}/cron.sh
echo "#!/bin/bash -x" > $TEMPSCRIPT
./src/usgs.py script_query >> $TEMPSCRIPT

chmod 755 $TEMPSCRIPT
$TEMPSCRIPT
