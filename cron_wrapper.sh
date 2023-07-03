#!/bin/bash

cd /backup/batch_jobs/raspishake_report/
source .venv/bin/activate

make build_db

TD=$(mktemp -d)
TEMPSCRIPT=${TD}/cron.sh
echo "#!/bin/bash -x" > $TEMPSCRIPT
./src/usgs.py query >> $TEMPSCRIPT

chmod 755 $TEMPSCRIPT
$TEMPSCRIPT
