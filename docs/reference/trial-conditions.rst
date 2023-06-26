Trial Conditions
================

There are many conditions that define the behaviour of a set of trials.
All time values are in seconds, and all distance values are fractions of
the screen height (i.e. a line of length 1.0 in these units would extend from the bottom to the top of the screen).

* Repetitions
   * The number of times the trial should be repeated
   * The trial will be repeated this many times (unless the maximum time is exceeded)
   * Default: ``1``
* Maximum time, 0=unlimited (secs)
   * The maximum time allowed to complete all repeats of these trial conditions
   * If zero, there is no time limit
   * If a trial is in progress when time runs out it is allowed to complete
   * Default: ``0``
* Number of targets
   * The number of outer targets to display
   * Default: ``8``
* Target order
   * The order in which targets should be activated
   * Can be ``clockwise``, ``anti-clockwise``, ``random``, or ``fixed``
   * If ``fixed``, the order is determined by the supplied "Target indices" (see next item)
   * Default: ``clockwise``
* Target indices
   * An ordered list of target ids to display, separated by spaces
   * Target ids go clockwise starting from 0 at the top of the circle
   * This is only used if ``fixed`` is chosen for "Target order"
   * Default: ``0 1 2 3 4 5 6 7``
* Add a central target
   * Enable to show a central target between each outer target
   * Default: ``enabled``
* Hide target when reached
   * Enable to hide a target once the cursor has reached it
   * Default: ``enabled``
* Display target labels
   * Enable to show a label inside each target
   * The labels are taken from "Target labels" (see below)
   * Default: ``disabled``
* Target labels
   * The label to display in each target, separated by spaces
   * Default: ``0 1 2 3 4 5 6 7``
* Fixed target display intervals
   * Enable to display a new target at fixed intervals
   * The interval is given by "Target display duration" below
   * The interval is not affected by the cursor reaching the target or not
   * If enabled, "Central target display duration" and "Delay between targets" are ignored
   * Default: ``disabled``
* Target display duration (secs)
   * How long each outer target should be displayed for
   * Default: ``5.0``
* Central target display duration (secs)
   * How long each central target should be displayed for
   * Default: ``5.0``
* Delay before target display (secs)
   * The delay before each outer target is displayed
   * Default: ``0.0``
* Delay before central target display (secs)
   * The delay before each central target is displayed
   * Default: ``0.0``
* Distance to targets (screen height fraction)
   * The distance from the centre of the screen to the outer targets
   * Default: ``0.4``
* Target size (screen height fraction)
   * Diameter of outer targets
   * Default: ``0.04``
* Central target size (screen height fraction)
   * Diameter of central targets
   * Default: ``0.02``
* Show inactive targets
   * Enable to make inactive targets visible (but greyed out)
   * Default: ``enabled``
* Ignore cursor hitting incorrect target
   * Enable to ignore when a cursor reaches an incorrect/inactive target
   * If disabled, when the cursor reaches any target the task will proceed to the next target
   * Default: ``enabled``
* Play a sound on target display
   * Enable to play an audible sound when a target is displayed
   * Default: ``enabled``
* Control the cursor using a joystick
   * Enable to use a joystick to control the cursor
   * If disabled, the mouse will be used instead
   * Default: ``disabled``
* Maximum joystick speed (screen height fraction per frame)
   * The maximum distance the cursor can move in a single frame
   * Multiply by the monitor refresh rate (fps) to get the speed in screen height fraction per second
   * The refresh rate is often 60fps, but some gaming monitors can have much higher refresh rates.
   * Default: ``0.02``
* Show cursor
   * Enable to display a cursor at the current cursor location
   * Default: ``enabled``
* Cursor size (screen height fraction)
   * The size of the cursor
   * Default: ``0.02``
* Show cursor path
   * Enable to display the path the cursor took
   * Default: ``enabled``
* Automatically move cursor to center
   * Enable to automatically move the cursor to the center after reaching an outer target
   * Default: ``disabled``
* Freeze cursor until target is displayed
   * Enable to freeze the cursor until a target is displayed
   * Default: ``disabled``
* Cursor rotation (degrees)
   * Rotate the cursor direction anticlockwise by this number of degrees
   * Default: ``0.0``
* Delay between trials (secs)
   * How long to wait after each trial
   * Default: ``0.0``
* Display results after each trial
   * Enable to display results for the trial after each trial
   * Default: ``disabled``
* Delay after last trial (secs)
   * How long to wait after the last trial with these trial conditions
   * Default: ``10.0``
* Display combined results after last trial
   * Enable to display combined results for these trial conditions after the last trial
   * Default: ``enabled``
* Display a countdown during delays
   * Enable to display a countdown in seconds while waiting between trials
   * Default: ``enabled``
* Skip delay by pressing enter key
   * Enable to allow the user to skip a delay between trials by pressing the enter key
   * Default: ``enabled``
