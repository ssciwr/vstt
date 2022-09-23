import cProfile

from motor_task_prototype.display import default_display_options
from motor_task_prototype.experiment import new_experiment_from_dicts
from motor_task_prototype.meta import default_metadata
from motor_task_prototype.task import MotorTask
from motor_task_prototype.trial import default_trial
from psychopy import core


trial = default_trial()
trial["weight"] = 1
trial["inter_target_duration"] = 0
experiment = new_experiment_from_dicts(
    [trial], default_display_options(), default_metadata()
)
motor_task = MotorTask(experiment)
with cProfile.Profile() as pr:
    results = motor_task.run()
pr.dump_stats("profile_task.prof")
core.quit()
