Creating a new experiment
=========================

To create a new experiment, go to File -> New,
or press ``Ctrl+N``,
or click on the white new document toolbar button.

.. figure:: images/gui.png
   :alt: Graphical User Interface

   The main graphical user interface


Metadata
--------

In the Metadata section you can edit the metadata for the experiment,
as well as the text that should be displayed before the experiment begins.
To see a preview of what the splash screen will look like, click on "Preview Splash Screen".

.. figure:: images/meta.png
   :alt: Metadata

   Metadata: Information about the experiment and text to display before it starts.


Display Options
---------------

You can choose which results and statistics to display in the Display Options section.

.. figure:: images/display-options.png
   :alt: Display Options

   Display Options: select which results and statistics to display.


Trial Conditions
----------------

The conditions used for the trials are listed here.
Conditions can be added, re-ordered, edited and removed using the buttons below the list of trials.

.. figure:: images/trial-conditions.png
   :alt: Trial Conditions

   The list of conditions used in the trial.

To edit a trial, either click "Edit" or double click on the trial.
This will then open a dialog box where the trial parameters can be adjusted.
When you are finished, click "OK".

.. figure:: images/trial-screen.png
   :alt: trial settings dialog

   Dialog to edit the settings for a trial.

Notes on trial settings:

* ``Target indices``
   * if ``Target order`` is ``fixed`` then this lists the targets in the order to be displayed
   * targets are numbered clockwise starting from 0 at the top of the circle
   * note: if ``Target order`` is not ``fixed`` these indices are ignored
* ``Fixed target display intervals``
   * if enabled
      * the next (outer) target is displayed every ``Target display duration`` seconds
      * this happens regardless of what the user does
      * the ``Delay between targets`` setting is ignored in this case
   * if disabled
      * all targets are displayed until either the user reaches them or ``Target display duration`` seconds elapse
      * then there is a pause of ``Delay between targets`` seconds before each (outer) target is displayed
