import cProfile

from psychopy import core
from vstt.experiment import Experiment
from vstt.task import MotorTask

experiment = Experiment()
experiment.trial_list[0]["weight"] = 1
experiment.trial_list[0]["inter_target_duration"] = 0
experiment.trial_list[0]["post_block_display_results"] = False
task = MotorTask(experiment)
with cProfile.Profile() as pr:
    task.run()
pr.dump_stats("profile_task.prof")
core.quit()
