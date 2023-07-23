# raspishake_report

Raspberry Shake Reports!

Alan Sheehan's work at https://github.com/sheeny72/RPiSandB is the
basis for this; I've added some things and tidied up the code a bit,
but this is all based on Alan's work and would not exist without his
generosity.  Thank you, Alan!

## How it works

- `src/usgs.py` will query the USGS feed
  - `usgs.py query` will fetch the feed, then generate shell commands to generate reports

  - `usgs.py build_db` will fetch the feed, then transform the geojson
    for local use by datasette & save it
    & save it

	- it's now ready for `geojson-to-sqlite --alter my.db features
      2.5_day.geojson`

- `src/report.py` actually generates the reports

- `report.ini` contains a few config items for these scripts...too few

- `cron_wrapper.sh` attempts to tie it all together

## Overall flow

This is what's in cron_wrapper.sh:

- `make build_db` should generate `local.db`.  Datasette can now run.

- `usgs.py query` should fetch the USGS feed, then spit out shell
  commands to generate reports.

- That output is captured in a temporary shell script & then run.

- This should now create reports in the reports dir.  Datasette's
  `report_url` column should now work.


<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
