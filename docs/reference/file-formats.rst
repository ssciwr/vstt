File formats
============

Experiments can be imported and exported in different formats: psydat, Excel, and json.
Psydat is the default format used by VSTT,
which can also be opened from Python scripts or Jupyter notebooks.
The Excel and json formats are provided to allow experiments
and results to be shared, analysed and modified
without requiring the VSTT software to do so.

.. list-table:: File format comparison
   :widths: 25 25 25 25
   :header-rows: 1

   * -
     - psydat
     - Excel
     - json
   * - Export experiment
     - Yes
     - Yes
     - Yes
   * - Import experiment
     - Yes
     - Yes
     - Yes
   * - Export results
     - Yes
     - Yes
     - No
   * - Import results
     - Yes
     - No
     - No

psydat
------

This is the default file format, which includes the experiment results.
These files can be opened in the VSTT GUI or in Python
(see the example notebook for more information).

Excel
-----

Experiments can also be exported as Excel spreadsheets.
The first 3 pages in the spreadsheet define the experiment:

* metadata
* display_options
* trial_list

These values can be edited in Excel and then the modified experiment can
be opened in the VSTT GUI (File -> Open, choose Excel as filetype).
Note that results are not imported from an Excel file.

The excel sheet also contains a statistics page with calculated statistics for each trial.
Then there is a sheet of data for each trial in the experiment with the following columns:

* timestamps
   * start at 0 for each trial, increase throughout the trial
* mouse_positions_x
   * x coordinate of mouse at this timestamp
* mouse_positions_y
   * y coordinate of mouse at this timestamp
* i_target
   * ``-99`` if no target is visible
   * ``-1`` if central target is visible
   * otherwise index (e.g. ``0``, ``1``, etc) of current displayed target
* target_x
   * x coordinate of currently visible target
   * ``-99`` if no target is visible
* target_y
   * y coordinate of currently visible target
   * ``-99`` if no target is visible

There is also the option to export a separate page of data for each target,
so a single trial with 8 targets would result in 8 separate pages of experiment data.
In this case for each target the timestamps begin at a negative value,
and reach zero when the target is displayed.

json
----

Experiments can also be exported as a json text file.
This is a convenient format for sharing experimental setups,
as it can be easily read and modified in a text editor.
These files can also be opened in the VSTT GUI
(File -> Open, choose JSON as filetype).
The json file contains all the information required to define the experiment:

* metadata
* display_options
* trial_list

This format does not include any statistics or experimental results.
