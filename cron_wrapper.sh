#!/bin/bash

cd /backup/batch_jobs/raspishake_report/
source .venv/bin/activate

TD=$(mktemp -d)
TEMPSCRIPT=${TD}/cron.sh
echo "#!/bin/bash -x" > $TEMPSCRIPT
./src/init/usgs.py >> $TEMPSCRIPT

chmod 755 $TEMPSCRIPT
$TEMPSCRIPT
