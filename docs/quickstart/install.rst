Installation
============

Windows with standalone Psychopy (recommended)
----------------------------------------------

* Install `StandalonePsychoPy <https://github.com/psychopy/psychopy/releases/download/2022.2.4/StandalonePsychoPy-2022.2.4-win64.exe>`_
* Download `UpdatePrototype.bat <https://github.com/ssciwr/vstt/releases/download/latest/UpdatePrototype.bat>`_ and double-click on it
* Download `RunPrototype.bat <https://github.com/ssciwr/vstt/releases/download/latest/RunPrototype.bat>`_ and double-click on it

.. note::
   * Your browser might warn you about downloading batch files
      * This is normal for a .bat file
      * Click keep -> show more -> keep anyway
   * The first time you run it you might get a "Windows protected your PC" message
      * This is also normal for a .bat file
      * Click more info -> run anyway
   * What does `UpdatePrototype.bat` do?
      * This installs the latest version of the prototype into your Psychopy Python environment using pip
      * It runs this command: ``"C:\Program Files\PsychoPy\python.exe" -m pip install https://github.com/ssciwr/vstt/releases/download/latest/vstt-latest-py3-none-any.whl``
   * What does `RunPrototype.bat` do?
      * This runs the prototype using your Psychopy Python environment
      * It runs this command: ``"C:\Program Files\PsychoPy\python.exe" -m vstt``
   * If in doubt you can always open the .bat file in notepad to see what commands it will run
   * If you have installed Psychopy in a non-default location you will need to update the paths
     in these batch files to point to the psychopy-installed python.exe.

Alternative pip install
-----------------------

If you already have a Python environment and git you can install using pip:

``pip install git+https://github.com/ssciwr/vstt``

.. note::
   On linux you will also need to give your Python executable permission
   to set its own priority: ``sudo setcap cap_sys_nice=eip /path/to/python/binary``.

.. note::
   This method also installs the psychopy library with pip, which may need additional
   system libraries and configuration steps to work properly,
   which is probably why they provide standalone installers for
   Psychopy on Windows and Mac which bundle all the requirements.
