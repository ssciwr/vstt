Forwards Compatibility
======================

Adding new features
-------------------

It seems likely that new features will need to be added in the future, in particular:

* adding a new field in ``MotorTaskTrial``
* adding some corresponding task logic that uses this field

Each new feature should have a default value resulting in unchanged behaviour from before the feature was added.
This might require a boolean on/off flag in addition to another field with the actual parameter.
This is required to ensure forwards compatibility of existing experiments with new versions of the software.

Unknown or missing fields
-------------------------

When importing a trial:

* Unknown fields are ignored
* Missing fields are replaced with their default values

This is required to ensure forwards compatibility of experiments with new versions of the software,
as well as (limited) backwards compatibility of experiments with older versions of the software.

Forwards compatibility
----------------------

As a consequence of the two sections above,
once an experiment is created using one version of the software,
it is guaranteed to continue to behave in the same way with any later version of the software.

Backwards compatibility
-----------------------

If an experiment is created in a newer version of the software and then opened in an older version of the software,
the experiment will still run. However, if it contains non-default values for any fields that did not exist in
the older version of the software, the user-visible task will differ.
