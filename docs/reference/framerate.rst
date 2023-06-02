Framerates and timestamps
=========================

Introduction
------------

During an experiment you see the cursor moving on the screen, but what your screen actually displays
is a series of still images, or frames, which are updated quickly enough that we don't notice the individual frames.

Typically computer monitors do this at a rate of 60 frames per second (fps), although gaming monitors are available
that offer much higher refresh rates.

The experiment saves information about the cursor position each time a new frame is displayed.

How an experiment works
-----------------------

This loop happens every time the monitor refreshes:

   - store the timestamp and current cursor location
   - prepare next frame to display (draw objects such as the cursor, targets, etc)
   - wait until the screen is updated with the new frame

In the stored data, each timestamp is the time when the specified target was displayed on the screen,
and the cursor location at that time. The display on the screen doesn't change until the next timestamp.

Dropped frames
--------------

The sampling frequency of the experimental data is limited by the refresh rate of the monitor.

In addition, it could sometimes be the case that the code preparing the next frame to be displayed takes too long,
and the monitor refreshes the screen before the next frame is available.
This is known as a "dropped frame", and will be visible in the recorded data as a larger than usual delay
before the next timestamp.

If this happens, ensuring that nothing else is running on the computer when an experiment is running may help.
