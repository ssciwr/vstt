import cProfile

from motor_task_prototype.experiment import MotorTaskExperiment
from motor_task_prototype.task import MotorTask
from psychopy import core

experiment = MotorTaskExperiment()
experiment.trial_list[0]["weight"] = 1
experiment.trial_list[0]["inter_target_duration"] = 0
experiment.trial_list[0]["post_block_display_results"] = False
task = MotorTask(experiment)
with cProfile.Profile() as pr:
    task.run()
pr.dump_stats("profile_task.prof")
core.quit()
